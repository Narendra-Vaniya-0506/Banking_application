from flask import Flask, render_template, redirect, url_for, flash, request, abort, send_file, session
from flask_pymongo import PyMongo
import bcrypt
from datetime import datetime
from forms import LoginForm, AddUserForm, CreditDebitForm, ApproveRequestForm, TransferForm, RequestForm
from bson import ObjectId
from utils import transfer_money, credit_user, debit_user, submit_request, approve_request, reject_request, mask_aadhar
from models import User, Transaction, Request, Admin
from db import mongo
from pdf import generate_passbook_pdf

app = Flask(__name__)
app.secret_key = "your_secret_key"

# MongoDB setup
app.config["MONGO_URI"] = "mongodb://localhost:27017/codeyatra_bank"
mongo.init_app(app)

@app.route('/')
def home():
    return render_template("home.html")  # Home page

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    if request.method == 'POST':
        if 'username' in request.form:
            # Admin login
            username = request.form['username']
            password = request.form['password']
            admin = Admin.find_by_username(username)
            if admin and admin.check_password(password):
                session['user_role'] = 'admin'
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid admin credentials')
                return redirect(url_for('login'))
        elif 'account_no' in request.form and 'mpin' in request.form:
            # User login
            account_no = request.form['account_no']
            mpin = request.form['mpin']
            user = User.find_by_account_no(account_no)
            if user and user.check_mpin(mpin):
                if user.first_login:
                    flash('Welcome! This is your first login.')
                    user.set_first_login(False)
                session['account_no'] = account_no
                session['user_role'] = 'user'
                return redirect(url_for('user_dashboard'))
            else:
                flash('Invalid user credentials')
                return redirect(url_for('login'))
    return render_template("login.html")

@app.route('/register', methods=['POST'])
def register():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    address = request.form.get('address')
    dob_str = request.form.get('dob')
    pan = request.form.get('pan')
    aadhar = request.form.get('aadhar')
    initial_deposit = request.form.get('deposit')
    mpin = request.form.get('mpin')

    # Validate required fields
    if not all([name, email, phone, address, dob_str, pan, aadhar, initial_deposit, mpin]):
        flash('Please fill in all required fields.')
        return redirect(url_for('login'))

    # Convert dob string to date object (input type="date" sends yyyy-mm-dd)
    try:
        dob = datetime.strptime(dob_str, '%Y-%m-%d')
    except ValueError:
        flash('Invalid date format for Date of Birth.')
        return redirect(url_for('login'))

    # Generate new account number
    account_no = User.generate_account_number()

    # Create new user object
    user = User(
        account_no=account_no,
        name=name,
        email=email,
        phone=phone,
        address=address,
        dob=dob,
        pan=pan,
        aadhar=aadhar,
        balance=float(initial_deposit),
        mpin=mpin
    )
    user.save()
    flash(f'Registration successful! Your account number is {account_no}. Please login.')
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if session.get('user_role') == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif session.get('user_role') == 'user':
        return redirect(url_for('user_dashboard'))
    else:
        flash('Please log in to access this page')
        return redirect(url_for('login'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('user_role') != 'admin':
        flash('Please log in as admin to access this page')
        return redirect(url_for('login'))
    # Fetch users and transactions from MongoDB
    users = list(mongo.db.users.find())
    transactions = list(mongo.db.transactions.find())
    return render_template("admin/dashboard.html", users=users, transactions=transactions)

@app.route('/user/dashboard')
def user_dashboard():
    if session.get('user_role') != 'user':
        flash('Please log in as user to access this page')
        return redirect(url_for('login'))
    # Get current user's account info
    account_no = session.get("account_no")
    user = User.find_by_account_no(account_no)
    transactions = Transaction.find_by_user(account_no)
    return render_template("user/dashboard.html", user=user, transactions=transactions)

@app.route('/admin/users')
def admin_users():
    if session.get('user_role') != 'admin':
        flash('Please log in as admin to access this page')
        return redirect(url_for('login'))
    users = User.find_all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/add_user', methods=['GET', 'POST'])
def admin_add_user():
    if session.get('user_role') != 'admin':
        flash('Please log in as admin to access this page')
        return redirect(url_for('login'))
    form = AddUserForm()
    if form.validate_on_submit():
        initial_deposit = form.initial_deposit.data
        if initial_deposit <= 0:
            flash('Initial deposit must be greater than 0')
            return redirect(url_for('admin_add_user'))
        account_no = User.generate_account_number()
        name = form.name.data
        email = form.email.data
        phone = form.phone.data
        address = form.address.data
        dob = form.dob.data
        pan = form.pan.data
        aadhar = form.aadhar.data
        mpin = form.mpin.data
        user = User(account_no, name, email, mpin, balance=initial_deposit, phone=phone, address=address, dob=dob, pan=pan, aadhar=aadhar)
        user.save()
        flash('User added successfully')
        return redirect(url_for('admin_users'))
    return render_template('admin/add_user.html', form=form)

@app.route('/admin/delete_user/<account_no>', methods=['POST'])
def admin_delete_user(account_no):
    if session.get('user_role') != 'admin':
        flash('Please log in as admin to access this page')
        return redirect(url_for('login'))
    mongo.db.users.delete_one({'account_no': account_no})
    flash('User deleted successfully')
    return redirect(url_for('admin_users'))

@app.route('/admin/credit_debit', methods=['GET', 'POST'])
def admin_credit_debit():
    if session.get('user_role') != 'admin':
        flash('Please log in as admin to access this page')
        return redirect(url_for('login'))
    users = User.find_all()
    form = CreditDebitForm()
    form.user_id.choices = [(user.account_no, f"{user.name} ({user.account_no})") for user in users]
    if form.validate_on_submit():
        account_no = form.user_id.data
        transaction_type = form.transaction_type.data
        amount = form.amount.data
        if transaction_type == 'credit':
            credit_user(account_no, amount)
        else:
            debit_user(account_no, amount)
        flash('Transaction completed successfully')
        return redirect(url_for('admin_credit_debit'))
    return render_template('admin/credit_debit.html', form=form, users=users)

@app.route('/admin/transactions')
def admin_transactions():
    if session.get('user_role') != 'admin':
        flash('Please log in as admin to access this page')
        return redirect(url_for('login'))
    transactions = Transaction.find_all()
    # Filter duplicates by unique transaction_id
    unique_txn_ids = set()
    filtered_transactions = []
    for txn in transactions:
        txn_id = txn.get('transaction_id') or txn.get('txn_id')
        if txn_id and txn_id not in unique_txn_ids:
            unique_txn_ids.add(txn_id)
            # Determine display_type
            txn_type = txn.get('type', '')
            if txn_type == 'transfer':
                # Determine credit or debit based on sender and receiver
                sender = txn.get('sender_account', '')
                receiver = txn.get('receiver_account', '')
                # For admin view, assume admin account is 'admin'
                if sender == 'admin':
                    display_type = 'debit'
                else:
                    display_type = 'credit'
            else:
                display_type = txn_type
            txn['display_type'] = display_type
            filtered_transactions.append(txn)
    return render_template('admin/transactions.html', transactions=filtered_transactions)

@app.route('/admin/requests', methods=['GET', 'POST'])
def admin_requests():
    if session.get('user_role') != 'admin':
        flash('Please log in as admin to access this page')
        return redirect(url_for('login'))
    if request.method == 'POST':
        req_id = request.form.get('request_id')
        action = request.form.get('action')
        if action == 'approve':
            approve_request(req_id)
            flash('Request approved')
        else:
            reject_request(req_id)
            flash('Request rejected')
        return redirect(url_for('admin_requests'))
    requests_list = Request.find_all()
    return render_template('admin/requests.html', requests=requests_list)

@app.route('/user/balance')
def user_balance():
    if session.get('user_role') != 'user':
        flash('Please log in as user to access this page')
        return redirect(url_for('login'))
    account_no = session.get('account_no')
    user = User.find_by_account_no(account_no)
    return render_template('user/balance.html', balance=user.balance)

@app.route('/user/transfer', methods=['GET', 'POST'])
def user_transfer():
    if session.get('user_role') != 'user':
        flash('Please log in as user to access this page')
        return redirect(url_for('login'))
    form = TransferForm()
    current_acc = session.get('account_no')
    if form.validate_on_submit():
        recipient_acc = form.recipient.data
        amount = form.amount.data
        mpin = form.mpin.data
        if recipient_acc == current_acc:
            flash('Cannot transfer to yourself')
            return redirect(url_for('user_transfer'))
        recipient = User.find_by_account_no(recipient_acc)
        if not recipient:
            flash('Invalid account number')
            return redirect(url_for('user_transfer'))
        current_user = User.find_by_account_no(current_acc)
        if not current_user.check_mpin(mpin):
            flash('Invalid MPIN')
            return redirect(url_for('user_transfer'))
        if transfer_money(current_acc, recipient_acc, amount):
            flash('Transfer successful')
            return redirect(url_for('user_dashboard'))
        else:
            flash('Transfer failed')
            return redirect(url_for('user_transfer'))
    return render_template('user/transfer.html', form=form)

@app.route('/user/request', methods=['GET', 'POST'])
def user_request():
    if session.get('user_role') != 'user':
        flash('Please log in as user to access this page')
        return redirect(url_for('login'))
    form = RequestForm()
    if form.validate_on_submit():
        account_no = session.get('account_no')
        req_type = form.request_type.data
        submit_request(account_no, req_type)
        flash('Request submitted successfully')
        return redirect(url_for('user_dashboard'))
    return render_template('user/request.html', form=form)

@app.route('/user/requests')
def user_requests():
    if session.get('user_role') != 'user':
        flash('Please log in as user to access this page')
        return redirect(url_for('login'))
    account_no = session.get('account_no')
    requests_list = list(mongo.db.requests.find({'acc_no': account_no}))
    return render_template('user/requests.html', requests=requests_list)

@app.route('/user/transactions')
def user_transactions():
    if session.get('user_role') != 'user':
        flash('Please log in as user to access this page')
        return redirect(url_for('login'))
    account_no = session.get('account_no')
    transactions = Transaction.find_by_user(account_no)
    seen_txn_ids = set()
    filtered_transactions = []
    for txn in transactions:
        txn_id = txn.get('transaction_id') or txn.get('txn_id')
        if not txn_id or txn_id in seen_txn_ids:
            continue
        txn_type = txn.get('type', '')
        if txn_type == 'transfer':
            sender = txn.get('sender_account', '')
            receiver = txn.get('receiver_account', '')
            # Only include transaction if user is sender or receiver
            if sender == account_no:
                txn['type'] = 'debit'
            elif receiver == account_no:
                txn['type'] = 'credit'
            else:
                continue
        seen_txn_ids.add(txn_id)
        filtered_transactions.append(txn)
    for txn in filtered_transactions:
        txn['_id'] = str(txn['_id'])
    return render_template('user/transactions.html', transactions=filtered_transactions)

@app.route('/user/passbook')
def user_passbook():
    if session.get('user_role') != 'user':
        flash('Please log in as user to access this page')
        return redirect(url_for('login'))
    account_no = session.get('account_no')
    user = User.find_by_account_no(account_no)
    transactions = Transaction.find_by_user(account_no)
    seen_txn_ids = set()
    filtered_transactions = []
    for txn in transactions:
        txn_id = txn.get('transaction_id') or txn.get('txn_id')
        if not txn_id or txn_id in seen_txn_ids:
            continue
        txn_type = txn.get('type', '')
        if txn_type == 'transfer':
            sender = txn.get('sender_account', '')
            receiver = txn.get('receiver_account', '')
            # Only include transaction if user is sender or receiver
            if sender == account_no:
                txn['type'] = 'debit'
            elif receiver == account_no:
                txn['type'] = 'credit'
            else:
                continue
        seen_txn_ids.add(txn_id)
        filtered_transactions.append(txn)
    filtered_transactions.sort(key=lambda x: x['transaction_time']['timestamp'])
    masked_aadhar = mask_aadhar(user.aadhar) if user.aadhar else ''
    return render_template('user/passbook.html', user=user, transactions=filtered_transactions, masked_aadhar=masked_aadhar)


@app.route('/user/passbook/pdf')
def user_passbook_pdf():
    if session.get('user_role') != 'user':
        flash('Please log in as user to access this page')
        return redirect(url_for('login'))
    account_no = session.get('account_no')
    user = User.find_by_account_no(account_no)
    transactions = Transaction.find_by_user(account_no)
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    if start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            # Set end_date to end of day
            end_date = end_date.replace(hour=23, minute=59, second=59)
            transactions = [txn for txn in transactions if start_date <= txn['transaction_time']['timestamp'] <= end_date]
        except ValueError:
            flash('Invalid date format. Please use yyyy-mm-dd.')
            return redirect(url_for('user_passbook'))
    transactions.sort(key=lambda x: x['transaction_time']['timestamp'])
    buffer = generate_passbook_pdf(user, transactions)
    if buffer is None:
        flash('Failed to generate PDF.')
        return redirect(url_for('user_passbook'))
    buffer.seek(0)
    response = send_file(buffer, as_attachment=True, download_name='passbook.pdf', mimetype='application/pdf')
    response.headers["Content-Disposition"] = "attachment; filename=passbook.pdf"
    return response

# Create initial admin and users if none exist
with app.app_context():
    if mongo.db.admins.count_documents({}) == 0:
        Admin.add_admin('admin', 'admin123')
        print("Default admin created: username='admin', password='admin123'")
    if mongo.db.users.count_documents({}) == 0:
        # Create sample users
        User.add_user('1234567890', 'John Doe', 'john@example.com', '1234', 1000.0)
        User.add_user('0987654321', 'Jane Smith', 'jane@example.com', '5678', 500.0)
        print("Sample users created")

if __name__ == '__main__':
    app.run(debug=True)

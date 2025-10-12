import bcrypt
import random
from datetime import datetime, date
from flask_login import UserMixin
from db import mongo
from bson import ObjectId

# User Model for regular users
# Collection: users
# Fields: account_no (unique), name, email, mpin, balance, role ('user'), status, created_at
class User(UserMixin):
    def __init__(self, account_no, name, email, mpin, balance=0.0, role='user', status='active', created_at=None, first_login=True, phone='', address='', ifsc_code='', micr_code='', cif_no='', dob=None, pan='', aadhar=''):
        self.account_no = account_no  # Unique account number
        self.name = name
        self.email = email
        self.mpin = mpin  # Store plain text MPIN
        self.balance = balance
        self.role = role  # 'user'
        self.status = status  # 'active', 'inactive', etc.
        self.created_at = created_at or datetime.utcnow()
        self.first_login = first_login  # True for new users
        self.phone = phone
        self.address = address
        self.ifsc_code = ifsc_code or self.generate_ifsc_code()
        self.micr_code = micr_code or self.generate_micr_code()
        self.cif_no = cif_no or self.generate_cif_no()
        self.dob = dob
        self.pan = pan
        self.aadhar = aadhar

    @staticmethod
    def generate_account_number():
        return str(random.randint(1000000000, 9999999999))

    @staticmethod
    def generate_ifsc_code():
        return "CODE" + str(random.randint(10000, 99999))

    @staticmethod
    def generate_micr_code():
        return str(random.randint(100000000, 999999999))

    @staticmethod
    def generate_cif_no():
        return str(random.randint(100000000, 999999999))

    def save(self):
        """Save user to MongoDB users collection"""
        # Convert dob to datetime if it's a date object
        dob_to_save = self.dob
        if isinstance(dob_to_save, date) and not isinstance(dob_to_save, datetime):
            dob_to_save = datetime.combine(dob_to_save, datetime.min.time())

        mongo.db.users.insert_one({
            'account_no': self.account_no,
            'name': self.name,
            'email': self.email,
            'mpin': self.mpin,
            'balance': self.balance,
            'role': self.role,
            'status': self.status,
            'created_at': self.created_at,
            'first_login': self.first_login,
            'phone': self.phone,
            'address': self.address,
            'ifsc_code': self.ifsc_code,
            'micr_code': self.micr_code,
            'cif_no': self.cif_no,
            'dob': dob_to_save,
            'pan': self.pan,
            'aadhar': self.aadhar
        })

    def update_balance(self, amount):
        """Update user balance"""
        self.balance += amount
        mongo.db.users.update_one({'account_no': self.account_no}, {'$set': {'balance': self.balance}})

    def check_mpin(self, mpin):
        """Check MPIN"""
        return self.mpin == mpin

    def set_first_login(self, value):
        """Set first_login flag"""
        self.first_login = value
        mongo.db.users.update_one({'account_no': self.account_no}, {'$set': {'first_login': self.first_login}})

    def get_id(self):
        return self.account_no

    @staticmethod
    def find_by_account_no(account_no):
        """Find user by account number"""
        user_data = mongo.db.users.find_one({'account_no': account_no})
        if user_data:
            user = User(
                account_no=user_data['account_no'],
                name=user_data['name'],
                email=user_data['email'],
                mpin=user_data.get('mpin', ''),
                balance=user_data.get('balance', 0.0),
                role=user_data.get('role', 'user'),
                status=user_data.get('status', 'active'),
                created_at=user_data.get('created_at'),
                first_login=user_data.get('first_login', True),
                phone=user_data.get('phone', ''),
                address=user_data.get('address', ''),
                ifsc_code=user_data.get('ifsc_code', ''),
                micr_code=user_data.get('micr_code', ''),
                cif_no=user_data.get('cif_no', ''),
                dob=user_data.get('dob'),
                pan=user_data.get('pan', ''),
                aadhar=user_data.get('aadhar', '')
            )
            return user
        return None

    @staticmethod
    def find_all():
        """Find all users"""
        users = []
        for user_data in mongo.db.users.find():
            user = User.find_by_account_no(user_data['account_no'])
            users.append(user)
        return users

    @staticmethod
    def add_user(account_no, name, email, mpin, balance=0.0, phone='', address=''):
        """Add a new user"""
        user = User(account_no, name, email, mpin, balance, phone=phone, address=address)
        user.save()
        return user

# Transaction Model
# Collection: transactions
# Fields: transaction_id, type, sender_account, receiver_account, amount, currency, status, method, description, balance_after_transaction, transaction_time
class Transaction:
    def __init__(self, transaction_id, txn_type, sender_account, receiver_account, amount, currency='INR', status='success', method='Transfer', balance_after_transaction=0.0, transaction_time=None):
        self.transaction_id = transaction_id  # Unique transaction ID like "CODE2025100812"
        self.txn_type = txn_type  # 'credit', 'debit', 'transfer'
        self.sender_account = sender_account
        self.receiver_account = receiver_account
        self.amount = amount
        self.currency = currency  # 'INR'
        self.status = status  # 'success', 'failed', 'pending'
        self.method = method  # 'UPI', 'NEFT', 'IMPS', 'QR', 'Cash', 'Transfer', 'Cash Submit in Bank'
        self.balance_after_transaction = balance_after_transaction  # Sender's balance after transaction
        self.transaction_time = transaction_time or {
            'date': datetime.utcnow().strftime('%Y-%m-%d'),
            'time': datetime.utcnow().strftime('%H:%M:%S'),
            'timestamp': datetime.utcnow()
        }

    def save(self):
        """Save transaction to MongoDB transactions collection"""
        return mongo.db.transactions.insert_one({
            'transaction_id': self.transaction_id,
            'type': self.txn_type,
            'sender_account': self.sender_account,
            'receiver_account': self.receiver_account,
            'amount': self.amount,
            'currency': self.currency,
            'status': self.status,
            'method': self.method,
            'balance_after_transaction': self.balance_after_transaction,
            'transaction_time': self.transaction_time
        }).inserted_id

    @staticmethod
    def find_by_user(account_no):
        """Find transactions for a user (as sender or receiver)"""
        return list(mongo.db.transactions.find({
            '$or': [
                {'sender_account': account_no},
                {'receiver_account': account_no}
            ]
        }))

    @staticmethod
    def find_all():
        """Find all transactions"""
        return list(mongo.db.transactions.find())

    @staticmethod
    def record_transaction(sender_acc, receiver_acc, amount, txn_type, method='Transfer', balance_after=0.0, status='success'):
        """Record a new transaction"""
        now = datetime.utcnow()
        import random
        transaction_id = f"CODE{random.randint(10000, 99999)}"  # Fixed prefix CODE + random 5 digit number
        transaction_time = {
            'date': now.strftime('%Y-%m-%d'),
            'time': now.strftime('%H:%M:%S'),
            'timestamp': now
        }
        txn = Transaction(transaction_id, txn_type, sender_acc, receiver_acc, amount, currency='INR', status=status, method=method, balance_after_transaction=balance_after, transaction_time=transaction_time)
        txn.save()
        return txn

# Request Model
# Collection: requests
# Fields: req_id, acc_no, type ('passbook'/'chequebook'), status, created_at
class Request:
    def __init__(self, req_id, acc_no, req_type, status='pending', created_at=None):
        self.req_id = req_id  # Unique request ID
        self.acc_no = acc_no
        self.req_type = req_type  # 'passbook', 'chequebook'
        self.status = status  # 'pending', 'approved', 'rejected'
        self.created_at = created_at or datetime.utcnow()

    def save(self):
        """Save request to MongoDB requests collection"""
        return mongo.db.requests.insert_one({
            'req_id': self.req_id,
            'acc_no': self.acc_no,
            'type': self.req_type,
            'status': self.status,
            'created_at': self.created_at
        }).inserted_id

    def update_status(self, status):
        """Update request status"""
        self.status = status
        mongo.db.requests.update_one({'req_id': self.req_id}, {'$set': {'status': status}})

    @staticmethod
    def find_all():
        """Find all requests"""
        return list(mongo.db.requests.find())

    @staticmethod
    def find_by_id(req_id):
        """Find request by ID"""
        return mongo.db.requests.find_one({'req_id': req_id})

    @staticmethod
    def log_request(acc_no, req_type):
        """Log a new request"""
        req_id = str(ObjectId())  # Generate unique req_id
        req = Request(req_id, acc_no, req_type)
        req.save()
        return req

# QR Transfer Model (optional)
# Collection: qr_transfers
# Fields: qr_id, sender_acc, receiver_acc, amount, status, date
class QRTransfer:
    def __init__(self, qr_id, sender_acc, receiver_acc, amount, status='pending', date=None):
        self.qr_id = qr_id  # Unique QR ID
        self.sender_acc = sender_acc
        self.receiver_acc = receiver_acc
        self.amount = amount
        self.status = status  # 'pending', 'completed', 'failed'
        self.date = date or datetime.utcnow()

    def save(self):
        """Save QR transfer to MongoDB qr_transfers collection"""
        return mongo.db.qr_transfers.insert_one({
            'qr_id': self.qr_id,
            'sender_acc': self.sender_acc,
            'receiver_acc': self.receiver_acc,
            'amount': self.amount,
            'status': self.status,
            'date': self.date
        }).inserted_id

    @staticmethod
    def find_all():
        """Find all QR transfers"""
        return list(mongo.db.qr_transfers.find())

    @staticmethod
    def simulate_qr_transfer(sender_acc, receiver_acc, amount):
        """Simulate QR code transfer"""
        qr_id = str(ObjectId())  # Generate unique qr_id
        qr_transfer = QRTransfer(qr_id, sender_acc, receiver_acc, amount)
        qr_transfer.save()
        # In a real app, this would integrate with QR scanning logic
        return qr_transfer

# Admin Model
# Collection: admins
# Fields: username (unique), hashed_password, role ('admin'), created_at
class Admin:
    def __init__(self, username, password, role='admin', created_at=None):
        self.username = username
        self.hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8') if password else None
        self.role = role
        self.created_at = created_at or datetime.utcnow()

    def save(self):
        """Save admin to MongoDB admins collection"""
        mongo.db.admins.insert_one({
            'username': self.username,
            'hashed_password': self.hashed_password,
            'role': self.role,
            'created_at': self.created_at
        })

    def check_password(self, password):
        """Check password"""
        return bcrypt.checkpw(password.encode('utf-8'), self.hashed_password.encode('utf-8')) if self.hashed_password else False

    @staticmethod
    def find_by_username(username):
        """Find admin by username"""
        admin_data = mongo.db.admins.find_one({'username': username})
        if admin_data:
            admin = Admin(
                username=admin_data['username'],
                password='',  # Don't load plain password
                role=admin_data.get('role', 'admin'),
                created_at=admin_data.get('created_at')
            )
            admin.hashed_password = admin_data.get('hashed_password')
            return admin
        return None

    @staticmethod
    def add_admin(username, password):
        """Add a new admin"""
        admin = Admin(username, password)
        admin.save()
        return admin

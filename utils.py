# Utility functions for Code Yatra Bank

from models import User, Transaction, Request, QRTransfer
from bson import ObjectId

def transfer_money(sender_acc, recipient_acc, amount):
    """
    Handle user-to-user money transfer.
    Validates sender balance, updates balances, and logs transactions.
    Returns True if successful, False otherwise.
    """
    sender = User.find_by_account_no(sender_acc)
    recipient = User.find_by_account_no(recipient_acc)

    if not sender or not recipient:
        return False

    if sender.balance < amount:
        return False

    # Deduct from sender
    sender.update_balance(-amount)
    # Add to recipient
    recipient.update_balance(amount)

    # Refresh sender balance from DB after update
    sender = User.find_by_account_no(sender_acc)
    # Refresh recipient balance from DB after update
    recipient = User.find_by_account_no(recipient_acc)

    # Log only one transaction record with updated balances
    Transaction.record_transaction(sender_acc, recipient_acc, amount, 'transfer', method='Transfer', balance_after=sender.balance)

    return True

def credit_user(account_no, amount):
    """
    Credit amount to user's account (admin function).
    """
    user = User.find_by_account_no(account_no)
    if user:
        user.update_balance(amount)
        Transaction.record_transaction('admin', account_no, amount, 'credit', method='Cash Submit in Bank', balance_after=user.balance)
        return True
    return False

def debit_user(account_no, amount):
    """
    Debit amount from user's account (admin function).
    """
    user = User.find_by_account_no(account_no)
    if user and user.balance >= amount:
        user.update_balance(-amount)
        Transaction.record_transaction(account_no, 'admin', amount, 'debit', method='Cash', balance_after=user.balance)
        return True
    return False

def submit_request(account_no, request_type):
    """
    Submit a request (passbook or chequebook).
    """
    return Request.log_request(account_no, request_type)

def approve_request(req_id):
    """
    Approve a request.
    """
    req_data = Request.find_by_id(req_id)
    if req_data:
        req = Request(req_data['req_id'], req_data['acc_no'], req_data['type'], req_data['status'], req_data['created_at'])
        req.update_status('approved')
        return True
    return False

def reject_request(req_id):
    """
    Reject a request.
    """
    req_data = Request.find_by_id(req_id)
    if req_data:
        req = Request(req_data['req_id'], req_data['acc_no'], req_data['type'], req_data['status'], req_data['created_at'])
        req.update_status('rejected')
        return True
    return False

def qr_transfer(sender_acc, receiver_acc, amount):
    """
    Simulate QR code transfer.
    """
    # Check balance
    sender = User.find_by_account_no(sender_acc)
    if not sender or sender.balance < amount:
        return False

    # Deduct and add
    sender.update_balance(-amount)
    recipient = User.find_by_account_no(receiver_acc)
    if recipient:
        recipient.update_balance(amount)

    # Log QR transfer
    QRTransfer.simulate_qr_transfer(sender_acc, receiver_acc, amount)
    # Log transactions
    Transaction.record_transaction(sender_acc, receiver_acc, amount, 'transfer')
    return True

def mask_aadhar(aadhar):
    """
    Mask Aadhaar number to show only last 4 digits.
    Example: 123456789012 -> XXXX XXXX 9012
    """
    if not aadhar or len(aadhar) < 4:
        return aadhar
    return "XXXX XXXX " + aadhar[-4:]

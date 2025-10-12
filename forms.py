from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, FloatField, HiddenField, DateField
from wtforms.validators import DataRequired, Optional, Length, Regexp

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class AddUserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    phone = StringField('Phone', validators=[Optional()])
    address = StringField('Address', validators=[Optional()])
    dob = DateField('Date of Birth', format='%Y-%m-%d', validators=[Optional()])
    pan = StringField('PAN Number', validators=[Optional(), Length(min=10, max=10), Regexp(r'^[A-Z]{4}\d{6}$', message='PAN must be 4 uppercase letters followed by 6 digits')])
    aadhar = StringField('Aadhar Number', validators=[Optional(), Length(min=12, max=12)])
    initial_deposit = FloatField('Initial Deposit', validators=[DataRequired()])
    mpin = PasswordField('MPIN', validators=[DataRequired()])
    submit = SubmitField('Add User')

class CreditDebitForm(FlaskForm):
    user_id = SelectField('User', choices=[], validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired()])
    transaction_type = SelectField('Type', choices=[('credit', 'Credit'), ('debit', 'Debit')], validators=[DataRequired()])
    submit = SubmitField('Submit')

class ApproveRequestForm(FlaskForm):
    request_id = HiddenField('Request ID')
    action = SelectField('Action', choices=[('approve', 'Approve'), ('reject', 'Reject')], validators=[DataRequired()])
    submit = SubmitField('Submit')

class TransferForm(FlaskForm):
    recipient = StringField('Recipient Account Number', validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired()])
    mpin = PasswordField('MPIN', validators=[DataRequired()])
    submit = SubmitField('Transfer')

class RequestForm(FlaskForm):
    request_type = SelectField('Request Type', choices=[('passbook', 'Passbook'), ('chequebook', 'Cheque Book')], validators=[DataRequired()])
    submit = SubmitField('Request')

import bcrypt

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'
ADMIN_PASSWORD_HASH = bcrypt.hashpw(ADMIN_PASSWORD.encode('utf-8'), bcrypt.gensalt())

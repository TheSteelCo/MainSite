import hashlib
import os

from Crypto.Cipher import AES
from flask import current_app
from sqlalchemy import create_engine, event
from sqlalchemy.exc import DisconnectionError
from sqlalchemy.orm import scoped_session, sessionmaker

KEY = '9ewguweigwebowieb89h'

if os.environ.get('DATABASE_URL') is None:
    SQL_ALCHEMY_DATABASE_URI = 'mysql://dbsteelco:Royal72uk@thesteelco.com/thesteelco'
else:
    SQL_ALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']


def checkout_listener(dbapi_con, con_record, con_proxy):
    try:
        try:
            dbapi_con.ping(False)
        except TypeError:
            dbapi_con.ping()
    except dbapi_con.OperationalError as exc:
        if exc.args[0] in (2006, 2013, 2014, 2045, 2055):
            raise DisconnectionError()
        else:
            raise


def get_db():
    if not hasattr(current_app, 'db'):
        engine = create_engine(SQL_ALCHEMY_DATABASE_URI, pool_size=100, pool_recycle=3000)
        event.listen(engine, 'checkout', checkout_listener)
        db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
        current_app.db = db_session
    return current_app.db


def encrypt(string):
    return _AESencrypt(KEY, string)


def decrypt(encrypted_string):
    return _AESdecrypt(KEY, encrypted_string)


def _AESencrypt(password, plaintext, base64=False):
    SALT_LENGTH = 32
    DERIVATION_ROUNDS = 1337
    BLOCK_SIZE = 16
    KEY_SIZE = 32
    MODE = AES.MODE_CBC
     
    salt = os.urandom(SALT_LENGTH)
    iv = os.urandom(BLOCK_SIZE)
     
    paddingLength = 16 - (len(plaintext) % 16)
    paddedPlaintext = plaintext + chr(paddingLength) * paddingLength
    derivedKey = password
    for i in range(0, DERIVATION_ROUNDS):
        derivedKey = hashlib.sha256(derivedKey + salt).digest()
    derivedKey = derivedKey[:KEY_SIZE]
    cipherSpec = AES.new(derivedKey, MODE, iv)
    ciphertext = cipherSpec.encrypt(paddedPlaintext)
    ciphertext = ciphertext + iv + salt
    if base64:
        import base64
        return base64.b64encode(ciphertext)
    else:
        return ciphertext.encode("hex")
 

def _AESdecrypt(password, ciphertext, base64=False):
    SALT_LENGTH = 32
    DERIVATION_ROUNDS = 1337
    BLOCK_SIZE = 16
    KEY_SIZE = 32
    MODE = AES.MODE_CBC
     
    if base64:
        import base64
        decodedCiphertext = base64.b64decode(ciphertext)
    else:
        decodedCiphertext = ciphertext.decode("hex")
    startIv = len(decodedCiphertext) - BLOCK_SIZE - SALT_LENGTH
    startSalt = len(decodedCiphertext) - SALT_LENGTH
    data, iv, salt = decodedCiphertext[:startIv], decodedCiphertext[startIv:startSalt], decodedCiphertext[startSalt:]
    derivedKey = password
    for i in range(0, DERIVATION_ROUNDS):
        derivedKey = hashlib.sha256(derivedKey + salt).digest()
    derivedKey = derivedKey[:KEY_SIZE]
    cipherSpec = AES.new(derivedKey, MODE, iv)
    plaintextWithPadding = cipherSpec.decrypt(data)
    paddingLength = ord(plaintextWithPadding[-1])
    plaintext = plaintextWithPadding[:-paddingLength]
    return plaintext

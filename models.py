from flask_bcrypt import generate_password_hash
from flask_login import UserMixin
from peewee import *

DATABASE = SqliteDatabase('journal.db')

def initialize():
    DATABASE.connect()
    DATABASE.create_tables([], safe=True)
    DATABASE.close()
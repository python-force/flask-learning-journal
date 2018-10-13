from flask_bcrypt import generate_password_hash
from flask_login import UserMixin
from slugify import slugify
import datetime
from peewee import *

DATABASE = SqliteDatabase('journal.db')

class User(UserMixin, Model):
    pub_date = DateTimeField(default=datetime.datetime.now)
    email = CharField(unique=True)
    password = CharField(max_length=100)

    class Meta:
        database = DATABASE
        order_by = ('-pub_date',)


    @classmethod
    def create_user(cls, email, password):
        try:
            with DATABASE.transaction():
                cls.create(
                    email=email,
                    password=generate_password_hash(password))
        except IntegrityError:
            raise ValueError("User already exists")


class Journal(Model):
    user = ForeignKeyField(model=User, related_name='journals')
    pub_date = DateTimeField(default=datetime.datetime.now)
    title = CharField(max_length=30)
    slug = CharField(max_length=50)
    date = DateTimeField()
    time_spent = IntegerField(min)
    learned = TextField()
    resources = TextField()

    class Meta:
        database = DATABASE
        order_by = ('-pub_date',)


    def __init__(self, *args, **kwargs):
        if not 'slug' in kwargs:
            kwargs['slug'] = slugify(kwargs.get('title', ''))
        super().__init__(*args, **kwargs)

def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Journal], safe=True)
    DATABASE.close()
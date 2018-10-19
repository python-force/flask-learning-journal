import unittest
from peewee import *
from models import User, Tag, Journal

MODELS = [User, Tag, Journal]

# use an in-memory SQLite for tests.
test_db = SqliteDatabase(':memory:')

USER_DATA = {
    'email': 'test_0@example.com',
    'password': 'password'
}


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        # Bind model classes to test db. Since we have a complete list of
        # all models, we do not need to recursively bind dependencies.
        test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)

        test_db.connect()
        test_db.create_tables(MODELS)

    @staticmethod
    def create_users(count=2):
        for i in range(count):
            User.create_user(
                email='test_{}@example.com'.format(i),
                password='password'
            )

    def test_create_user(self):
        self.create_users()
        self.assertEqual(User.select().count(), 2)
        self.assertNotEqual(
            User.select().get().password,
            'password'
        )

    def test_create_duplicate_user(self):
        self.create_users()
        with self.assertRaises(ValueError):
            User.create_user(
                email='test_1@example.com',
                password='password'
            )

    def test_journal_creation(self):
        self.create_users()
        user = User.select().get()
        Journal.create(
            user=user,
            title='Space',
            date='2018-10-12',
            time_spent=12,
            learned='Test',
            resources='Test'
        )
        journal = Journal.select().get()

        self.assertEqual(Journal.select().count(), 1)
        self.assertEqual(journal.user, user)

    def test_tag_creation(self):
        self.create_users()
        Tag.create(
            title='Space',
        )

        self.assertEqual(Tag.select().count(), 1)

    def tearDown(self):
        # Not strictly necessary since SQLite in-memory databases only live
        # for the duration of the connection, and in the next step we close
        # the connection...but a good practice all the same.
        test_db.drop_tables(MODELS)

        # Close connection to db.
        test_db.close()

        # If we wanted, we could re-bind the models to their original
        # database here. But for tests this is probably not necessary.


if __name__ == '__main__':
    unittest.main()

import unittest
from peewee import *
import datetime
from models import User, Tag, Journal

import app
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


"""
class UserModelTestCase(unittest.TestCase):
    @staticmethod
    def create_users(count=2):
        for i in range(count):
            User.create_user(
                email='test_{}@example.com'.format(i),
                password='password'
            )

    def test_create_user(self):
        with test_database(TEST_DB, (User,)):
            self.create_users()
            self.assertEqual(User.select().count(), 2)
            self.assertNotEqual(
                User.select().get().password,
                'password'
            )

    def test_create_duplicate_user(self):
        with test_database(TEST_DB, (User,)):
            self.create_users()
            with self.assertRaises(ValueError):
                User.create_user(
                    email='test_1@example.com',
                    password='password'
                )


class JournalModelTestCase(unittest.TestCase):
    def test_journal_creation(self):
        with test_database(TEST_DB, (User, Journal)):
            UserModelTestCase.create_users()
            user = User.select().get()
            Journal.create(
                user=user,
                protein='chicken',
                shell='flour',
                cheese=False,
                extras='Gimme some guac.'
            )
            taco = Taco.select().get()

            self.assertEqual(
                Taco.select().count(),
                1
            )
            self.assertEqual(taco.user, user)




class ViewTestCase(unittest.TestCase):
    def setUp(self):
        tacocat.app.config['TESTING'] = True
        tacocat.app.config['WTF_CSRF_ENABLED'] = False
        self.app = tacocat.app.test_client()


class UserViewsTestCase(ViewTestCase):
    def test_registration(self):
        data = {
            'email': 'test@example.com',
            'password': 'password',
            'password2': 'password'
        }
        with test_database(TEST_DB, (User,)):
            rv = self.app.post(
                '/register',
                data=data)
            self.assertEqual(rv.status_code, 302)
            self.assertEqual(rv.location, 'http://localhost/')

    def test_good_login(self):
        with test_database(TEST_DB, (User,)):
            UserModelTestCase.create_users(1)
            rv = self.app.post('/login', data=USER_DATA)
            self.assertEqual(rv.status_code, 302)
            self.assertEqual(rv.location, 'http://localhost/')

    def test_bad_login(self):
        with test_database(TEST_DB, (User,)):
            rv = self.app.post('/login', data=USER_DATA)
            self.assertEqual(rv.status_code, 200)

    def test_logout(self):
        with test_database(TEST_DB, (User,)):
            # Create and login the user
            UserModelTestCase.create_users(1)
            self.app.post('/login', data=USER_DATA)

            rv = self.app.get('/logout')
            self.assertEqual(rv.status_code, 302)
            self.assertEqual(rv.location, 'http://localhost/')

    def test_logged_out_menu(self):
        rv = self.app.get('/')
        self.assertIn("sign up", rv.get_data(as_text=True).lower())
        self.assertIn("log in", rv.get_data(as_text=True).lower())

    def test_logged_in_menu(self):
        with test_database(TEST_DB, (User,)):
            UserModelTestCase.create_users(1)
            self.app.post('/login', data=USER_DATA)
            rv = self.app.get('/')
            self.assertIn("add a new taco", rv.get_data(as_text=True).lower())
            self.assertIn("log out", rv.get_data(as_text=True).lower())


class TacoViewsTestCase(ViewTestCase):
    def test_empty_db(self):
        with test_database(TEST_DB, (Taco,)):
            rv = self.app.get('/')
            self.assertIn("no tacos yet", rv.get_data(as_text=True).lower())

    def test_taco_create(self):
        taco_data = {
            'protein': 'chicken',
            'shell': 'flour',
            'cheese': False,
            'extras': 'Gimme some guac.'
        }
        with test_database(TEST_DB, (User, Taco)):
            UserModelTestCase.create_users(1)
            self.app.post('/login', data=USER_DATA)

            taco_data['user'] = User.select().get()
            rv = self.app.post('/taco', data=taco_data)
            self.assertEqual(rv.status_code, 302)
            self.assertEqual(rv.location, 'http://localhost/')
            self.assertEqual(Taco.select().count(), 1)

    def test_taco_list(self):
        taco_data = {
            'protein': 'chicken',
            'shell': 'flour',
            'cheese': False,
            'extras': 'Gimme some guac.'
        }
        with test_database(TEST_DB, (User, Taco)):
            UserModelTestCase.create_users(1)
            taco_data['user'] = User.select().get()
            Taco.create(**taco_data)

            rv = self.app.get('/')
            self.assertNotIn('no tacos yet', rv.get_data(as_text=True))
            self.assertIn(taco_data['extras'], rv.get_data(as_text=True))
"""

if __name__ == '__main__':
    unittest.main()

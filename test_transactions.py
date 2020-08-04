from datetime import datetime, timedelta
import unittest
from app import app, db
from app.models import Transaction, TransactionType, Account, Category


DEFAULT_CATEGORIES = [
    'Category 1'
]


DEFAULT_ACCOUNTS = [
    {'name': 'Account 1', 'currency': '€', 'balance': 0.0, 'description': ''},
    {'name': 'Account 2', 'currency': '€', 'balance': 0.0, 'description': ''},
    {'name': 'Account 3', 'currency': 'CHF', 'balance': 0.0, 'description': ''},
]


class TransactionModelCase(unittest.TestCase):

    def setUp(self):
        # Use in-memory SQLite database
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()
        self.create_default_categories()
        self.create_default_accounts()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_add_remove_transactions(self):

        a1 = Account.query.filter_by(name="Account 1").first()
        a2 = Account.query.filter_by(name="Account 2").first()
        c1 = Category.query.first()
        t1 = Transaction(type=TransactionType.expense, value=50.0, currency="€")
        t2 = Transaction(type=TransactionType.transfer, value=50.0, value_alt=50.0, currency="€", currency_alt="€")

        db.session.add(a1)
        db.session.add(a2)
        db.session.add(c1)
        db.session.commit()

        a1.add_transaction(t1)
        self.assertEqual(a1.balance, -50.0)
        self.assertIn(t1, a1.transactions_from.all())
        a1.add_transaction(t2, to_account=a2)
        self.assertEqual(a1.balance, -100.0)
        self.assertIn(t2, a1.transactions_from.all())
        self.assertEqual(a2.balance, 50.0)
        self.assertIn(t2, a2.transactions_to.all())
        a1.remove_transaction(t1)
        self.assertEqual(a1.balance, -50.0)
        self.assertNotIn(t1, a1.transactions_from.all())
        a1.remove_transaction(t2)
        self.assertEqual(a1.balance, 0.0)
        self.assertNotIn(t2, a1.transactions_from.all())
        self.assertEqual(a2.balance, 0.0)
        self.assertNotIn(t2, a2.transactions_to.all())

    def test_wrong_currency(self):
        a1 = Account.query.filter_by(name="Account 1").first()
        t1 = Transaction(type=TransactionType.expense, value=50.0, currency="CHF")
        db.session.add(a1)
        with self.assertRaises(RuntimeError) as _:
            a1.add_transaction(t1)

    @staticmethod
    def create_default_categories():
        for name in DEFAULT_CATEGORIES:
            category = Category(name=name)
            db.session.add(category)
        db.session.commit()

    @staticmethod
    def create_default_accounts():
        for a in DEFAULT_ACCOUNTS:
            account = Account(name=a['name'], currency=a['currency'],
                              balance=a['balance'], description=a['description'])
            db.session.add(account)
        db.session.commit()


if __name__ == '__main__':
    unittest.main(verbosity=2)

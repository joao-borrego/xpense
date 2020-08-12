import unittest
from app import create_app, db
from app.models import Transaction, TransactionType, Account
from config import Config

ACCOUNTS = [
    {'name': 'Account 1', 'currency': 'EUR', 'balance': 0.0, },
    {'name': 'Account 2', 'currency': 'EUR', 'balance': 0.0, },
    {'name': 'Category 1', 'currency': 'EUR', 'balance': 0.0, 'is_category': True},
]


class TestConfig(Config):
    TESTING = True
    # Use in-memory SQLite database
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


class TransactionModelCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.create_accounts()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_add_remove_transactions(self):

        a1 = Account.query.filter_by(name="Account 1").first()
        a2 = Account.query.filter_by(name="Account 2").first()
        c1 = Account.query.filter_by(name="Category 1").first()
        t1 = Transaction(type=TransactionType.expense,
                         value_src=50.0, currency_src="EUR", value_dest=50.0, currency_dest="EUR")
        t2 = Transaction(type=TransactionType.transfer,
                         value_src=50.0, currency_src="EUR", value_dest=50.0, currency_dest="EUR")
        db.session.add(a1)
        db.session.add(a2)
        db.session.add(c1)
        db.session.commit()

        a1.add_transaction(t1, dest_account=c1)
        self.assertEqual(a1.balance, -50.0)
        self.assertIn(t1, a1.transactions_from.all())
        a1.add_transaction(t2, dest_account=a2)
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
        t1 = Transaction(type=TransactionType.expense, value_src=50.0, currency_src="CHF")
        c1 = Account.query.filter_by(name="Category 1").first()
        db.session.add(a1)
        with self.assertRaises(RuntimeError) as _:
            a1.add_transaction(t1, dest_account=c1)

    @staticmethod
    def create_accounts():
        for a in ACCOUNTS:
            account = Account(**a)
            db.session.add(account)
        db.session.commit()


if __name__ == '__main__':
    unittest.main(verbosity=2)

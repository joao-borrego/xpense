import enum
from datetime import datetime
from hashlib import md5

from app import db


class TransactionType(enum.Enum):
    expense = 1
    income = 2
    transfer = 3


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Enum(TransactionType), nullable=False)
    datetime = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    from_account_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    to_account_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    # Value in account currency
    value = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(5), default="€")
    # Value before converting to account currency
    value_alt = db.Column(db.Float)
    currency_alt = db.Column(db.String(5))
    # TODO Maybe convert to generic tags?
    where = db.Column(db.String(50))
    description = db.Column(db.String(140))

    def __repr__(self):
        if self.type == TransactionType.transfer:
            return f"<{self.type} {self.datetime} {self.value} {self.currency} to {self.to_account}>"
        return f"<{self.type} {self.datetime} {self.value} {self.currency}>"


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String(140))
    balance = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(5), default="€")
    # Transactions from this account
    transactions_from =\
        db.relationship('Transaction', backref='from_account', lazy='dynamic',
                        foreign_keys='Transaction.from_account_id')
    # Transactions to this account
    transactions_to =\
        db.relationship('Transaction', backref='to_account', lazy='dynamic',
                        foreign_keys='Transaction.to_account_id')

    def __repr__(self):
        return f'<Account {self.name}: {self.balance} {self.currency}>'

    def check_same_currency(self, transaction: Transaction):
        """Checks if transaction has the correct currency"""
        if transaction.currency != self.currency:
            raise RuntimeError(f"Incorrect currency: "
                               f"{transaction.currency}, expected {self.currency}")

    def add_transaction(self, transaction: Transaction, to_account: "Account" = None):
        self.check_same_currency(transaction)
        if transaction.type == TransactionType.expense:
            self.balance -= transaction.value
        elif transaction.type == TransactionType.income:
            self.balance += transaction.value
        elif transaction.type == TransactionType.transfer:
            if to_account is None:
                raise RuntimeError("No destination account provided")
            if transaction.currency_alt != to_account.currency:
                raise RuntimeError(f"Incorrect currency at destination: "
                                   f"{transaction.currency}, expected {to_account.currency}")
            self.balance -= transaction.value
            to_account.balance += transaction.value_alt
            to_account.transactions_to.append(transaction)

        self.transactions_from.append(transaction)
        db.session.commit()

    def remove_transaction(self, transaction: Transaction):
        self.check_same_currency(transaction)
        if transaction.type == TransactionType.expense:
            self.balance += transaction.value
        elif transaction.type == TransactionType.income:
            self.balance -= transaction.value
        elif transaction.type == TransactionType.transfer:
            self.balance += transaction.value
            print(self.balance)
            to_account = transaction.to_account
            to_account.balance -= transaction.value_alt
            to_account.transactions_to.remove(transaction)
        self.transactions_from.remove(transaction)
        db.session.commit()


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String(140))
    icon = db.Column(db.String(140))

    def __repr__(self):
        return f'<Category {self.name}>'

    def get_icon(self, size: int = 50):
        digest = md5(self.name.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

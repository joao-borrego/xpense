import enum
from datetime import datetime
from hashlib import md5
from app import db


class TransactionType(enum.Enum):
    expense = 1
    income = 2
    transfer = 3

    @staticmethod
    def from_str(label):
        if label in ('expense', 'Expenses'):
            return TransactionType.expense
        elif label in ('income', 'Income'):
            return TransactionType.income
        elif label in ('transfer', 'Transfer'):
            return TransactionType.transfer
        else:
            raise NotImplementedError


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Enum(TransactionType), nullable=False)
    datetime = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    src_account_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    dest_account_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    # Value in source account currency
    value_src = db.Column(db.Float, nullable=False)
    currency_src = db.Column(db.String(5), default="EUR")
    # Value in destination account currency
    value_dest = db.Column(db.Float, nullable=False)
    currency_dest = db.Column(db.String(5), default="EUR")
    # TODO Maybe convert to generic tags?
    where = db.Column(db.String(50))
    description = db.Column(db.String(140))

    def __repr__(self):
        if self.type != TransactionType.income:
            return f"<{self.type.name} {self.datetime} " \
                   f"{self.value_src} {self.currency_src} as {self.value_dest} {self.currency_dest} " \
                   f"from {self.src_account} to {self.dest_account}: {self.description}>"
        return f"<{self.type.name} {self.datetime} {self.value_src} {self.currency_src}:" \
               f"{self.description} @ {self.where}>"


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String(140))
    balance = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(5), default="EUR")
    is_category = db.Column(db.Boolean, default=False)
    icon = db.Column(db.String(140))

    # Transactions from this account
    transactions_from =\
        db.relationship('Transaction', backref='src_account', lazy='dynamic',
                        foreign_keys='Transaction.src_account_id')
    # Transactions to this account
    transactions_to =\
        db.relationship('Transaction', backref='dest_account', lazy='dynamic',
                        foreign_keys='Transaction.dest_account_id')

    def __repr__(self):
        return f'<Account {self.name}: {self.balance:.2f} {self.currency}>'

    def check_valid_currency(self, transaction: Transaction, dest_account: "Account" = None):
        """Checks if transaction has the correct currency"""
        if transaction.type == TransactionType.income:
            if transaction.currency_dest != self.currency:
                raise RuntimeError(f"Incorrect currency at destination: "
                                   f"{transaction.currency_dest}, expected {self.currency}")
        elif transaction.type in (TransactionType.expense, TransactionType.transfer):
            if dest_account is None:
                raise RuntimeError("No destination account provided")
            if transaction.currency_dest != dest_account.currency:
                raise RuntimeError(f"Incorrect currency at destination: "
                                   f"{transaction.currency_dest}, expected {dest_account.currency}")
            if transaction.currency_src != self.currency:
                raise RuntimeError(f"Incorrect currency at source: "
                                   f"{transaction.currency_src}, expected {self.currency}")

    def add_transaction(self, transaction: Transaction, dest_account: "Account" = None):
        """Associates a transaction with respective accounts

        Should be used as follows
        `src_account.add_transaction(expense, dest_category)`
        `src_account.add_transaction(transfer, dest_account)`
        `dest_account.add_transaction(income)`
        """
        self.check_valid_currency(transaction, dest_account)
        if transaction.type == TransactionType.income:
            self.balance += transaction.value_dest
            self.transactions_to.append(transaction)
        elif transaction.type in (TransactionType.expense, TransactionType.transfer):
            self.balance -= transaction.value_src
            dest_account.balance += transaction.value_dest
            dest_account.transactions_to.append(transaction)
            self.transactions_from.append(transaction)
        db.session.commit()

    def remove_transaction(self, transaction: Transaction):
        """Removes the association of a transaction with respective accounts

        Should be used as follows
        `src_account.remove_transaction(expense/transfer)`
        `dest_account.remove_transaction(income)`
        """
        dest_account = transaction.dest_account
        self.check_valid_currency(transaction, dest_account)
        if transaction.type == TransactionType.income:
            self.balance -= transaction.value_dest
            self.transactions_to.remove(transaction)
        elif transaction.type in (TransactionType.expense, TransactionType.transfer):
            self.balance += transaction.value_src
            dest_account.balance -= transaction.value_dest
            dest_account.transactions_to.remove(transaction)
            self.transactions_from.remove(transaction)
        db.session.commit()

    def get_icon(self, size: int = 50):
        if not self.icon:
            digest = md5(self.name.lower().encode('utf-8')).hexdigest()
            self.icon = f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'
            db.session.commit()
        return self.icon

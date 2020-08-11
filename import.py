import csv
from datetime import datetime
from typing import Dict, List, Tuple

from app import app, db
from app.models import Transaction, TransactionType, Account


def main():

    #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    db.drop_all()
    db.create_all()

    csv_file = '/home/borrego/Downloads/avz_export.csv'
    dict_list = to_dict(csv_file)
    for entry in dict_list:
        create_transaction(entry)

    print("\n----Accounts----\n")
    for account in Account.query.filter_by(is_category=False).order_by(Account.name.asc()):
        print(account)

    print("\n----Expense Categories----\n")
    for account in Account.query.filter_by(is_category=True).order_by(Account.name.asc()):
        print(account)

    #db.drop_all()


def extract_where(entry) -> Tuple[str, str]:
    description, _, where = entry.get('Comment').partition(" @ ")
    return description, where


def extract_participants(entry) -> Tuple[str, List[str]]:
    participants = []
    description = entry.get('Comment')
    return description, participants


def get_account(name: str, currency: str, is_category=False):
    account = Account.query.filter_by(name=name, currency=currency).first()
    if account is None:
        account = Account(name=name, currency=currency, balance=0.0, is_category=is_category)
        db.session.add(account)
        db.session.commit()
        print(f"Added {account}")
    return account


def create_transaction(entry: Dict):
    transaction_type = TransactionType.from_str(entry['Type'])

    value_src = entry.get('Source value') or entry['Amount']
    currency_src = entry.get('Source category currency') or entry['Currency']
    value_dest = entry.get('Destination value') or entry['Amount']
    currency_dest = entry.get('Destination category currency') or entry['Currency']
    description, where = extract_where(entry)
    datetime_obj = datetime.strptime(entry['Time'], '%d/%m/%Y %H:%M:%S')

    # TODO Extract participants e.g. (Person1, Person2, ...)

    t = Transaction(type=transaction_type, datetime=datetime_obj,
                    value_src=float(value_src), currency_src=currency_src,
                    value_dest=float(value_dest), currency_dest=currency_dest,
                    description=description, where=where)

    is_category = transaction_type == TransactionType.expense
    dest_account = get_account(entry['Destination'], currency_dest, is_category)
    if transaction_type != TransactionType.income:
        src_account = get_account(entry['Source'], currency_src, is_category)
        src_account.add_transaction(t, dest_account)
    else:
        dest_account.add_transaction(t)

    print(t)


def to_dict(csv_file):
    dict_list = []
    with open(csv_file, 'r', encoding="utf-8-sig") as file:
        reader = csv.DictReader(file, delimiter=';')
        for line in reader:
            dict_list.append(line)
    return dict_list


if __name__ == '__main__':
    main()

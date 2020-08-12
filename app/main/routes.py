from datetime import datetime
from typing import List

from flask import render_template, request, url_for, current_app, redirect

from app import db
from app.main import bp
from app.main.forms import AddExpenseForm
from app.models import Account, Transaction, TransactionType


def get_all_accounts() -> List[Account]:
    return Account.query.filter_by(is_category=False).order_by(Account.name.asc())


def get_all_categories() -> List[Account]:
    return Account.query.filter_by(is_category=True).order_by(Account.name.asc())


@bp.route('/')
@bp.route('/index')
def index():
    page = request.args.get('page', 1, type=int)
    transactions = Transaction.query.order_by(Transaction.datetime.desc()).paginate(
        page, current_app.config['TRANSACTIONS_PER_PAGE'], False)
    next_url = url_for('main.index', page=transactions.next_num) \
        if transactions.has_next else None
    prev_url = url_for('main.index', page=transactions.prev_num) \
        if transactions.has_prev else None
    return render_template('index.html', title='Home', transactions=transactions.items,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/accounts')
def view_accounts():
    accounts = get_all_accounts()
    categories = get_all_categories()
    return render_template('accounts.html', title='Accounts', accounts=accounts, categories=categories)


@bp.route('/add/expense', methods=['GET', 'POST'])
def add_expense():
    form = AddExpenseForm()
    accounts = get_all_accounts()
    categories = get_all_categories()
    form.src_account.choices = [a.name for a in accounts]
    form.dest_account.choices = [c.name for c in categories]

    if form.validate_on_submit():
        account = Account.query.filter_by(name=form.src_account.data).first()
        category = Account.query.filter_by(name=form.dest_account.data).first()
        transaction = Transaction(
            type=TransactionType.expense, datetime=form.datetime.data,
            value_src=float(form.value_src.data), currency_src=account.currency,
            value_dest=float(form.value_dest.data), currency_dest=category.currency,
            description=form.description.data, where=form.where.data
        )
        account.add_transaction(transaction=transaction, dest_account=category)
        db.session.commit()
        return redirect(url_for('main.index'))

    form.src_account.data = accounts[0].name
    form.dest_account.data = categories[0].name
    return render_template('add_expense.html', title='Add expense', form=form)

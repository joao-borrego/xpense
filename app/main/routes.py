from typing import List

from flask import render_template, request, url_for, current_app, redirect

from app import db
from app.main import bp
from app.main.forms import AddExpenseForm, AddTransferForm, AddIncomeForm, EmptyForm
from app.models import Account, Transaction, TransactionType


def get_all_accounts() -> List[Account]:
    return Account.query.filter_by(is_category=False).order_by(Account.name.asc())


def get_all_categories() -> List[Account]:
    return Account.query.filter_by(is_category=True).order_by(Account.name.asc())


@bp.route('/')
@bp.route('/index')
def index():
    form = EmptyForm()
    page = request.args.get('page', 1, type=int)
    transactions = Transaction.query.order_by(Transaction.datetime.desc()).paginate(
        page, current_app.config['TRANSACTIONS_PER_PAGE'], False)
    next_url = url_for('main.index', page=transactions.next_num) \
        if transactions.has_next else None
    prev_url = url_for('main.index', page=transactions.prev_num) \
        if transactions.has_prev else None
    return render_template('index.html', title='Home', transactions=transactions.items,
                           next_url=next_url, prev_url=prev_url, form=form)


@bp.route('/accounts')
def view_accounts():
    accounts = get_all_accounts()
    categories = get_all_categories()
    return render_template('accounts.html', title='Accounts', accounts=accounts, categories=categories)


@bp.route('/account/<id>')
def view_account(id):
    account = Account.query.filter_by(id=id).first()
    transactions = account.transactions_cur_month()
    return render_template('account.html', title='Account', account=account, transactions=transactions)


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


@bp.route('/add/transfer', methods=['GET', 'POST'])
def add_transfer():
    form = AddTransferForm()
    accounts = get_all_accounts()
    categories = get_all_categories()
    form.src_account.choices = form.dest_account.choices = [a.name for a in accounts]

    if form.validate_on_submit():
        src_account = Account.query.filter_by(name=form.src_account.data).first()
        dest_account = Account.query.filter_by(name=form.dest_account.data).first()
        transaction = Transaction(
            type=TransactionType.transfer, datetime=form.datetime.data,
            value_src=float(form.value_src.data), currency_src=src_account.currency,
            value_dest=float(form.value_dest.data), currency_dest=dest_account.currency,
            description=form.description.data, where=form.where.data
        )
        src_account.add_transaction(transaction=transaction, dest_account=dest_account)
        db.session.commit()
        return redirect(url_for('main.index'))

    form.src_account.data = accounts[0].name
    form.dest_account.data = categories[0].name
    return render_template('add_transfer.html', title='Add expense', form=form)


@bp.route('/add/income', methods=['GET', 'POST'])
def add_income():
    form = AddIncomeForm()
    accounts = get_all_accounts()
    form.dest_account.choices = [a.name for a in accounts]

    if form.validate_on_submit():
        dest_account = Account.query.filter_by(name=form.dest_account.data).first()
        transaction = Transaction(
            type=TransactionType.income, datetime=form.datetime.data,
            value_src=float(form.value_src.data), currency_src=dest_account.currency,
            value_dest=float(form.value_dest.data), currency_dest=dest_account.currency,
            description=form.description.data, where=form.where.data
        )
        dest_account.add_transaction(transaction=transaction)
        db.session.commit()
        return redirect(url_for('main.index'))

    form.dest_account.data = accounts[0].name
    return render_template('add_income.html', title='Add expense', form=form)


@bp.route('/transaction/remove/<id>', methods=['POST'])
def remove_transaction(id):
    form = EmptyForm()
    if form.validate_on_submit():
        transaction = Transaction.query.filter_by(id=id).first()
        if not transaction:
            return redirect(url_for('main.index'))
        if transaction.type == TransactionType.income:
            transaction.dest_account.remove_transaction(transaction)
        else:
            transaction.src_account.remove_transaction(transaction)

    return redirect(url_for('main.index'))


@bp.route('/transaction/edit/<id>', methods=['POST'])
def edit_transaction(id):
    return redirect(url_for('main.index'))


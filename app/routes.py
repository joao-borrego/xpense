from flask import render_template, request, url_for

from app import app
from app.models import Transaction


@app.route('/')
@app.route('/index')
def index():
    page = request.args.get('page', 1, type=int)
    transactions = Transaction.query.order_by(Transaction.datetime.desc()).paginate(
        page, app.config['TRANSACTIONS_PER_PAGE'], False)
    next_url = url_for('index', page=transactions.next_num) \
        if transactions.has_next else None
    prev_url = url_for('index', page=transactions.prev_num) \
        if transactions.has_prev else None
    return render_template('index.html', title='Home', transactions=transactions.items,
                           next_url=next_url, prev_url=prev_url)

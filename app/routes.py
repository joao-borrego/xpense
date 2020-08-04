from flask import render_template
from app import app


@app.route('/')
@app.route('/index')
def index():
    transactions = [
        {
            'timestamp': '2020-08-04T09:25:34Z',
            'value': 5.0,
            'currency': 'Fr',
            'description': 'Ice Cream',
        },
        {
            'timestamp': '2020-08-04T09:25:34Z',
            'value': 25.0,
            'currency': 'Eur',
            'description': 'Fondue',
            'where': 'Refuge Florimont'
        }
    ]
    return render_template('index.html', title='Home', transactions=transactions)

from app import create_app, db
from app.models import Transaction, TransactionType, Account


app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Transaction': Transaction,
        'TransactionType': TransactionType,
        'Account': Account,
    }

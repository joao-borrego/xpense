from app import app, db
from app.models import Transaction, TransactionType, Account, Category


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Transaction': Transaction,
        'TransactionType': TransactionType,
        'Account': Account,
        'Category': Category,
    }

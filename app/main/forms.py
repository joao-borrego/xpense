from flask_wtf import FlaskForm
from wtforms import SelectField, DecimalField, StringField, TextAreaField, SubmitField, DateTimeField


class AddExpenseForm(FlaskForm):
    src_account = SelectField('Source Account')
    dest_account = SelectField('Category')
    value_src = DecimalField('Source value')
    value_dest = DecimalField('Destination value')
    description = TextAreaField('Description')
    where = StringField('Where')
    datetime = DateTimeField('When', format='%Y/%m/%d %H:%M:%S')
    submit = SubmitField('Add Expense')

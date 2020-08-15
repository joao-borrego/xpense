from flask_wtf import FlaskForm
from wtforms import SelectField, DecimalField, StringField, TextAreaField, SubmitField, DateTimeField
from wtforms.validators import DataRequired

from flask import request


class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')


class SearchForm(FlaskForm):
    q = StringField('Search', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)


# TODO: Reduce number of forms, somewhat redundant?

class AddExpenseForm(FlaskForm):
    src_account = SelectField('Source Account')
    dest_account = SelectField('Category')
    value_src = DecimalField('Source value')
    value_dest = DecimalField('Destination value')
    description = TextAreaField('Description')
    where = StringField('Where')
    datetime = DateTimeField('When', format='%Y/%m/%d %H:%M:%S')
    submit = SubmitField('Add Expense')


class AddTransferForm(FlaskForm):
    src_account = SelectField('Source Account')
    dest_account = SelectField('Destination Account')
    value_src = DecimalField('Source value')
    value_dest = DecimalField('Destination value')
    description = TextAreaField('Description')
    where = StringField('Where')
    datetime = DateTimeField('When', format='%Y/%m/%d %H:%M:%S')
    submit = SubmitField('Add Transfer')


class AddIncomeForm(FlaskForm):
    dest_account = SelectField('Destination Account')
    value_src = DecimalField('Source value')
    value_dest = DecimalField('Destination value')
    description = TextAreaField('Description')
    where = StringField('Where')
    datetime = DateTimeField('When', format='%Y/%m/%d %H:%M:%S')
    submit = SubmitField('Add Transfer')

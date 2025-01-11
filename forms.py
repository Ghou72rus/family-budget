from flask_wtf import FlaskForm
from wtforms import FloatField, SelectField, TextAreaField, DateField
from wtforms.validators import DataRequired

class TransactionForm(FlaskForm):
    amount = FloatField('Сумма', validators=[DataRequired()])
    transaction_type = SelectField('Тип', choices=[('income', 'Доход'), ('expense', 'Расход')], validators=[DataRequired()])
    description = TextAreaField('Описание')
    date = DateField('Дата')
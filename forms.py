from flask_wtf import FlaskForm
from wtforms import FloatField, SelectField, TextAreaField, DateField, StringField
from wtforms.validators import DataRequired

class TransactionForm(FlaskForm):
    amount = FloatField('Сумма', validators=[DataRequired()])
    transaction_type = SelectField('Тип', choices=[('income', 'Доход'), ('expense', 'Расход')], validators=[DataRequired()])
    description = TextAreaField('Описание')
    date = DateField('Дата')

class ReportForm(FlaskForm):
    start_date = DateField('Начальная дата', validators=[DataRequired()])
    end_date = DateField('Конечная дата', validators=[DataRequired()])
    category = StringField('Категория', validators=[DataRequired()])
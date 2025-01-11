from flask_wtf import FlaskForm
from wtforms import FloatField, SelectField, TextAreaField, DateField, StringField, IntegerField
from wtforms.validators import DataRequired
from wtforms_sqlalchemy.fields import QuerySelectField
from models import FamilyMember


def family_query():
    return FamilyMember.query


def get_member_label(member):
    return member.name


class TransactionForm(FlaskForm):
    amount = FloatField('Сумма', validators=[DataRequired()])
    transaction_type = SelectField('Тип', choices=[('income', 'Доход'), ('expense', 'Расход')],
                                   validators=[DataRequired()])
    description = TextAreaField('Описание')
    date = DateField('Дата')
    member_id = QuerySelectField('Член семьи', query_factory=family_query, allow_blank=True, get_label=get_member_label)


class ReportForm(FlaskForm):
    start_date = DateField('Начальная дата', validators=[DataRequired()])
    end_date = DateField('Конечная дата', validators=[DataRequired()])
    category = StringField('Категория', validators=[DataRequired()])


class GoalForm(FlaskForm):
    name = StringField('Название цели', validators=[DataRequired()])
    target_amount = FloatField('Необходимая сумма', validators=[DataRequired()])


class FamilyMemberForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])

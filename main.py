import os
from flask import Flask, render_template, redirect, url_for, request, make_response
from flask_sqlalchemy import SQLAlchemy
from forms import TransactionForm, ReportForm
from models import Transaction, db
from dotenv import load_dotenv
import plotly.graph_objects as go
import json
import datetime
import plotly.utils
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle
from io import BytesIO
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL") or 'sqlite:///' + os.path.join(basedir,
                                                                                                      'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/', methods=['GET', 'POST'])
def index():
    form = TransactionForm()
    report_form = ReportForm()

    if form.validate_on_submit():
        transaction = Transaction(
            amount=form.amount.data,
            transaction_type=form.transaction_type.data,
            description=form.description.data,
            date=form.date.data if form.date.data else datetime.date.today()
        )
        db.session.add(transaction)
        db.session.commit()
        return redirect(url_for('index'))

    transactions = Transaction.query.order_by(Transaction.date.desc()).all()
    balance = sum([t.amount if t.transaction_type == 'income' else -t.amount for t in transactions])

    # Подготовка данных для графика
    dates = [t.date.strftime('%Y-%m-%d') for t in transactions]
    amounts = [t.amount if t.transaction_type == 'income' else -t.amount for t in transactions]
    balance_over_time = []
    current_balance = 0

    for amount in amounts:
        current_balance += amount
        balance_over_time.append(current_balance)

    # Создаем график
    fig = go.Figure(data=[go.Scatter(x=dates, y=balance_over_time, mode='lines+markers',
                                     marker=dict(size=8, color='#007bff'),
                                     line=dict(color='#007bff', width=2))])

    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color="white",
        xaxis=dict(showgrid=True, gridcolor='#444'),
        yaxis=dict(showgrid=True, gridcolor='#444'),
        margin=dict(l=20, r=20, t=20, b=20)
    )
    graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('index.html', form=form, transactions=transactions, balance=balance, graph_json=graph_json,
                           report_form=report_form)


@app.route('/delete/<int:transaction_id>', methods=['POST'])
def delete_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    db.session.delete(transaction)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/report', methods=['POST'])
def generate_report():
    report_form = ReportForm()
    if report_form.validate_on_submit():
        start_date = report_form.start_date.data
        end_date = report_form.end_date.data
        category = report_form.category.data

        transactions = Transaction.query.filter(
            Transaction.description.contains(category),
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).order_by(Transaction.date).all()

        if not transactions:
            return render_template('no_report.html', report_form=report_form)

        return create_pdf_report(transactions, start_date, end_date, category)
    return redirect(url_for('index'))


def create_pdf_report(transactions, start_date, end_date, category):
    buffer = BytesIO()  # Создаем объект BytesIO для хранения PDF в памяти
    pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))  # Регистрация шрифта
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        name='CustomTitle',
        parent=styles['h1'],
        fontName='Arial',  # Используем шрифт Arial для заголовка
        alignment=TA_CENTER  # Выравнивание по центру
    )

    desc_style = ParagraphStyle(
        name='CustomNormal',
        parent=styles['Normal'],
        fontName='Arial',  # Используем шрифт Arial для текста
        fontSize=10
    )

    story = []

    title = Paragraph(f"Отчет по категории '{category}' за период {start_date} - {end_date}", title_style)
    story.append(title)

    data = [["Дата", "Тип", "Сумма", "Описание"]]
    total_amount = 0
    for transaction in transactions:
        amount = transaction.amount
        if transaction.transaction_type == 'expense':
            amount = abs(amount)  # Модуль для расходов
            total_amount -= transaction.amount
            amount_str = f"{amount}"
        else:
            total_amount += transaction.amount
            amount_str = f"{amount}"

        data.append([
            transaction.date,
            'Доход' if transaction.transaction_type == 'income' else 'Расход',
            amount_str,
            transaction.description,
        ])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Arial'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(table)

    total_str = f"Общая сумма: {abs(total_amount)} руб."
    p = Paragraph(total_str, desc_style)
    story.append(p)

    doc.build(story)

    buffer.seek(0)  # Перемещаем указатель на начало буфера
    response = make_response(buffer.read())  # Записываем байтовый поток
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=report.pdf'

    return response


if __name__ == '__main__':
    app.run(debug=True)
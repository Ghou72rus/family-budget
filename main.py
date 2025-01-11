import os
from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from forms import TransactionForm
from models import Transaction, db
from dotenv import load_dotenv
import plotly.graph_objects as go
import json
import datetime
import plotly.utils


load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL") or 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/', methods=['GET', 'POST'])
def index():
    form = TransactionForm()
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

    return render_template('index.html', form=form, transactions=transactions, balance=balance, graph_json=graph_json)


@app.route('/delete/<int:transaction_id>', methods=['POST'])
def delete_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    db.session.delete(transaction)
    db.session.commit()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='192.168.0.148', port=5050)
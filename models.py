from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False)
    description = db.Column(db.String(200))
    date = db.Column(db.Date, default=date.today())

    def __repr__(self):
        return f"<Transaction {self.id}>"

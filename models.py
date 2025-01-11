from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False)
    description = db.Column(db.String(200))
    date = db.Column(db.Date, default=date.today())
    member_id = db.Column(db.Integer, db.ForeignKey('family_member.id'), nullable=True)

    def __repr__(self):
        return f"<Transaction {self.id}>"


class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0)

    def __repr__(self):
        return f"<Goal {self.id}>"


class FamilyMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<FamilyMember {self.id}>"

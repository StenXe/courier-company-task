from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Sender(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50))
    street_address = db.Column(db.String(100))
    city = db.Column(db.String(20))
    country_code = db.Column(db.String(3))

class Recipient(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50))
    street_address = db.Column(db.String(100))
    city = db.Column(db.String(20))
    country_code = db.Column(db.String(3))

class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('sender.id', ondelete="CASCADE"))
    recipient_id = db.Column(db.Integer, db.ForeignKey('recipient.id', ondelete="CASCADE"))
    value = db.Column(db.Float)
    despatch_date = db.Column(db.DateTime)
    contents_declaration = db.Column(db.String(50))
    insurance_required = db.Column(db.Boolean)
    tracking_reference = db.Column(db.String(50))
    order_url = db.Column(db.String(100))
    accepted_at = db.Column(db.DateTime)
    insurance_provided = db.Column(db.Boolean)
    total_insurance_charge = db.Column(db.Float)
    ipt_included_in_charge = db.Column(db.Float)

class Country(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    country_name = db.Column(db.String(50))
    country_code = db.Column(db.String(3))

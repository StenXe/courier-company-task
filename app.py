from flask import Flask, request, render_template, jsonify, make_response, redirect
from flask_pydantic import validate
from order_models import OrderRequest, OrderResponse
from datetime import date, datetime
from models import db, Sender, Recipient, Orders, Country
import os
import pandas as pd


app = Flask(__name__)                                                           #initialize flask application
secret_key = os.urandom(16)                                                     #generate random secret key

app.config['SECRET_KEY'] = secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./database/database.db'      #SQLITE as database
app.config['DEBUG'] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.app_context().push()
db.create_all()                                                                 #create all the database tables

df = pd.read_csv('./static/country_codes.csv')                                  #import csv for country and code mapping
df.to_sql('country', con=db.get_engine(), index_label='id', if_exists='replace')#populate the table

@app.route('/')
def home():
    return redirect('orders')                                                   #redirect home page requests to /orders

#GET requested order and return in JSON (commented) or as a Jinja template
@app.route('/orders/<int:order_id>/', methods=['GET'])
def get_order(order_id):
    order = Orders.query.get_or_404(order_id)
    sender = Sender.query.get_or_404(order.sender_id)
    recipient = Recipient.query.get_or_404(order.recipient_id)

    # return {'value': order.value, 'contents_declaration': order.contents_declaration, 'tracking_reference': order.tracking_reference}
    return render_template('view_order.html', order=order, sender=sender, recipient=recipient, title='View Order')

#GET route to facilitate new order submission
@app.route('/orders/', methods=['GET'])
def create_order():
    country_codes = Country.query.all()

    return render_template('create_order.html', country_codes=country_codes, title='Get Insurance')

#PUT method processes the request via browser or JSON Request
@app.route('/orders/', methods=['PUT'])
@validate()
def process_order(body: OrderRequest):

    order_value = float(body.value)
    track_num_exists = Orders.query.filter_by(tracking_reference=body.tracking_reference).first() is not None
    num_days = (body.despatch_date - date.today()).days
    insurance_provided = False
    order_url = ''
    accepted_at = ''
    insc_chrg = 0
    ipt_included_in_charge = 0

    if(body.insurance_required and order_value<=10000 and num_days in (0, 1) and not track_num_exists):
        accepted_at = datetime.today()
        insurance_provided = True
        order_url = 'url'
        if(body.recipient['country_code'] == 'GB'):
            insc_chrg = 0.01 * order_value
        elif(body.recipient['country_code'] in ('FR', 'DE', 'NL', 'BE')):
            insc_chrg = 0.015 * order_value
        else:
            insc_chrg = 0.04 * order_value
        insc_chrg = max(round(insc_chrg, 2), 9)
        ipt_included_in_charge = round(insc_chrg - insc_chrg / 1.12, 2)

        sender = Sender(name=body.sender['name'],
                        street_address=body.sender['street_address'],
                        city=body.sender['city'],
                        country_code=body.sender['country_code'])
        db.session.add(sender)

        recipient = Recipient(name=body.recipient['name'],
                        street_address=body.recipient['street_address'],
                        city=body.recipient['city'],
                        country_code=body.recipient['country_code'])
        db.session.add(recipient)
        db.session.commit()

        order = Orders(sender_id=sender.id,
                        recipient_id=recipient.id,
                        value=body.value,
                        despatch_date=body.despatch_date,
                        contents_declaration=body.contents_declaration,
                        insurance_required=body.insurance_required,
                        tracking_reference=body.tracking_reference,
                        order_url='',
                        accepted_at=accepted_at,
                        insurance_provided=insurance_provided,
                        total_insurance_charge=insc_chrg,
                        ipt_included_in_charge=ipt_included_in_charge)
        db.session.add(order)
        db.session.commit()

        update_order = Orders.query.filter_by(id=order.id).first()
        update_order.order_url = request.host_url + 'orders/' + str(update_order.id)
        db.session.add(update_order)
        db.session.commit()

        order_url = update_order.order_url
    else:
        reason = ''
        if(not body.insurance_required):
            reason = 'Insurance not required.'
        elif(order_value>10000):
            reason = 'Order value more than £10,000.'
        elif(num_days not in (0, 1)):
            reason = 'Order Despatch Date is not today or tomorrow.'
        elif(track_num_exists):
            reason = 'Tracking Reference already exists.'

        response = {'message': f'Order not processed. {reason}', 'code':'ERROR'}
        return make_response(jsonify(response), 406)

    return OrderResponse(package=body,
                        order_url=order_url,
                        accepted_at=accepted_at,
                        insurance_provided=insurance_provided,
                        total_insurance_charge=insc_chrg,
                        ipt_included_in_charge=ipt_included_in_charge)

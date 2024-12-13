from flask import jsonify, request
from structure.models import TelAfricSubscribers, Payment, CallLog,User, Rate
from flask import render_template, Blueprint, session, redirect, url_for, jsonify, current_app, request ,send_file
import random
from flask_sqlalchemy import SQLAlchemy
from structure import db,mail ,photos,app
from flask_login import current_user
import requests
import uuid
from urllib.parse import unquote
import os
from datetime import datetime
telafric = Blueprint('telafric', __name__)

# ... existing code ...

@telafric.route('/api/validate_subscriber', methods=['POST','GET'])
def validate_subscriber():
    # Get phone number from query parameters
    phone_number = request.args.get('phone_number')

    if not phone_number:
        return jsonify(False), 400  # Return False with a 400 status code if phone number is missing

    subscriber = User.query.filter_by(phone_number=phone_number).first()
    if subscriber:
        return jsonify(True), 200  # Return True with a 200 status code if subscriber exists
    return jsonify(False), 404  # Return False with a 404 status code if subscriber does not exist

@telafric.route('/api/validate_pin', methods=['POST', 'GET'])
def validate_pin():
    phone_number = request.args.get('phone_number')
    pin_code = request.args.get('pin_code')
    
    subscriber = User.query.filter_by(phone_number=phone_number, pin_code=pin_code).first()
    if subscriber:
        return jsonify(True), 200  # Return true if subscriber exists
    return jsonify(False), 200  # Return false if subscriber does not exist

@telafric.route('/api/subscribe', methods=['POST','GET'])
def subscribe():
    # data = request.get_json()
    phone_number = request.args.get('phone_number')

    # Generate a random secure 4-digit PIN code
    pin_code = str(random.randint(1000, 9999))

    # Create a new subscriber
    new_subscriber = User(phone_number=phone_number, pin_code=pin_code)
    db.session.add(new_subscriber)
    db.session.commit()

    return jsonify({"status": True, "pin_code": pin_code}), 201
# ... existing code ...
@telafric.route('/api/delete', methods=['DELETE','GET'])
def delete_all_subscribers():
    try:
        db.session.query(User).delete()
        db.session.commit()
        return jsonify({"message": "All subscribers deleted successfully."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@telafric.route('/api/subscribers', methods=['GET'])
def get_subscribers():
    subscribers = User.query.all()
    subscriber_list = [{"phone_number": sub.phone_number, "pin_code": sub.pin_code, "balance":sub.balance} for sub in subscribers]
    return jsonify(subscriber_list), 200

@telafric.route('/api/balance', methods=['GET'])
def get_balance():
    phone_number = request.args.get('phone_number')
    print("number",phone_number)
    subscriber = User.query.filter_by(phone_number=phone_number).first()
    
    if subscriber:
        # Assuming the balance is a field in the User model
        return jsonify({"balance": subscriber.balance}), 200  # Return the balance with a 200 status code
    return jsonify({"error": "Subscriber not found"}), 404  # Return an error if subscriber does not exist


# @telafric.route('/api/bill_call', methods=['POST','GET'])
# def deduct_balance():
#     print("request.args", request.args)
#     print("request.get_json()", request.get_json())
#     data = request.get_json()
#     phone_number = request.args.get('phone_number')
#     duration = request.args.get('duration')

#     print("phone_number", phone_number)
#     print("duration", duration)

#     if not phone_number or not duration:
#         return jsonify({"error": "Missing phone number or duration"}), 400

#     subscriber = User.query.filter_by(phone_number=phone_number).first()
#     print("subscriber", subscriber)
    
#     if subscriber:
#         # Assuming the balance is a field in the User model
#         cost = float(duration) * 0.20
#         print("cost", cost)
#         if subscriber.balance >= cost:
#             print("previous balance", subscriber.balance)
#             subscriber.balance -= cost
#             db.session.commit()
#             print("new balance", subscriber.balance)
#             return jsonify({"balance": subscriber.balance}), 200  # Return the updated balance with a 200 status code
#         else:
#             return jsonify({"error": "Insufficient balance"}), 402  # Return an error if the subscriber does not have enough balance
#     return jsonify({"error": "Subscriber not found"}), 404  # Return an error if subscriber does not exist

@telafric.route('/api/bill_call', methods=['POST', 'GET'])
def deduct_balance():
    print("request.args", request.args)
    print("request.get_json()", request.get_json())
    data = request.get_json()
    phone_number = unquote(request.args.get('phone_number', ''))
    duration = request.args.get('duration')

    print("phone_number", phone_number)
    print("duration", duration)

    if not phone_number or not duration:
        return jsonify({"error": "Missing phone number or duration"}), 400

    subscriber = User.query.filter_by(phone_number=phone_number).first()
    print("subscriber", subscriber)
    
    if subscriber:
        # Find applicable rate by checking prefixes manually
        destination = data.get('destination')  # Assuming destination is passed in the request
        matching_rates = Rate.query.filter(Rate.destination_prefix == destination).all()

        if not matching_rates:
            return jsonify({"error": "No applicable rate found for this destination"}), 404

        # Get the rate per minute for the longest matching prefix
        rate = max(matching_rates, key=lambda x: len(x.destination_prefix))
        cost = float(duration) * rate.rate_per_minute  # Calculate cost based on the rate

        print("cost", cost)
        if subscriber.balance >= cost:
            print("previous balance", subscriber.balance)
            subscriber.balance -= cost
            db.session.commit()
            print("new balance", subscriber.balance)
            return jsonify({"balance": subscriber.balance}), 200  # Return the updated balance with a 200 status code
        else:
            return jsonify({"error": "Insufficient balance"}), 402  # Return an error if the subscriber does not have enough balance
    return jsonify({"error": "Subscriber not found"}), 404  # Return an error if subscriber does not exist

@telafric.route('/api/check_balance', methods=['GET'])
def check_balance():
    phone_number = request.args.get('phone_number')

    if not phone_number:
        return jsonify({"error": "Missing phone number"}), 400

    subscriber = User.query.filter_by(phone_number=phone_number).first()
    
    if subscriber:
        # Assuming the balance is a field in the User model
        return jsonify({"balance": subscriber.balance}), 200  # Return the balance with a 200 status code
    return jsonify({"error": "Subscriber not found"}), 404  # Return an error if subscriber does not exist


@telafric.route('/api/add_balance', methods=['GET'])
def add_balance():
    phone_number = request.args.get('phone_number')

    if not phone_number:
        return jsonify({"error": "Missing phone number"}), 400

    subscriber = User.query.filter_by(phone_number=phone_number).first()
    
    if subscriber:
        subscriber.balance = 20
        db.session.commit()
        return jsonify({"balance": subscriber.balance}), 200  # Return the updated balance with a 200 status code
    return jsonify({"error": "Subscriber not found"}), 404  # Return an error if subscriber does not exist


@telafric.route('/api/get_rate', methods=['GET'])
def get_rate():
    destination = request.args.get('destination')

    if not destination:
        return jsonify({"error": "Missing destination"}), 400

    # Find applicable rate by checking prefixes manually
    matching_rates = []
    all_rates = Rate.query.all()
    for rate in all_rates:
        if destination.startswith(rate.destination_prefix):
            matching_rates.append(rate)
    
    if not matching_rates:
        return jsonify({"error": "No rate found for this destination"}), 404

    # Get the longest matching prefix (most specific)
    rate = max(matching_rates, key=lambda x: len(x.destination_prefix))
    
    return jsonify({
        "rate": rate.rate_per_minute,
        "description": rate.description
    }), 200

@telafric.route('/api/rates', methods=['GET'])
def list_rates():
    if not current_user.is_authenticated:
        return jsonify({"error": "Unauthorized"}), 401
        
    rates = Rate.query.all()
    return jsonify([{
        "id": rate.id,
        "destination_prefix": rate.destination_prefix,
        "description": rate.description,
        "rate_per_minute": rate.rate_per_minute
    } for rate in rates]), 200

@telafric.route('/api/rates', methods=['POST'])
def create_rate():
    if not current_user.is_authenticated:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    
    if not all(k in data for k in ["destination_prefix", "rate_per_minute"]):
        return jsonify({"error": "Missing required fields"}), 400

    new_rate = Rate(
        destination_prefix=data["destination_prefix"],
        description=data.get("description", ""),
        rate_per_minute=float(data["rate_per_minute"])
    )
    
    db.session.add(new_rate)
    db.session.commit()
    
    return jsonify({
        "id": new_rate.id,
        "destination_prefix": new_rate.destination_prefix,
        "description": new_rate.description,
        "rate_per_minute": new_rate.rate_per_minute
    }), 201

@telafric.route('/api/rates/<int:rate_id>', methods=['PUT'])
def update_rate(rate_id):
    if not current_user.is_authenticated:
        return jsonify({"error": "Unauthorized"}), 401

    rate = Rate.query.get_or_404(rate_id)
    data = request.get_json()
    
    if "destination_prefix" in data:
        rate.destination_prefix = data["destination_prefix"]
    if "description" in data:
        rate.description = data["description"]
    if "rate_per_minute" in data:
        rate.rate_per_minute = float(data["rate_per_minute"])
    
    db.session.commit()
    
    return jsonify({
        "id": rate.id,
        "destination_prefix": rate.destination_prefix,
        "description": rate.description,
        "rate_per_minute": rate.rate_per_minute
    }), 200

@telafric.route('/api/rates/<int:rate_id>', methods=['DELETE'])
def delete_rate(rate_id):
    if not current_user.is_authenticated:
        return jsonify({"error": "Unauthorized"}), 401

    rate = Rate.query.get_or_404(rate_id)
    db.session.delete(rate)
    db.session.commit()
    
    return jsonify({"message": "Rate deleted successfully"}), 200

# Update the check_credit route to use dynamic rates
@telafric.route('/api/check_credit', methods=['GET'])
def check_credit():
    phone_number = unquote(request.args.get('phone_number', ''))
    destination = unquote(request.args.get('destination', ''))

    print(f"check_credit - Phone Number: {phone_number}")
    print(f"check_credit - Destination: {destination}")

    if not phone_number or not destination:
        print("check_credit - Missing phone number or destination")
        return jsonify({"error": "Missing phone number or destination"}), 400

    subscriber = User.query.filter_by(phone_number=phone_number).first()
    print(f"check_credit - Subscriber found: {subscriber}")
    
    if not subscriber:
        print("check_credit - Subscriber not found")
        return jsonify({"error": "Subscriber not found"}), 404

    # Find applicable rate by checking prefixes manually
    matching_rates = []
    all_rates = Rate.query.all()
    print(f"check_credit - Total Rates: {len(all_rates)}")
    
    for rate in all_rates:
        print(f"check_credit - Checking Rate: {rate.destination_prefix}")
        if destination.startswith(rate.destination_prefix):
            matching_rates.append(rate)
            print(f"check_credit - Matched Rate: {rate}")
    
    if not matching_rates:
        print("check_credit - No matching rates found")
        return jsonify({"error": "No rate found for this destination"}), 404

    # Get the longest matching prefix (most specific)
    rate = max(matching_rates, key=lambda x: len(x.destination_prefix))
    print(f"check_credit - Selected Rate: {rate}")
    
    rate_per_minute = rate.rate_per_minute
    balance = subscriber.balance

    print(f"check_credit - Rate per minute: {rate_per_minute}")
    print(f"check_credit - Current Balance: {balance}")

    if rate_per_minute > 0:
        max_duration = int(balance / (rate_per_minute / 60))
    else:
        max_duration = 0

    print(f"check_credit - Max Duration: {max_duration}")

    return jsonify({
        "balance": balance,
        "rate": rate_per_minute,
        "max_duration": max_duration,
        "description": rate.description,
        "timestamp": datetime.utcnow().isoformat()
    }), 200



@telafric.route('/api/send_sms', methods=['POST'])
def send_sms():
    print("send_sms called")
    
    data = request.get_json()
    print("data",data)
    phone_number = data.get('phone_number').strip() if data.get('phone_number') else ''
    amount = data.get('amount') 
    phone_number = unquote(phone_number)
    print("number",phone_number)
    if not phone_number:
        print("Missing phone number or amount")
        return jsonify({"error": "Missing phone number or amount"}), 400

    subscriber = User.query.filter_by(phone_number=phone_number).first()
    print("subscriber response",subscriber)
    if not subscriber:
        print("Subscriber not found")
        return jsonify({"error": "Subscriber not found"}), 404

    # Generate a unique reference for this transaction
    reference = str(uuid.uuid4())
    print("Generated reference:", reference)

    # Create Paystack payment link
    paystack_secret_key = os.environ.get('PAYSTACK_KEY')
    paystack_url = "https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {paystack_secret_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "amount": 5,
        "email": 'raymond@delaphonegh.com',  # Assuming subscriber has an email field
        "reference": reference,
        "callback_url": f"https://ids-slw6.onrender.com/api/paystack_callback/{subscriber.id}/{reference}"
    }

    print("Payload:", payload)
    paystack_response = requests.post(paystack_url, json=payload, headers=headers)
    print("Paystack response status code:", paystack_response.status_code)
    
    if paystack_response.status_code != 200:
        print("Failed to create payment link")
        return jsonify({"error": "Failed to create payment link"}), 500

    payment_link = paystack_response.json()['data']['authorization_url']

    # Send SMS with payment link
    sms_token = os.environ.get('SMS_SECRET')
    if not sms_token:
        print("Missing SMS token")
        return jsonify({"error": "Missing SMS token"}), 500

    sms_headers = {
        'Authorization': 'Bearer ' + sms_token,
        'Content-Type': 'application/json'
    }
    sms_payload = {
        "sender_id": "RaymondDLP",
        "recipients": [phone_number],
        "message": f"Follow the link to top-up: {payment_link}"
    }
    print("SMS payload:", sms_payload)
    sms_response = requests.post('https://staging.api.delaphonegh.com/v1/sms', headers=sms_headers, json=sms_payload)
    print("SMS response status code:", sms_response.content)

    if sms_response.status_code != 202:
        print("Failed to send sms")
        return jsonify({"error": "Failed to send sms"}), 500

    print("SMS sent successfully")
    return jsonify({"status": "success", "payment_link": payment_link}), 200

@telafric.route('/api/paystack_callback/<int:subscriber_id>/<string:reference>', methods=['GET', 'POST'])
def paystack_callback(subscriber_id, reference):
    print("paystack_callback triggered")
    print("Subscriber ID:", subscriber_id)
    print("Reference:", reference)
    # Verify the transaction
    paystack_secret_key = os.environ.get('PAYSTACK_KEY')
    headers = {"Authorization": f"Bearer {paystack_secret_key}"}
    response = requests.get(f"https://api.paystack.co/transaction/verify/{reference}", headers=headers)
    print("Paystack verify response:", response.status_code)
    print("Paystack verify response content:", response.content)
    if response.status_code == 200:
        transaction_data = response.json()['data']
        print("Transaction data:", transaction_data)
        if transaction_data['status'] == 'success':
            subscriber = User.query.get(subscriber_id)
            if subscriber:
                print("Subscriber found:", subscriber)
                # Update subscriber's balance
                amount_in_main_currency = transaction_data['amount'] / 100 
                print("Amount in main currency:", amount_in_main_currency)
                subscriber.balance += amount_in_main_currency
                db.session.commit()
                print("Updated subscriber balance:", subscriber.balance)
                # Save the payment to model
                payment = Payment(
                    reference=reference,
                    amount=amount_in_main_currency,
                    subscriber_id=subscriber_id
                )
                db.session.add(payment)
                db.session.commit()
                print("Payment saved to model")
                print({"status": "success", "message": "Payment successful and balance updated"})
                return render_template('telafric/paymentconfirmation.html',amount=amount_in_main_currency)
            else:
                print("Subscriber not found")
                return jsonify({"error": "Subscriber not found"}), 404
        else:
            print("Payment was not successful")
            return jsonify({"error": "Payment was not successful"}), 400
    else:
        print("Failed to verify transaction")
        return jsonify({"error": "Failed to verify transaction"}), 500




@telafric.route('/api/send_sms2', methods=['POST'])
def send_sms2():
    print("send_sms called")
    
    data = request.get_json()
    print("data",data)
    phone_number = data.get('phone_number').strip() if data.get('phone_number') else ''
    amount = data.get('amount') 
    phone_number = unquote(phone_number)
    print("number",phone_number)
    if not phone_number:
        print("Missing phone number or amount")
        return jsonify({"error": "Missing phone number or amount"}), 400

    # subscriber = User.query.filter_by(phone_number=phone_number).first()
    # print("subscriber response",subscriber)
    # if not subscriber:
    #     print("Subscriber not found")
    #     return jsonify({"error": "Subscriber not found"}), 404

    # Generate a unique reference for this transaction
    reference = str(uuid.uuid4())
    print("Generated reference:", reference)

    # Create Paystack payment link
    paystack_secret_key = os.environ.get('PAYSTACK_KEY')
    paystack_url = "https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {paystack_secret_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "amount": 5,
        "email": 'raymond@delaphonegh.com',  # Assuming subscriber has an email field
        "reference": reference,
        "callback_url": f"https://emily-zawk.onrender.com/api/paystack_callback/{subscriber.id}/{reference}"
    }

    print("Payload:", payload)
    paystack_response = requests.post(paystack_url, json=payload, headers=headers)
    print("Paystack response status code:", paystack_response.status_code)
    
    if paystack_response.status_code != 200:
        print("Failed to create payment link")
        return jsonify({"error": "Failed to create payment link"}), 500

    payment_link = paystack_response.json()['data']['authorization_url']

    # Send SMS with payment link
    sms_token = os.environ.get('SMS_SECRET')
    if not sms_token:
        print("Missing SMS token")
        return jsonify({"error": "Missing SMS token"}), 500

    sms_headers = {
        'Authorization': 'Bearer ' + sms_token,
        'Content-Type': 'application/json'
    }
    sms_payload = {
        "sender_id": "RaymondDLP",
        "recipients": [phone_number],
        "message": f"Follow the link to top-up: {payment_link}"
    }
    print("SMS payload:", sms_payload)
    sms_response = requests.post('https://staging.api.delaphonegh.com/v1/sms', headers=sms_headers, json=sms_payload)
    print("SMS response status code:", sms_response.content)

    if sms_response.status_code != 202:
        print("Failed to send sms")
        return jsonify({"error": "Failed to send sms"}), 500

    print("SMS sent successfully")
    return jsonify({"status": "success", "payment_link": payment_link}), 200

@telafric.route('/dashboard', methods=['GET'])
def dashboard():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    
    
    # Fetch call logs and payments for the current user
    call_logs = CallLog.query.filter_by(subscriber_id=current_user.id).all()
    payments = Payment.query.filter_by(subscriber_id=current_user.id).all()
    
    return render_template('ids/dashboard.html', call_logs=call_logs, payments=payments,user =current_user)

@telafric.route('/api/log_call', methods=['POST'])
def log_call():
    data = request.get_json()
    
    print("log_call - Received Data:", data)
    
    # Decode the phone number
    phone_number = unquote(data.get('phone_number'))
    destination = data.get('destination')
    duration = data.get('duration')
    
    print(f"log_call - Phone Number: {phone_number}")
    print(f"log_call - Destination: {destination}")
    print(f"log_call - Duration: {duration}")
    
    subscriber = User.query.filter_by(phone_number=phone_number).first()
    
    print(f"log_call - Subscriber found: {subscriber}")
    
    if subscriber:
        call_log = CallLog(
            phone_number=phone_number, 
            destination=destination, 
            duration=duration, 
            subscriber=subscriber  # This should work if the relationship is set correctly
        )
        db.session.add(call_log)
        db.session.commit()
        
        print("log_call - Call log saved successfully")
        return jsonify({"status": "success"}), 201
    
    print("log_call - Subscriber not found")
    return jsonify({"error": "Subscriber not found"}), 404

@telafric.route('/top_up', methods=['GET'])
def top_up():
    # PayPal sandbox URL
    paypal_url = "https://sandbox.paypal.com/cgi-bin/webscr"
    
    # PayPal parameters
    params = {
        "cmd": "_xclick",
        "business": "your-paypal-email@example.com",  # Replace with your PayPal sandbox email
        "item_name": "Top Up",
        "amount": "10.00",  # Amount to top up
        "currency_code": "USD",
        "return": url_for('telafric.paypal_callback', _external=True),  # Callback URL
        "cancel_return": url_for('telafric.dashboard', _external=True),  # Cancel URL
        "notify_url": url_for('telafric.paypal_callback', _external=True)  # IPN URL
    }
    
    # Redirect to PayPal
    return redirect(paypal_url + "?" + requests.compat.urlencode(params))

@telafric.route('/paypal_callback', methods=['GET'])
def paypal_callback():
    # Here you would handle the payment confirmation
    # For now, let's just simulate saving the payment
    # You can access the payment details via request.args
    payment_status = request.args.get('st')  # Get the payment status from PayPal
    amount = request.args.get('amt')  # Get the amount from PayPal
    payer_email = request.args.get('payer_email')  # Get payer's email

    # Save the payment to the database (you'll need to implement this)
    # payment = Payment(reference=..., amount=amount, subscriber_id=current_user.id)
    # db.session.add(payment)
    # db.session.commit()

    # flash('Payment successful! Amount: ' + amount)
    return redirect(url_for('telafric.dashboard'))

@telafric.route('/rates', methods=['GET'])
def view_rates():
    rates = Rate.query.all()  # Fetch all rates from the database
    return render_template('ids/rates.html', rates=rates)
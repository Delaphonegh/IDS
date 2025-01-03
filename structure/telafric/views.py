from flask import jsonify, request, flash
from structure.models import TelAfricSubscribers, Payment, CallLog,User, Rate
from flask import render_template, Blueprint, session, redirect, url_for, jsonify, current_app, request ,send_file
import random
from flask_sqlalchemy import SQLAlchemy
from structure import db,mail ,photos,app
from flask_login import current_user
import requests
import uuid 
from urllib.parse import unquote, urlencode
import os
from datetime import datetime
from werkzeug.security import generate_password_hash

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
    phone_number = request.args.get('phone_number')

    # Generate a random secure 4-digit PIN code
    pin_code = str(random.randint(1000, 9999))

    # Create a new subscriber
    new_subscriber = User(phone_number=phone_number, pin_code=pin_code)
    db.session.add(new_subscriber)
    db.session.commit()

    # Send welcome SMS with PIN and app information
    sms_url = "https://api.wirepick.com/httpsms/send"
    welcome_message = (
        f"Welcome to Delaphone! "
        f"Your PIN is: {pin_code}\n"
        "Visit our portal: https://ids-slw6.onrender.com/"
    )
    wirepick_key =  os.environ.get('WIREPICK_KEY')
    
    sms_params = {
        'client': 'raymond',
        'password': wirepick_key,
        'phone': phone_number,
        'text': welcome_message,
        'from': 'Delaphone'
    }
    
    try:
        sms_response = requests.get(sms_url, params=sms_params)
        print("Welcome SMS response:", sms_response.content)
        
        if sms_response.status_code != 200:
            print("Failed to send welcome SMS")
            # Note: We don't return an error here as the subscription was successful
    except Exception as e:
        print(f"Error sending welcome SMS: {str(e)}")
        # We continue even if SMS fails as the subscription was successful

    return jsonify({"status": True, "pin_code": pin_code}), 201


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
#i need to later add a check to make sure a destination is passed. Might not need to do that if i handle this in dialplan
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



@telafric.route('/api/bill_call', methods=['POST', 'GET'])
def deduct_balance():
    print("Received request for deduct_balance")
    print("Request args:", request.args)
    print("Request JSON:", request.get_json())

    # Extract parameters from request
    phone_number = unquote(request.args.get('phone_number', ''))
    duration = request.args.get('duration')
    destination = unquote(request.args.get('destination', ''))

    print("Extracted parameters:")
    print("Phone Number:", phone_number)
    print("Duration:", duration)
    print("Destination:", destination)
    # if int(duration) < 1:
    #     return jsonify({"error": "Call not billable"}), 400


    # Validate parameters
    if not phone_number or not duration or not destination:
        print("Error: Missing parameters")
        return jsonify({"error": "Missing phone number, duration, or destination"}), 400

    # Find the subscriber
    subscriber = User.query.filter_by(phone_number=phone_number).first()
    print("Subscriber found:", subscriber)

    if subscriber:
        # Find applicable rates by checking prefixes manually
        matching_rates = []
        all_rates = Rate.query.all()
        print(f"Total Rates: {len(all_rates)}")

        for rate in all_rates:
            print(f"Checking Rate: {rate.destination_prefix}")
            if destination.startswith(rate.destination_prefix):
                matching_rates.append(rate)
                print(f"Matched Rate: {rate}")

        if not matching_rates:
            print("No matching rates found")
            return jsonify({"error": "No rate found for this destination"}), 404

        # Get the longest matching prefix (most specific)
        rate = max(matching_rates, key=lambda x: len(x.destination_prefix))
        print(f"Selected Rate: {rate}")

        cost = float(duration) * rate.rate_per_minute  # Calculate cost based on the rate
        print("Calculated cost:", cost)

        if subscriber.balance >= cost:
            print("Previous balance:", subscriber.balance)
            subscriber.balance -= cost
            db.session.commit()
            print("New balance after deduction:", subscriber.balance)

            # Log the call
            call_log = CallLog(
                phone_number=phone_number,
                destination=destination,
                duration=duration,
                amount = cost,
                subscriber=subscriber  # Assuming the relationship is set correctly
            )
            db.session.add(call_log)
            db.session.commit()  # Commit the call log to the database
            print("Call logged successfully")

            return jsonify({"balance": subscriber.balance}), 200  # Return the updated balance with a 200 status code
        else:
            print("Error: Insufficient balance")
            return jsonify({"error": "Insufficient balance"}), 402  # Return an error if the subscriber does not have enough balance
    else:
        print("Error: Subscriber not found")
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
def add_rate():
    if not current_user.is_authenticated:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    
    # if not all(k in data for k in ["destination_prefix", "rate_per_minute"]):
    #     return jsonify({"error": "Missing required fields"}), 400

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

@telafric.route('/api/rates/<int:rate_id>', methods=['PUT','GET', 'POST'])
def edit_rate(rate_id):
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

@telafric.route('/api/rates/<int:rate_id>', methods=['DELETE','POST'])
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
        return jsonify({
            "status": "error",
            "error_code": "DESTINATION_NOT_SUPPORTED",
            "message": "No rate found for this destination"
        }), 404

    # Get the longest matching prefix (most specific)
    rate = max(matching_rates, key=lambda x: len(x.destination_prefix))
    print(f"check_credit - Selected Rate: {rate}")
    
    rate_per_minute = rate.rate_per_minute
    balance = subscriber.balance

    print(f"check_credit - Rate per minute: {rate_per_minute}")
    print(f"check_credit - Current Balance: {balance}")

    if rate_per_minute > 0:
        max_duration = int(balance / (rate_per_minute / 60))
        minutes, seconds = divmod(max_duration, 60)
        # minutes = max_duration // 60
        # seconds = max_duration % 60
    else:
        max_duration = 0
        minutes = 0
        seconds = 0

    print(f"check_credit - Max Duration: {max_duration}")
    print(f"check_credit - Minutes: {minutes}")
    print(f"check_credit - Seconds: {seconds}")

    return jsonify({
        "balance": balance,
        "rate": rate_per_minute,
        "max_duration": max_duration,
        "description": rate.description,
        "minutes": minutes,
        "seconds": seconds,
        "timestamp": datetime.utcnow().isoformat()
    }), 200
 

# @telafric.route('/api/get_balance', methods=['GET'])
# def get_balance():
#     phone_number = unquote(request.args.get('phone_number', ''))
#     print("getiing balance for:",phone_number)
#     # destination = unquote(request.args.get('destination', ''))

#     if not phone_number:
#         print("No phone number provided")
#         return jsonify({"error": "Missing phone number"}), 400  # Return an error if phone number is not provided

#     subscriber = User.query.filter_by(phone_number=phone_number).first()
    
    if subscriber:
        print("Balance is :",subscriber.balance)
        return jsonify({"balance": subscriber.balance}), 200  # Return the balance with a 200 status code
    return jsonify({"error": "Subscriber not found"}), 404  # Return an error if subscriber does not exist


@telafric.route('/api/send_sms', methods=['POST'])
def send_sms():
    print("send_sms called")
    
    data = request.get_json()
    print("data", data)
    phone_number = data.get('phone_number').strip() if data.get('phone_number') else ''
    amount = data.get('amount') 
    phone_number = unquote(phone_number)
    print("number", phone_number)
    print("amount", amount)
    
    if not phone_number:
        print("Missing phone number or amount")
        return jsonify({"error": "Missing phone number or amount"}), 400

    subscriber = User.query.filter_by(phone_number=phone_number).first()
    print("subscriber response", subscriber)
    if not subscriber:
        print("Subscriber not found")
        return jsonify({"error": "Subscriber not found"}), 404

    # Generate a unique reference for this transaction
    reference = str(uuid.uuid4())
    print("Generated reference:", reference)
    base_url = os.environ.get("BASE_URL")

    # Create Paystack payment link
    paystack_secret_key = os.environ.get('PAYSTACK_KEY')
    paystack_url = "https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {paystack_secret_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "amount": int(amount * 100),  # Convert to kobo
        "email": 'raymond@delaphonegh.com',
        "reference": reference,
        "callback_url": f"{base_url}/api/paystack_callback/{subscriber.id}/{reference}"
    }

    print("Payload:", payload)
    paystack_response = requests.post(paystack_url, json=payload, headers=headers)
    print("Paystack response status code:", paystack_response.status_code)
    
    if paystack_response.status_code != 200:
        print("Failed to create payment link")
        return jsonify({"error": "Failed to create payment link"}), 500

    payment_link = paystack_response.json()['data']['authorization_url']

    # Send SMS with new API
    wirepick_key =  os.environ.get('WIREPICK_KEY')
    sms_url = "https://api.wirepick.com/httpsms/send"
    sms_params = {
        'client': 'raymond',
        'password': wirepick_key,
        'phone': phone_number,
        'text': f"Follow the link to top-up: {payment_link}",
        'from': 'Delaphone'
    }
    
    print("SMS params:", sms_params)
    sms_response = requests.get(sms_url, params=sms_params)
    print("SMS response:", sms_response.content)

    if sms_response.status_code != 200:
        print("Failed to send sms")
        return jsonify({"error": "Failed to send sms"}), 500

    print("SMS sent successfully")
    return jsonify({"status": "success", "payment_link": payment_link}), 200





@telafric.route('/api/paystack_topup', methods=['POST'])
def paystack_topup():
    print("Paystack top-up initiated")  # Debugging print

    if not current_user.is_authenticated:
        print("User is not authenticated")  # Debugging print
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    print(f"Received data: {data}")  # Debugging print

    amount = data.get('amount')  # Amount should be in kobo (1 unit = 0.01 currency)
    if not amount:
        print("Missing amount")  # Debugging print
        return jsonify({"error": "Missing amount"}), 400

    base_url = os.environ.get("BASE_URL")
    # Generate a unique reference for this transaction
    reference = str(uuid.uuid4())
    print(f"Generated reference: {reference}")  # Debugging print
    amount = float(data.get('amount', 0))  # Ensure amount is a float
# Convert to kobo
    amount_in_kobo = int(amount * 100) 
    # Create Paystack payment link
    paystack_secret_key = os.environ.get('PAYSTACK_KEY')
    paystack_url = "https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {paystack_secret_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "amount": amount_in_kobo,  # Convert to kobo
        # "amount": 5,  # Convert to kobo
        "email": "raymond@delaphonegh.com",  # Assuming the user has an email field
        "reference": reference,
        "callback_url": f"{base_url}/api/paystack_callback/{current_user.id}/{reference}"  # Adjust the callback URL
    }

    print(f"Payload for Paystack API: {payload}")  # Debugging print

    paystack_response = requests.post(paystack_url, json=payload, headers=headers)
    print(f"Paystack response status code: {paystack_response.status_code,paystack_response.content}")  # Debugging print

    if paystack_response.status_code != 200:
        print("Failed to create payment link")  # Debugging print
        return jsonify({"error": "Failed to create payment link"}), 500

    payment_link = paystack_response.json()['data']['authorization_url']
    print(f"Payment link generated: {payment_link}")  # Debugging print

    return jsonify({"payment_link": payment_link}), 200



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
                    subscriber_id=subscriber_id,
                    aggregator = "Paystack"
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
        return redirect(url_for('users.login'))
    
    
    
    # Fetch call logs and payments for the current user
    call_logs = CallLog.query.filter_by(subscriber_id=current_user.id).all()
    payments = Payment.query.filter_by(subscriber_id=current_user.id).all()
    
    return render_template('ids/portal/dashboard.html', call_logs=call_logs, payments=payments,user =current_user)





@telafric.route('/top_up', methods=['GET'])
def top_up():
    # Get amount from query parameter, default to 10 if not provided
    amount = request.args.get('amount', '10.00')
    
    # Generate a unique transaction ID
    transaction_id = str(uuid.uuid4())
    
    # PayPal sandbox URL (use PDT endpoint)
    paypal_url = "https://www.sandbox.paypal.com/cgi-bin/webscr"
    
    # PayPal parameters (updated)
    params = {
        "cmd": "_xclick",
        "business": "sb-3zjqn30858747@business.example.com",  # Your PayPal sandbox business email
        "item_name": "Account Top Up",
        "amount": amount,
        "currency_code": "USD",
        "return": url_for('telafric.paypal_success', transaction_id=transaction_id, _external=True),
        "cancel_return": url_for('telafric.dashboard', _external=True),
        "notify_url": url_for('telafric.paypal_ipn', _external=True),
        "custom": transaction_id,  # Pass transaction ID for tracking
        "no_shipping": "1",  # No shipping required
        "no_note": "1"  # No notes allowed
    }
    
    # Construct redirect URL
    redirect_url = paypal_url + "?" + urlencode(params)
    return redirect(redirect_url)

@telafric.route('/paypal_success')
def paypal_success():
    transaction_id = request.args.get('transaction_id')
    
    # Find the payment in the database
    payment = Payment.query.filter_by(reference=transaction_id).first()
    
    if payment:
        payment.status = 'completed'
        db.session.commit()
        flash('Payment successful!')
    else:
        flash('Payment record not found.')
    
    return redirect(url_for('telafric.dashboard'))

@telafric.route('/paypal_ipn', methods=['POST'])
def paypal_ipn():
    # Verify IPN message with PayPal
    data = request.form.copy()
    data['cmd'] = '_notify-validate'
    
    # Verify with PayPal
    response = requests.post("https://www.sandbox.paypal.com/cgi-bin/webscr", data=data)
    
    if response.text == "VERIFIED":
        # Extract payment details
        payment_status = request.form.get('payment_status')
        transaction_id = request.form.get('custom')
        amount = request.form.get('mc_gross')
        payer_email = request.form.get('payer_email')
        
        # Find existing payment or create new one
        payment = Payment.query.filter_by(reference=transaction_id).first()
        
        if not payment:
            # Create new payment record if not exists
            payment = Payment(
                reference=transaction_id,
                amount=float(amount),
                paid_at=datetime.utcnow(),
                status=payment_status.lower(),
                subscriber_id=current_user.id,  # Ensure current_user is imported/available
                aggregator='PayPal'
            )
            db.session.add(payment)
        else:
            # Update existing payment
            payment.status = payment_status.lower()
            payment.paid_at = datetime.utcnow()
        
        # Update user balance
        if payment_status.lower() == 'completed':
            current_user.balance += float(amount)
        
        db.session.commit()
    
    return "OK"

@telafric.route('/rates', methods=['GET'])
def view_rates():
    rates = Rate.query.all()  # Fetch all rates from the database
    return render_template('ids/portal/rates.html', rates=rates)



@telafric.route('/call_logs', methods=['GET'])
# @login_required
def view_call_logs():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))  # Redirect to login if not authenticated

    search_query = request.args.get('search', '')  # Get the search query from the request
    call_logs = CallLog.query.filter_by(subscriber_id=current_user.id)

    if search_query:
        # Filter call logs based on the search query
        call_logs = call_logs.filter(
            (CallLog.phone_number.like(f'%{search_query}%')) |  # Search by phone number
            (CallLog.destination.like(f'%{search_query}%')) |  # Search by destination
            (CallLog.duration.like(f'%{search_query}%')) |  # Search by duration
            (CallLog.timestamp.like(f'%{search_query}%'))  # Search by timestamp (if applicable)
            # Add more fields to search as needed
        )

    call_logs = call_logs.all()  # Execute the query

    return render_template('ids/portal/call_logs.html', call_logs=call_logs, search_query=search_query)

@telafric.route('/payments', methods=['GET'])
def view_payments():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))  # Redirect to login if not authenticated

    payments = Payment.query.filter_by(subscriber_id=current_user.id).all()  # Fetch payments for the current user
    return render_template('ids/portal/payments.html', payments=payments,user=current_user)











# Admin Stuff
@telafric.route('/admin/dashboard', methods=['GET'])
# @login_required
def admin_dashboard():
    user = User.query.filter_by(id = session['id']).first()
    print("user")
    return render_template('ids/admin/dashboard.html',user=user)  # Adjust the template path as necessary

@telafric.route('/admin/rates', methods=['GET'])
def admin_rates():
    rates = Rate.query.all()  # Fetch all rates from the database
    return render_template('ids/admin/rates.html', rates=rates)


@telafric.route('/admin/admins', methods=['GET', 'POST'])
def admins():
    if not current_user.is_authenticated or current_user.role != 'admin':
        return jsonify({"error": "Unauthorized"}), 401  # Ensure only admins can access this route
    admins = User.query.filter_by(role="admin").all()
    if request.method == 'POST':
        data = request.form
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')
        role = 'admin'  # Set the role to admin

        # Create a new admin user
        new_admin = User(email=email, username=username, password=password, role=role)
        new_admin.password_hash = generate_password_hash(password)  # Hash the password
        db.session.add(new_admin)
        db.session.commit()

        flash('Admin account created successfully!', 'success')
        return redirect(url_for('telafric.admin_dashboard'))  # Redirect to the admin dashboard

    return render_template('ids/admin/admins.html',admins=admins)  # Render the form template



@telafric.route('/api/admins', methods=['GET'])
def fetch_admins():
    if not current_user.is_authenticated or current_user.role != 'admin':
        return jsonify({"error": "Unauthorized"}), 401  # Ensure only admins can access this route

    # Query to get all users with the role of admin
    admins = User.query.filter_by(role='admin').all()
    
    # Prepare the response data
    admin_list = [{
        "id": admin.id,
        "email": admin.email,
        "username": admin.username
    } for admin in admins]

    return jsonify(admin_list), 200  # Return the list of admins as JSON


@telafric.route('/api/admins', methods=['POST'])
def add_admin():
    print("adding a new admin")
    if not current_user.is_authenticated or current_user.role != 'admin':
        return jsonify({"error": "Unauthorized"}), 401  # Ensure only admins can access this route

    data = request.get_json()  # Get the JSON data from the request
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    # Validate input
    if not email or not username or not password:
        print("missing fields")
        return jsonify({"error": "Missing required fields"}), 400

    # Check if the email or username already exists
    existing_admin = User.query.filter((User.email == email) | (User.username == username)).first()
    if existing_admin:
        return jsonify({"error": "Email or username already exists"}), 409  # Conflict

    # Create a new admin user
    new_admin = User(
        email=email,
        username=username,
        password=password,
        role="admin"  # Pass the plain password to the User constructor
    )
    new_admin.password_hash = generate_password_hash(password)  # Hash the password
    db.session.add(new_admin)
    db.session.commit()
    print("admin added")

    return jsonify({"message": "Admin account created successfully!"}), 201  # Return success message



@telafric.route('/api/admins/<int:admin_id>', methods=['DELETE'])
def delete_admin(admin_id):
    if not current_user.is_authenticated or current_user.role != 'admin':
        return jsonify({"error": "Unauthorized"}), 401  # Ensure only admins can access this route

    admin_to_delete = User.query.get(admin_id)
    if not admin_to_delete:
        return jsonify({"error": "Admin not found"}), 404  # Return an error if the admin does not exist

    db.session.delete(admin_to_delete)
    db.session.commit()

    return jsonify({"message": "Admin account deleted successfully!"}), 200  # Return success message


@telafric.route('/api/admins/<int:admin_id>', methods=['PUT'])
def edit_admin(admin_id):
    if not current_user.is_authenticated or current_user.role != 'admin':
        return jsonify({"error": "Unauthorized"}), 401  # Ensure only admins can access this route

    data = request.get_json()  # Get the JSON data from the request
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    # Validate input
    if not email or not username:
        return jsonify({"error": "Missing required fields"}), 400

    admin_to_edit = User.query.get(admin_id)
    if not admin_to_edit:
        return jsonify({"error": "Admin not found"}), 404  # Return an error if the admin does not exist

    # Check for duplicate email or username
    existing_admin = User.query.filter(
        (User.email == email) | (User.username == username)
    ).first()
    if existing_admin and existing_admin.id != admin_id:
        return jsonify({"error": "Email or username already exists"}), 409  # Conflict

    # Update admin details
    admin_to_edit.email = email
    admin_to_edit.username = username
    if password:  # Only update password if provided
        admin_to_edit.password_hash = generate_password_hash(password)

    db.session.commit()

    return jsonify({"message": "Admin account updated successfully!"}), 200  # Return success message
from flask import Flask, request, jsonify, Blueprint
import requests
import hashlib
import time
import json
import os

vtiger = Blueprint('vtiger', __name__)

# vTiger configuration
VTIGER_URL = "http://102.22.15.133/webservice.php"
VTIGER_ACCESS_KEY = os.environ.get('VTIGER_ACCESS_KEY')
VTIGER_USERNAME = os.environ.get('VTIGER_USER')


def get_vtiger_token():
    """Get challenge token from vTiger"""
    params = {
        'operation': 'getchallenge',
        'username': VTIGER_USERNAME
    }
    print("Requesting challenge token from vTiger with params:",params)
    response = requests.get(VTIGER_URL, params=params)
    print("vTiger response:", response.content)
    token = response.json()['result']['token']
    print("Challenge token:", token)
    return token

def vtiger_login():
    """Login to vTiger and get session ID"""
    token = get_vtiger_token()
    print("vTiger challenge token:", token)
    accessKey = hashlib.md5(
        (token + VTIGER_ACCESS_KEY).encode()
    ).hexdigest()
    
    login_params = {
        'operation': 'login',
        'username': VTIGER_USERNAME,
        'accessKey': accessKey
    }
    print("Logging in to vTiger with access key:", accessKey)
    response = requests.post(VTIGER_URL, data=login_params)
    print("vTiger response:", response.content)
    return response.json()['result']['sessionName']

def search_contact(phone_number, session_id):
    """Search for contact by phone number"""
    query = f"SELECT * FROM Contacts WHERE phone = '{phone_number}';"
    print("Searching for contact with phone number:", phone_number)
    params = {
        'operation': 'query',
        'sessionName': session_id,
        'query': query
    }
    print("vTiger query:", query)
    response = requests.get(VTIGER_URL, params=params)
    print("vTiger response:", response.content)
    return response.json()

def create_contact(contact_data, session_id):
    """Create new contact in vTiger"""
    print("Creating contact with data:", contact_data)
    params = {
        'operation': 'create',
        'sessionName': session_id,
        'element': json.dumps(contact_data),
        'elementType': 'Contacts'
    }
    print("vTiger request:", params)
    response = requests.post(VTIGER_URL, data=params)
    print("vTiger response:", response.content)
    return response.json()

@vtiger.route('/handle_call', methods=['POST'])
def handle_call():
    # Extract data from Isabel's webhook
    data = request.json
    phone_number = data.get('phone_number')
    print("Received phone number:", phone_number)
    # return "done"
    
    if not phone_number:
        print("Phone number is missing from request")
        return jsonify({'error': 'Phone number is required'}), 400
    
    try:
        # Login to vTiger
        session_id = vtiger_login()
        print("Obtained vTiger session ID:", session_id)
        
        # Search for existing contact
        existing_contact = search_contact(phone_number, session_id)
        print("Search contact result:", existing_contact)
        
        if existing_contact.get('result'):
            # Contact exists - return URL to contact's detail view
            contact_id = existing_contact['result'][0]['id']
            print("Contact exists with ID:", contact_id)
            return jsonify({
                'status': 'success',
                'action': 'view',
                'url': f"{VTIGER_URL}?module=Contacts&view=Detail&record={contact_id}"
            })
        else:
            # Create new contact
            contact_data = {
                'lastname': 'Unknown',  # Required field in vTiger
                'phone': phone_number,
                'assigned_user_id': 1  # Default assignee
            }
            print("Creating new contact with data:", contact_data)
            new_contact = create_contact(contact_data, session_id)
            print("New contact created:", new_contact)
            
            return jsonify({
                'status': 'success',
                'action': 'create',
                'url': f"{VTIGER_URL}?module=Contacts&view=Detail&record={new_contact['result']['id']}"
            })
            
    except Exception as e:
        print("Error occurred:", str(e))
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@vtiger.route('/handle_call2', methods=['GET'])
def handle_call_get():
    phone_number = request.args.get('phone_number')
    print("Received phone number:", phone_number)
    
    if not phone_number:
        print("Phone number is missing from request")
        return jsonify({'error': 'Phone number is required'}), 400
    
    try:
        # Login to vTiger
        session_id = vtiger_login()
        print("Obtained vTiger session ID:", session_id)
        
        # Search for existing contact
        existing_contact = search_contact(phone_number, session_id)
        print("Search contact result:", existing_contact)
        
        if existing_contact.get('result'):
            # Contact exists - return URL to contact's detail view
            contact_id = existing_contact['result'][0]['id']
            print("Contact exists with ID:", contact_id)
            return jsonify({
                'status': 'success',
                'action': 'view',
                'url': f"{VTIGER_URL}?module=Contacts&view=Detail&record={contact_id}"
            })
        else:
            # Create new contact
            contact_data = {
                'lastname': 'Unknown',  # Required field in vTiger
                'phone': phone_number,
                'assigned_user_id': 1  # Default assignee
            }
            print("Creating new contact with data:", contact_data)
            new_contact = create_contact(contact_data, session_id)
            print("New contact created:", new_contact)
            
            return jsonify({
                'status': 'success',
                'action': 'create',
                'url': f"{VTIGER_URL}?module=Contacts&view=Detail&record={new_contact['result']['id']}"
            })
            
    except Exception as e:
        print("Error occurred:", str(e))
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
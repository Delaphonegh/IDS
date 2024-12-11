from flask import Flask, request, jsonify, Blueprint, redirect, make_response
import requests
import hashlib
import json
import os
# from flask_cors import CORS

vtiger = Blueprint('vtiger', __name__)

# vTiger configuration
VTIGER_URL = "http://102.22.15.133/webservice.php"
VTIGER_RETURN_URL = "http://nppcrm.delaphonegh.com"
VTIGER_ACCESS_KEY = os.environ.get('VTIGER_ACCESS_KEY')
VTIGER_USERNAME = os.environ.get('VTIGER_USER')


DEMO_VTIGER_URL = "http://102.22.14.237/webservice.php"
DEMO_VTIGER_RETURN_URL = "http://democrm.delaphonegh.net"
DEMO_VTIGER_ACCESS_KEY = os.environ.get('DEMO_VTIGER_ACCESS_KEY')
DEMO_VTIGER_USERNAME = os.environ.get('DEMO_VTIGER_USER')

def get_vtiger_token():
    """Get challenge token from vTiger"""
    params = {
        'operation': 'getchallenge',
        'username': VTIGER_USERNAME
    }
    response = requests.get(VTIGER_URL, params=params)
    return response.json()['result']['token']

def vtiger_login():
    """Login to vTiger and get session ID"""
    token = get_vtiger_token()
    accessKey = hashlib.md5(
        (token + VTIGER_ACCESS_KEY).encode()
    ).hexdigest()
    
    login_params = {
        'operation': 'login',
        'username': VTIGER_USERNAME,
        'accessKey': accessKey
    }
    response = requests.post(VTIGER_URL, data=login_params)
    return response.json()['result']['sessionName']

def clean_phone_number(phone_number):
    """Clean phone number by removing non-digit characters"""
    return ''.join(filter(str.isdigit, phone_number))

def search_contact(phone_number, session_id):
    """Search for contact by phone number using multiple fields"""
    clean_number = clean_phone_number(phone_number)
    
    # vTiger prefers simpler queries - let's search one field at a time
    phone_fields = ['phone', 'mobile', 'homephone', 'otherphone']
    
    for field in phone_fields:
        # Try exact match first
        query = f"SELECT * FROM Contacts WHERE {field} = '{phone_number}';"
        params = {
            'operation': 'query',
            'sessionName': session_id,
            'query': query
        }
        
        response = requests.get(VTIGER_URL, params=params)
        result = response.json()
        
        if result.get('success') and result.get('result'):
            return result
            
        # Try with cleaned number
        if clean_number != phone_number:
            query = f"SELECT * FROM Contacts WHERE {field} = '{clean_number}';"
            params['query'] = query
            
            response = requests.get(VTIGER_URL, params=params)
            result = response.json()
            
            if result.get('success') and result.get('result'):
                return result
    
    # If no contact found, return empty success response
    return {'success': True, 'result': []}

def create_contact(phone_number, session_id):
    """Create a new contact with basic information"""
    contact_data = {
        'lastname': f'Unknown ({phone_number})',  # More descriptive default name
        'phone': phone_number,
        'assigned_user_id': '19x1',
        'leadsource': 'Phone Call'  # Add lead source for better tracking
    }
    
    params = {
        'operation': 'create',
        'sessionName': session_id,
        'element': json.dumps(contact_data),
        'elementType': 'Contacts'
    }
    
    response = requests.post(VTIGER_URL, data=params)
    return response.json()

@vtiger.route('/handle_call', methods=['POST'])
def handle_call():
    """Handle incoming call webhook"""
    data = request.json
    phone_number = data.get('phone_number')
    
    if not phone_number:
        return jsonify({'error': 'Phone number is required'}), 400
        
    try:
        session_id = vtiger_login()
        
        # First try to find existing contact
        existing_contact = search_contact(phone_number, session_id)
        
        if existing_contact.get('success') and existing_contact.get('result'):
            contact_id = existing_contact['result'][0]['id']
            return jsonify({
                'status': 'success',
                'action': 'view',
                'contact_id': contact_id,
                'url': f"{VTIGER_RETURN_URL}?module=Contacts&view=Detail&record={contact_id}"
            })
        
        # If no contact found and no error occurred, create new contact
        if existing_contact.get('success'):
            create_result = create_contact(phone_number, session_id)
            
            if create_result.get('success'):
                new_contact_id = create_result['result']['id']
                return jsonify({
                    'status': 'success',
                    'action': 'create',
                    'contact_id': new_contact_id,
                    'url': f"{VTIGER_RETURN_URL}?module=Contacts&view=Detail&record={new_contact_id}"
                })
            
            if 'duplicate' in str(create_result.get('error', {})).lower():
                return jsonify({
                    'status': 'error',
                    'message': 'Potential duplicate contact detected. Please search manually.',
                    'phone_number': phone_number
                }), 409
            
            raise Exception(f"Failed to create contact: {create_result.get('error', {}).get('message', 'Unknown error')}")
        
        raise Exception(f"Search failed: {existing_contact.get('error', {}).get('message', 'Unknown error')}")
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'details': {
                'phone_number': phone_number
            }
        }), 500


@vtiger.route('/handle_call2', methods=['GET'])
def handle_call2():
    """Handle incoming call webhook via GET request"""
    phone_number = request.args.get('phone_number')
    print("Received phone number:", phone_number)

    if not phone_number:
        print("Phone number is missing from request")
        return jsonify({'error': 'Phone number is required'}), 400

    try:
        session_id = vtiger_login()
        print("Obtained vTiger session ID:", session_id)

        existing_contact = search_contact(phone_number, session_id)
        print("Search contact result:", existing_contact)

        if existing_contact.get('success') and existing_contact.get('result'):
            # contact_id = existing_contact['result'][0]['id']
            contact_id = existing_contact['result'][0]['id'].split('x')[-1]
            
            print("Contact exists with ID:", contact_id)
            final_url = f"{VTIGER_RETURN_URL}/index.php?module=Contacts&view=Detail&record={contact_id}&app=INVENTORY"
            print(f"Redirecting to: {final_url}")
            return redirect(final_url)

        if existing_contact.get('success'):
            create_result = create_contact(phone_number, session_id)
            print("Create contact result:", create_result)

            if create_result.get('success'):
                new_contact_id = create_result['result']['id']
                print("New contact created:", new_contact_id)
                final_url = f"{VTIGER_RETURN_URL}/index.php?module=Contacts&view=Detail&record={new_contact_id}&app=INVENTORY"
                print(f"Redirecting to: {final_url}")
                return redirect(final_url)

            if 'duplicate' in str(create_result.get('error', {})).lower():
                print("Potential duplicate contact detected. Please search manually.")
                return jsonify({'error': 'Potential duplicate contact detected. Please search manually.'}), 409

            raise Exception(f"Failed to create contact: {create_result.get('error', {}).get('message', 'Unknown error')}")

        raise Exception(f"Search failed: {existing_contact.get('error', {}).get('message', 'Unknown error')}")

    except Exception as e:
        print("Error occurred:", str(e))
        return jsonify({'error': str(e)}), 500
# @vtiger.route('/handle_call2', methods=['GET'])
# def handle_call2():
#     """Handle incoming call webhook via GET request"""
#     # Get phone number from query parameters instead of JSON body
#     phone_number = request.args.get('phone_number')
#     print("Received phone number:", phone_number)
    
#     if not phone_number:
#         print("Phone number is missing from request")
#         return jsonify({'error': 'Phone number is required'}), 400
        
#     try:
#         session_id = vtiger_login()
#         print("Obtained vTiger session ID:", session_id)
        
#         # First try to find existing contact
#         existing_contact = search_contact(phone_number, session_id)
#         print("Search contact result:", existing_contact)
        
#         if existing_contact.get('success') and existing_contact.get('result'):
#             contact_id = existing_contact['result'][0]['id']
#             print("Contact exists with ID:", contact_id)
#             return jsonify({
#                 'status': 'success',
#                 'action': 'view',
#                 'contact_id': contact_id,
#                 'url': f"{VTIGER_URL}?module=Contacts&view=Detail&record={contact_id}"
#             })
        
#         # If no contact found and no error occurred, create new contact
#         if existing_contact.get('success'):
#             create_result = create_contact(phone_number, session_id)
#             print("Create contact result:", create_result)
            
#             if create_result.get('success'):
#                 new_contact_id = create_result['result']['id']
#                 print("New contact created:", new_contact_id)
#                 return jsonify({
#                     'status': 'success',
#                     'action': 'create',
#                     'contact_id': new_contact_id,
#                     'url': f"{VTIGER_URL}?module=Contacts&view=Detail&record={new_contact_id}"
#                 })
            
#             if 'duplicate' in str(create_result.get('error', {})).lower():
#                 print("Potential duplicate contact detected. Please search manually.")
#                 return jsonify({
#                     'status': 'error',
#                     'message': 'Potential duplicate contact detected. Please search manually.',
#                     'phone_number': phone_number
#                 }), 409
            
#             raise Exception(f"Failed to create contact: {create_result.get('error', {}).get('message', 'Unknown error')}")
        
#         raise Exception(f"Search failed: {existing_contact.get('error', {}).get('message', 'Unknown error')}")
            
#     except Exception as e:
#         print("Error occurred:", str(e))
#         return jsonify({
#             'status': 'error',
#             'message': str(e),
#             'details': {
#                 'phone_number': phone_number
#             }
#         }), 500



# @vtiger.route('/handle_call2', methods=['GET'])
# def handle_call2():
#     """Handle incoming call webhook via GET request"""
#     phone_number = request.args.get('phone_number')
#     print("Received phone number:", phone_number)

#     if not phone_number:
#         print("Phone number is missing from request")
#         return jsonify({'error': 'Phone number is required'}), 400

#     try:
#         session_id = vtiger_login()
#         print("Obtained vTiger session ID:", session_id)

#         existing_contact = search_contact(phone_number, session_id)
#         print("Search contact result:", existing_contact)

#         if existing_contact.get('success') and existing_contact.get('result'):
#             contact_id = existing_contact['result'][0]['id']
#             print("Contact exists with ID:", contact_id)
#             # return f"{VTIGER_RETURN_URL}?module=Contacts&view=Detail&record={contact_id}"
#             final_url = f"{VTIGER_RETURN_URL}?module=Contacts&view=Detail&record={contact_id}"
#             print(f"Redirecting to: {final_url}")
#             return redirect(final_url)

#         if existing_contact.get('success'):
#             create_result = create_contact(phone_number, session_id)
#             print("Create contact result:", create_result)

#             if create_result.get('success'):
#                 new_contact_id = create_result['result']['id']
#                 print("New contact created:", new_contact_id)
#                 # return f"{VTIGER_RETURN_URL}?module=Contacts&view=Detail&record={new_contact_id}"
#                 final_url = f"{VTIGER_RETURN_URL}?module=Contacts&view=Detail&record={contact_id}"
#                 print(f"Redirecting to: {final_url}")
#                 return redirect(final_url)

#             if 'duplicate' in str(create_result.get('error', {})).lower():
#                 print("Potential duplicate contact detected. Please search manually.")
#                 return jsonify({'error': 'Potential duplicate contact detected. Please search manually.'}), 409

#             raise Exception(f"Failed to create contact: {create_result.get('error', {}).get('message', 'Unknown error')}")

#         raise Exception(f"Search failed: {existing_contact.get('error', {}).get('message', 'Unknown error')}")

#     except Exception as e:
#         print("Error occurred:", str(e))
#         return jsonify({'error': str(e)}), 500


@vtiger.route('/handle_call3', methods=['GET'])
def handle_call3():
    """Handle incoming call webhook via GET request!"""
    phone_number = request.args.get('phone_number')
    print("Received phone number:", phone_number)
    
    if not phone_number:
        print("Phone number is missing from request")
        return """
            <script>
                document.write('Error: Phone number is required');
            </script>
        """
        
    try:
        session_id = vtiger_login()
        print("Obtained vTiger session ID:", session_id)
        
        # First try to find existing contact
        existing_contact = search_contact(phone_number, session_id)
        print("Search contact result:", existing_contact)
        
        if existing_contact.get('success') and existing_contact.get('result'):
            contact_id = existing_contact['result'][0]['id']
            print("Contact exists with ID:", contact_id)
            vtiger_url = f"{VTIGER_RETURN_URL}/index.php?module=Contacts&view=Detail&record={contact_id}&app=MARKETING"
            print("url:",vtiger_url)
            # rvtiger_url = f"{VTIGER_RETURN_URL}/index.php?module=Contacts&view=Detail&record={contact_id}&app=MARKETING"
    
            response = make_response(f"""
            <html>
                <head>
                    <script>
                        window.location.href = '{vtiger_url}';
                    </script>
                </head>
            </html>
            """)
            
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
            
            return response
        
        # If no contact found and no error occurred, create new contact
        if existing_contact.get('success'):
            create_result = create_contact(phone_number, session_id)
            print("Create contact result:", create_result)
            
            if create_result.get('success'):
                new_contact_id = create_result['result']['id']
                print("New contact created:", new_contact_id)
                vtiger_url = f"{VTIGER_RETURN_URL}/index.php?module=Contacts&view=Detail&record={new_contact_id}&app=MARKETING"
                print("url:",vtiger_url)
                # vtiger_url = f"{VTIGER_RETURN_URL}/index.php?module=Contacts&view=Detail&record={contact_id}&app=MARKETING"
    
                response = make_response(f"""
                <html>
                    <head>
                        <script>
                            window.location.href = '{vtiger_url}';
                        </script>
                    </head>
                </html>
                """)
                
                response.headers['Access-Control-Allow-Origin'] = '*'
                response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
                
                return response
            
            if 'duplicate' in str(create_result.get('error', {})).lower():
                print("Potential duplicate contact detected")
                return """
                    <script>
                        document.write('Error: Potential duplicate contact detected. Please search manually.');
                    </script>
                """
            
            raise Exception(f"Failed to create contact: {create_result.get('error', {}).get('message', 'Unknown error')}")
        
        raise Exception(f"Search failed: {existing_contact.get('error', {}).get('message', 'Unknown error')}")
            
    except Exception as e:
        print("Error occurred:", str(e))
        error_msg = str(e).replace("'", "\\'")
        return f"""
            <script>
                document.write('Error: {error_msg}');
            </script>
        """



# @vtiger.route('/handle_call4', methods=['GET'])
# def handle_call4():
#     """Handle incoming call webhook via GET request"""
#     phone_number = request.args.get('phone_number')
#     print("Received phone number:", phone_number)
    
#     if not phone_number:
#         print("Phone number is missing from request")
#         return f"<script>window.open('', '_self').document.write('Error: Phone number is required');</script>"
        
#     try:
#         session_id = vtiger_login()
#         print("Obtained vTiger session ID:", session_id)
        
#         # First try to find existing contact
#         existing_contact = search_contact(phone_number, session_id)
#         print("Search contact result:", existing_contact)
        
#         if existing_contact.get('success') and existing_contact.get('result'):
#             contact_id = existing_contact['result'][0]['id']
#             print("Contact exists with ID:", contact_id)
#             vtiger_url = f"{VTIGER_URL}?module=Contacts&view=Detail&record={contact_id}"
#             return f"<script>window.location.href = '{vtiger_url}';</script>"
        
#         # If no contact found and no error occurred, create new contact
#         if existing_contact.get('success'):
#             create_result = create_contact(phone_number, session_id)
#             print("Create contact result:", create_result)
            
#             if create_result.get('success'):
#                 new_contact_id = create_result['result']['id']
#                 print("New contact created:", new_contact_id)
#                 vtiger_url = f"{VTIGER_URL}?module=Contacts&view=Detail&record={new_contact_id}"
#                 return f"<script>window.location.href = '{vtiger_url}';</script>"
            
#             if 'duplicate' in str(create_result.get('error', {})).lower():
#                 print("Potential duplicate contact detected")
#                 error_msg = "Potential duplicate contact detected. Please search manually."
#                 return f"<script>window.open('', '_self').document.write('{error_msg}');</script>"
            
#             raise Exception(f"Failed to create contact: {create_result.get('error', {}).get('message', 'Unknown error')}")
        
#         raise Exception(f"Search failed: {existing_contact.get('error', {}).get('message', 'Unknown error')}")
            
#     except Exception as e:
#         print("Error occurred:", str(e))
#         error_msg = str(e).replace("'", "\\'")  # Escape single quotes for JavaScript
#         return f"<script>window.open('', '_self').document.write('Error: {error_msg}');</script>"


def get_demo_vtiger_token():
    """Get challenge token from vTiger"""
    params = {
        'operation': 'getchallenge',
        'username': DEMO_VTIGER_USERNAME
    }
    response = requests.get(DEMO_VTIGER_URL, params=params)
    return response.json()['result']['token']

def vtiger_demo_login():
    """Login to vTiger and get session ID"""
    token = get_demo_vtiger_token()
    accessKey = hashlib.md5(
        (token + DEMO_VTIGER_ACCESS_KEY).encode()
    ).hexdigest()
    
    login_params = {
        'operation': 'login',
        'username': DEMO_VTIGER_USERNAME,
        'accessKey': accessKey
    }
    response = requests.post(DEMO_VTIGER_URL, data=login_params)
    return response.json()['result']['sessionName']

def clean_demo_phone_number(phone_number):
    """Clean phone number by removing non-digit characters"""
    return ''.join(filter(str.isdigit, phone_number))

def search_demo_contact(phone_number, session_id):
    """Search for contact by phone number using multiple fields"""
    clean_number = clean_demo_phone_number(phone_number)
    
    # vTiger prefers simpler queries - let's search one field at a time
    phone_fields = ['phone', 'mobile', 'homephone', 'otherphone']
    
    for field in phone_fields:
        # Try exact match first
        query = f"SELECT * FROM Contacts WHERE {field} = '{phone_number}';"
        params = {
            'operation': 'query',
            'sessionName': session_id,
            'query': query
        }
        
        response = requests.get(DEMO_VTIGER_URL, params=params)
        result = response.json()
        
        if result.get('success') and result.get('result'):
            return result
            
        # Try with cleaned number
        if clean_number != phone_number:
            query = f"SELECT * FROM Contacts WHERE {field} = '{clean_number}';"
            params['query'] = query
            
            response = requests.get(DEMO_VTIGER_URL, params=params)
            result = response.json()
            
            if result.get('success') and result.get('result'):
                return result
    
    # If no contact found, return empty success response
    return {'success': True, 'result': []}

def create_demo_contact(phone_number, session_id):
    """Create a new contact with basic information"""
    contact_data = {
        'lastname': f'Unknown ({phone_number})',  # More descriptive default name
        'phone': phone_number,
        'assigned_user_id': '19x1',
        'leadsource': 'Phone Call'  # Add lead source for better tracking
    }
    
    params = {
        'operation': 'create',
        'sessionName': session_id,
        'element': json.dumps(contact_data),
        'elementType': 'Contacts'
    }
    
    response = requests.post(DEMO_VTIGER_URL, data=params)
    return response.json()


@vtiger.route('/demo/handle_call', methods=['GET'])
def demo_handle_call():
    """Handle incoming call webhook via GET request"""
    phone_number = request.args.get('phone_number')
    print("Received phone number:", phone_number)

    if not phone_number:
        print("Phone number is missing from request")
        return jsonify({'error': 'Phone number is required'}), 400

    try:
        session_id = vtiger_demo_login()
        print("Obtained vTiger session ID:", session_id)

        existing_contact = search_demo_contact(phone_number, session_id)
        print("Search contact result:", existing_contact)

        if existing_contact.get('success') and existing_contact.get('result'):
            # contact_id = existing_contact['result'][0]['id']
            contact_id = existing_contact['result'][0]['id'].split('x')[-1]
            
            print("Contact exists with ID:", contact_id)
            final_url = f"{DEMO_VTIGER_RETURN_URL}/index.php?module=Contacts&view=Detail&record={contact_id}&app=INVENTORY"
            print(f"Redirecting to: {final_url}")
            return redirect(final_url)

        if existing_contact.get('success'):
            create_result = create_demo_contact(phone_number, session_id)
            print("Create contact result:", create_result)

            if create_result.get('success'):
                new_contact_id = create_result['result']['id']
                print("New contact created:", new_contact_id)
                final_url = f"{DEMO_VTIGER_RETURN_URL}/index.php?module=Contacts&view=Detail&record={new_contact_id}&app=INVENTORY"
                print(f"Redirecting to: {final_url}")
                return redirect(final_url)

            if 'duplicate' in str(create_result.get('error', {})).lower():
                print("Potential duplicate contact detected. Please search manually.")
                return jsonify({'error': 'Potential duplicate contact detected. Please search manually.'}), 409

            raise Exception(f"Failed to create contact: {create_result.get('error', {}).get('message', 'Unknown error')}")

        raise Exception(f"Search failed: {existing_contact.get('error', {}).get('message', 'Unknown error')}")

    except Exception as e:
        print("Error occurred:", str(e))
        return jsonify({'error': str(e)}), 500



def debug_vtiger_api(phone_number):
    """Helper function to debug API calls"""
    try:
        session_id = vtiger_login()
        print(f"Session ID: {session_id}")
        
        # Test a simple query first
        test_query = "SELECT * FROM Contacts LIMIT 1;"
        test_params = {
            'operation': 'query',
            'sessionName': session_id,
            'query': test_query
        }
        
        print("Testing basic query...")
        test_response = requests.get(VTIGER_URL, params=test_params)
        print(f"Test query response: {test_response.text}")
        
        # Now try the actual search
        print(f"Searching for phone: {phone_number}")
        search_result = search_demo_contact(phone_number, session_id)
        print(f"Search result: {json.dumps(search_result, indent=2)}")
        
        return search_result
        
    except Exception as e:
        print(f"Debug error: {str(e)}")
        return None
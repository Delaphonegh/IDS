# users/views.py
from flask import render_template,url_for,flash,redirect,request,Blueprint,session
from flask_login import login_user, current_user, logout_user, login_required
from structure import db,photos,mail ,app
from structure.models import User 
from structure.users.forms import RegistrationForm,LoginForm,UpdateUserForm
from structure.users.picture_handler import add_profile_pic
import secrets
import os
from requests.auth import HTTPBasicAuth
from flask_mail import Mail, Message
# from structure.core.views import generate_secure_password
from werkzeug.security import generate_password_hash
import string
import random
from datetime import datetime, timedelta
import requests
from urllib.parse import unquote
from itsdangerous import URLSafeTimedSerializer

users = Blueprint('users',__name__)


def generate_secure_password(length=12):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    secure_password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return secure_password


connex_username = os.environ.get('connex_username')
connex_password = os.environ.get('connex_password')
# register
# @users.route('/register',methods=['GET','POST'])
# def register():
#     form = RegistrationForm()
#     print("hghgj")
#     # if form.validate_on_submit():
#     if request.method == 'POST':
#         if form.plans.data != 1:
#             organization = Organization.query.filter_by(org_code=form.organization.data).first()
#             is_organization = True
#         else:
#             organization = None
#             is_organization = False
#         print("df")
#         user = User(email=form.email.data,
#                     name=form.name.data,
#                     username=form.username.data,
#                     password=form.password.data,
#                     last_name=form.last_name.data,role="user",
#                     number=form.number.data,organization_id=organization,is_organization=is_organization)

#         db.session.add(user)
#         db.session.commit()
#         flash('Thanks for registering!')
        
#         return redirect(url_for('chats',id=user.id))
            

#     return render_template('user/signup.html',form=form)







# @users.route('/', methods=['GET', 'POST'])
@users.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method =="POST":
        # Grab the user based on email or phone number
        user_input = form.email.data  # This can still be named 'email' for the input field
        user = User.query.filter((User.email == user_input) | (User.phone_number == user_input)).first()

        if user is not None:
            # Check if the entered password matches either the user's password or pin code
            password_is_valid = False
            
            # Check if the user has a password set
            if user.password_hash:  # Ensure the user has a password
                password_is_valid = user.check_password(form.password.data)

            # Allow login if the password is valid or if the pin code matches
            if password_is_valid or form.password.data == user.pin_code:
                # Log in the user
                session['name'] = user.name
                session['email'] = user.email
                session['id'] = user.id
                if user.is_organization:
                    session['organization'] = user.organization_id
                login_user(user)
                flash('Logged in successfully.')

                if user.role == "admin":
                    next = url_for('telafric.admin_rates')

                    return redirect(next)





                # If a user was trying to visit a page that requires a login
                next = request.args.get('next')

                # So let's now check if that next exists, otherwise we'll go to
                # the welcome page.
                if next is None or not next.startswith('/'):
                    next = url_for('telafric.dashboard')

                return redirect(next)
            else:
                session['loginmsg'] = "Invalid credentials. Try again"
                next = request.args.get('next')

                # So let's now check if that next exists, otherwise we'll go to
                # the welcome page.
                if next is None or not next.startswith('/'):
                    next = url_for('telafric.dashboard')

                return redirect(next)
        else:
            session['loginmsg'] = "Invalid credentials. Try again"
            next = request.args.get('next')

            # So let's now check if that next exists, otherwise we'll go to
            # the welcome page.
            if next is None or not next.startswith('/'):
                next = url_for('users.login')

            return redirect(next)
    return render_template('user/signin.html', form=form)



# logout
@users.route("/logout")
def logout():
    logout_user()
    session.pop('email',None)
    session.pop('name',None)
    session.pop('role',None)
    # session.pop('loginmsg',None)

    return redirect(url_for("users.login"))


# account (update UserForm)
# ... existing code ...
@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    userinfo = User.query.filter_by(id=session["id"]).first_or_404()

    if request.method == 'POST':
        # Directly handle form data from request
        username = request.form.get('username')
        email = request.form.get('email')
        name = request.form.get('name')
        number = request.form.get('number')
        # location = request.form.get('location')


        # Update user information
        userinfo.username = username
        userinfo.email = email
        userinfo.name = name
        userinfo.phone_number = number
        # userinfo.location = location


        # Commit changes to the database
        db.session.commit()
        flash('User Account Updated')
        return redirect(url_for('users.account'))

    # Pre-fill the form fields with current user info for GET request
    return render_template('ids/portal/profile.html', userinfo=userinfo)

# ... existing code ...


@users.route("/admin_account", methods=['GET', 'POST'])
@login_required
def admin_account():
    # Ensure the current user is an admin
    if not current_user.role == "admin":
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('users.login'))

    userinfo = User.query.filter_by(email=session["email"]).first_or_404()

    if request.method == 'POST':
        # Directly handle form data from request
        username = request.form.get('username')
        email = request.form.get('email')
        name = request.form.get('name')
        number = request.form.get('number')
        location = request.form.get('location')

        # Update user information
        userinfo.username = username
        userinfo.email = email
        userinfo.name = name
        userinfo.number = number
        userinfo.location = location

        # Commit changes to the database
        db.session.commit()
        flash('Admin Account Updated')
        return redirect(url_for('users.admin_account'))

    # Pre-fill the form fields with current user info for GET request
    return render_template('ids/admin/profile.html', userinfo=userinfo)





@users.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        pin = request.form.get('pin')
        country = request.form.get('country')
        number = request.form.get('number')
        if User.query.filter_by(email=email).first():
            print('Email already exists. Please use a different email.', 'danger')
            return redirect(url_for('users.register'))

        # Create a new user instance
        new_user = User(email=email, password=password, pin_code=pin, phone_number=number)
        new_user.password_hash = generate_password_hash(password)
        db.session.add(new_user)
        db.session.commit()

        # Send welcome email if email is provided
        if email:
            welcome_message = f"""
            Welcome to TelAfric!
            
            Your account has been created successfully.
            Thank you for joining our platform.
            
            Best regards,
            TelAfric Team
            """
            send_email(email, "Welcome to TelAfric!", welcome_message)

        # Send welcome SMS with PIN
        # if number:
        #     sms_url = "https://api.wirepick.com/httpsms/send"
        #     welcome_message = (
        #         f"Welcome to TelAfric! "
        #         f"Your PIN is: {pin}\n"
        #         "Visit our portal: https://ids-slw6.onrender.com/"
        #     )
        #     wirepick_key = os.environ.get('WIREPICK_KEY')
            
        #     sms_params = {
        #         'client': 'raymond',
        #         'password': wirepick_key,
        #         'phone': number,
        #         'text': welcome_message,
        #         'from': 'Delaphone'
        #     }
            
        #     try:
        #         sms_response = requests.get(sms_url, params=sms_params)
        #         print("Welcome SMS response:", sms_response.content)
        #     except Exception as e:
        #         print(f"Error sending welcome SMS: {str(e)}")

        flash('Signup successful! Please log in.', 'success')
        return redirect(url_for('users.login'))

    return render_template('user/signup.html')


@users.route("/change_pin", methods=['GET', 'POST'])
@login_required
def change_pin():
    if request.method == 'POST':
        current_pin = request.form.get('current_pin')
        new_pin = request.form.get('new_pin')
        confirm_new_pin = request.form.get('confirm_new_pin')

        userinfo = User.query.filter_by(id=session["id"]).first_or_404()

        # Check if the current PIN is correct
        if userinfo.pin_code != current_pin:
            flash('Current PIN is incorrect.', 'danger')
            return redirect(url_for('users.change_pin'))

        # Check if the new PIN and confirm PIN match
        if new_pin != confirm_new_pin:
            flash('New PIN and confirmation do not match.', 'danger')
            return redirect(url_for('users.change_pin'))

        # Validate PIN format
        if not new_pin.isdigit() or len(new_pin) != 4:
            flash('PIN must be exactly 4 digits.', 'danger')
            return redirect(url_for('users.change_pin'))

        # Update the user's PIN
        userinfo.pin_code = new_pin
        db.session.commit()
        flash('PIN changed successfully!', 'success')
        return redirect(url_for('users.account'))  # Redirect to account page

    return render_template('ids/portal/change_pin.html')

def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def send_email(to, subject, body):
    """Helper function to send emails"""
    msg = Message(subject,
                 sender='raymond@delaphonegh.com',
                 recipients=[to])
    msg.body = body
    mail.send(msg)

# Add new routes for password/PIN recovery
def get_reset_token_serializer():
    return URLSafeTimedSerializer(app.config['SECRET_KEY'])

@users.route("/forgot_password", methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Generate a secure token
            serializer = get_reset_token_serializer()
            reset_token = serializer.dumps(user.email, salt='password-reset-salt')
            
            # Create the reset link
            reset_url = url_for('users.reset_password', 
                              token=reset_token, 
                              _external=True)
            
            # Send recovery email
            recovery_message = f"""
            Hello,
            
            You have requested to reset your password. Click the link below to proceed:
            
            {reset_url}
            
            This link will expire in 1 hour.
            
            If you did not request this reset, please ignore this email.
            
            Best regards,
            TelAfric Team
            """
            try:
                send_email(email, "Password Reset Request", recovery_message)
                flash('Password reset link sent to your email!', 'success')
            except Exception as e:
                flash('Failed to send reset email. Please try again.', 'error')
            return redirect(url_for('users.login'))
        else:
            flash('Email not found.', 'error')
    
    return render_template('user/forgot_password.html')

@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    try:
        # Verify the reset token
        serializer = get_reset_token_serializer()
        email = serializer.loads(token, salt='password-reset-salt', max_age=3600)  # Token expires after 1 hour
    except:
        flash('The password reset link is invalid or has expired.', 'error')
        return redirect(url_for('users.forgot_password'))
    
    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('users.reset_password', token=token))
        
        user = User.query.filter_by(email=email).first()
        if user:
            user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            flash('Your password has been updated!', 'success')
            return redirect(url_for('users.login'))
        else:
            flash('User not found.', 'error')
            return redirect(url_for('users.forgot_password'))
    
    return render_template('user/reset_password.html')

@users.route("/forgot_pin", methods=['GET', 'POST'])
def forgot_pin():
    if request.method == 'POST':
        phone_number = request.form.get('phone_number')
        user = User.query.filter_by(phone_number=phone_number).first()
        
        if user:
            otp = generate_otp()
            session['pin_reset_otp'] = otp
            session['pin_reset_phone'] = phone_number
            session['pin_reset_expiry'] = (datetime.utcnow() + timedelta(minutes=5)).timestamp()
            
            # Send OTP via SMS
            sms_url = "https://api.wirepick.com/httpsms/send"
            otp_message = f"Your TelAfric PIN reset code is: {otp}. Valid for 5 minutes."
            
            wirepick_key = os.environ.get('WIREPICK_KEY')
            sms_params = {
                'client': 'raymond',
                'password': wirepick_key,
                'phone': phone_number,
                'text': otp_message,
                'from': 'Delaphone'
            }
            
            try:
                sms_response = requests.get(sms_url, params=sms_params)
                if sms_response.status_code == 200:
                    flash('OTP sent successfully to your phone!', 'success')
                    return redirect(url_for('users.verify_pin_otp'))
                else:
                    flash('Failed to send OTP. Please try again.', 'error')
            except Exception as e:
                flash('Failed to send OTP. Please try again.', 'error')
        else:
            flash('Phone number not found.', 'error')
    
    return render_template('user/forgot_pin.html')

@users.route("/verify_pin_otp", methods=['GET', 'POST'])
def verify_pin_otp():
    if request.method == 'POST':
        entered_otp = request.form.get('otp')
        stored_otp = session.get('pin_reset_otp')
        expiry = session.get('pin_reset_expiry')
        
        if not all([stored_otp, expiry]):
            flash('OTP session expired. Please request a new one.', 'error')
            return redirect(url_for('users.forgot_pin'))
        
        if datetime.utcnow().timestamp() > expiry:
            flash('OTP has expired. Please request a new one.', 'error')
            return redirect(url_for('users.forgot_pin'))
        
        if entered_otp == stored_otp:
            phone_number = session.pop('pin_reset_phone', None)
            session.pop('pin_reset_otp', None)
            session.pop('pin_reset_expiry', None)
            session['pin_reset_verified_phone'] = phone_number
            flash('OTP verified successfully!', 'success')
            return redirect(url_for('users.reset_pin'))
        else:
            flash('Invalid OTP. Please try again.', 'error')
    
    return render_template('user/verify_pin_otp.html')

@users.route("/reset_pin", methods=['GET', 'POST'])
def reset_pin():
    phone_number = session.get('pin_reset_verified_phone')
    if not phone_number:
        flash('Please start the PIN reset process again.', 'error')
        return redirect(url_for('users.forgot_pin'))
    
    if request.method == 'POST':
        new_pin = request.form.get('new_pin')
        confirm_pin = request.form.get('confirm_pin')
        
        if new_pin != confirm_pin:
            flash('PINs do not match.', 'error')
            return redirect(url_for('users.reset_pin'))
        
        user = User.query.filter_by(phone_number=phone_number).first()
        if user:
            user.pin_code = new_pin
            db.session.commit()
            session.pop('pin_reset_verified_phone', None)
            flash('PIN reset successfully!', 'success')
            return redirect(url_for('users.login'))
    
    return render_template('user/reset_pin.html')
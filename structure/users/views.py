# users/views.py
from flask import render_template,url_for,flash,redirect,request,Blueprint,session
from flask_login import login_user, current_user, logout_user, login_required
from structure import db,photos,mail 
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
    userinfo = User.query.filter_by(email=session["email"]).first_or_404()

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
        email = request.form['email']
        password = request.form['password']
        pin = request.form['pin']
        country = request.form['country']
        number = request.form['number']

        # Create a new user instance
        new_user = User(email=email, password=password, pin_code=pin, number=number)
        new_user.password_hash = generate_password_hash(password)  # Hash the password
        db.session.add(new_user)
        db.session.commit()

        # Send signup email notification
        # msg = Message("Welcome to Our Service!",
        #               recipients=[email])
        # msg.body = f"Hello {new_user.username},\n\nThank you for signing up! Your account has been created successfully.\n\nBest regards,\nYour Company Name"
        # mail.send(msg)

        flash('Signup successful! Please log in.', 'success')
        return redirect(url_for('users.login'))  # Redirect to login page after signup

    return render_template('user/signup.html')


@users.route("/change_pin", methods=['GET', 'POST'])
@login_required
def change_pin():
    if request.method == 'POST':
        current_pin = request.form.get('current_pin')
        new_pin = request.form.get('new_pin')
        confirm_new_pin = request.form.get('confirm_new_pin')

        userinfo = User.query.filter_by(email=session["email"]).first_or_404()

        # Check if the current PIN is correct
        if userinfo.pin_code != current_pin:
            flash('Current PIN is incorrect.', 'danger')
            return redirect(url_for('users.change_pin'))

        # Check if the new PIN and confirm PIN match
        if new_pin != confirm_new_pin:
            flash('New PIN and confirmation do not match.', 'danger')
            return redirect(url_for('users.change_pin'))

        # Update the user's PIN
        userinfo.pin_code = new_pin
        db.session.commit()
        flash('PIN changed successfully!', 'success')
        return redirect(url_for('users.account'))  # Redirect to account page or any other page

    return render_template('ids/portal/change_pin.html')
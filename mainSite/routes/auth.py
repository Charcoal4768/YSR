from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import generate_csrf, validate_csrf
from mainSite.models import User

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        csrf_token = request.form.get('csrf_token')
        # Handle login logic
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        # Check fields first
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('views.home'))
        flash('Login failed. Check your email and password.', 'danger')
    csrf_token = generate_csrf()
    return render_template('login.html', csrf_token=csrf_token)

@auth.route('/logout')
def logout():
    # Handle logout logic
    logout_user()
    return redirect(url_for('views.home'))

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        csrf_token = request.form.get('csrf_token')
        try:
            validate_csrf(csrf_token)
        except:
            flash('Invalid CSRF token.', 'danger')
            return redirect(url_for('auth.login'))
        # Handle signup logic
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        password2 = request.form['password2']
        #min length check for all fields
        if len(name) < 2 or len(email) < 5 or len(password) < 6:
            flash('Please fill out all fields correctly.', 'danger')
            return redirect(url_for('auth.signup'))
        if password != password2:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth.signup'))
        user = User.get_user_by_email(email)
        if user:
            flash('Email already registered. Please log in.', 'danger')
            return redirect(url_for('auth.login'))
        new_user = User.make_user(username=name, email=email, password=password)
        login_user(new_user)
        flash(f'Signed up as {email}! You can now add more details.', 'success')
        return redirect(url_for('views.home'))
    csrf_token = generate_csrf()
    return render_template('signup.html', csrf_token=csrf_token)

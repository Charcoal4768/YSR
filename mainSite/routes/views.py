from flask import Blueprint, render_template, redirect, url_for, request, session
from flask_wtf.csrf import generate_csrf, validate_csrf, CSRFError
from flask_login import login_required, current_user
from secrets import token_urlsafe
from mainSite import csrf, socket
from mainSite.models import Product
views = Blueprint('views', __name__)

@views.route('/', methods=['GET'])
def home():
    csrf_token = generate_csrf()
    return render_template('home.html', csrf_token=csrf_token, current_user=current_user)

@views.route('/more', methods=['GET'])
def more():
    return render_template('more.html', current_user=current_user)

@views.route('/contact', methods=['GET'])
def contact():
    return render_template('contact.html', current_user=current_user)

@views.route('/admin/products', methods=['GET'])
def admin_panel():
    csrf_token = generate_csrf()
    return render_template('admin/products.html', products = Product.query.all(), current_user=current_user, csrf_token=csrf_token)

@views.route('/home', methods=['GET'])
def redirect_home():
    return redirect(url_for('views.home'))
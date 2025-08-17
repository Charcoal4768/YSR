from flask import Blueprint, render_template, redirect, url_for, request, session
from flask_wtf.csrf import generate_csrf, validate_csrf, CSRFError
from secrets import token_urlsafe
from . import csrf, socket
views_bp = Blueprint('views', __name__)

@views_bp.route('/')
def home():
    csrf_token = generate_csrf()
    return render_template('home.html', csrf_token=csrf_token)

@views_bp.route('/more')
def more():
    return render_template('more.html')

@views_bp.route('/contact')
def contact():
    return render_template('contact.html')

@views_bp.route('/admin/products')
def admin_panel():
    return render_template('admin/products.html')

@views_bp.route('/home')
def redirect_home():
    return redirect(url_for('views.home'))
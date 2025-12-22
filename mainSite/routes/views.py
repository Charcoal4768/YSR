from flask import Blueprint, render_template, redirect, url_for, request, session
from flask_wtf.csrf import generate_csrf
from flask_login import current_user, login_required
from mainSite.models import Product, Tags
from sqlalchemy.orm import joinedload
views = Blueprint('views', __name__)

from flask import Blueprint, render_template, redirect, url_for, request, session
from flask_wtf.csrf import generate_csrf
from flask_login import current_user, login_required
from mainSite.models import Product, Tags
from sqlalchemy.orm import joinedload
views = Blueprint('views', __name__)

@views.route('/', methods=['GET','POST'])
def home():
    csrf_token = generate_csrf()
    return render_template('home.html',
                           csrf_token=csrf_token,
                           current_user=current_user,
                           tags_pagination={'page': 1, 'has_next': True})  # dummy


@views.route('/more', methods=['GET'])
def more():
    """
    Renders the 'more' page.
    """
    return render_template('more.html', current_user=current_user)

@views.route('/contact', methods=['GET'])
def contact():
    """
    Renders the contact page.
    """
    return render_template('contact.html', current_user=current_user)

@login_required
@views.route('/admin/products', methods=['GET'])
def admin_panel():
    """
    Renders the admin products panel.
    """
    if not current_user.is_authenticated or current_user.role != 'admin':
        return redirect(url_for('views.home'))
    csrf_token = generate_csrf()
    return render_template('admin/products.html',
                           current_user=current_user,
                           csrf_token=csrf_token,
                           products_pagination={'page': 1, 'has_next': True})  # dummy

@views.route('/home', methods=['GET'])
def redirect_home():
    """
    Redirects from /home to the root URL.
    """
    return redirect(url_for('views.home'))

# @views.route('/test', methods=['GET', 'POST'])
# def test_page():
#     """
#     Renders a test page for development purposes.
#     """
#     return render_template('testing.html', current_user=current_user)
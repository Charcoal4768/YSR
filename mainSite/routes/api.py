from email.mime.text import MIMEText
import os
import html
import random
import sqlite3
from secrets import token_urlsafe
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, json, request, current_app
from flask_login import login_required, current_user
from mainSite.services.storage_service_gcp import upload_and_optimize_file, delete_file_by_url
from mainSite.services.temporary_account_service import make_temp_account
from werkzeug.utils import secure_filename
from mainSite.models import Tags, Product
from mainSite import db, csrf
import smtplib, ssl
import dotenv

dotenv.load_dotenv()

api = Blueprint('api', __name__)
admin = os.environ.get("EMAIL_ADDR_ADMIN")
username = os.environ.get("EMAIL_ADDR")
password = os.environ.get("EMAIL_APP_PASS")

DB_PATH = os.path.join(os.path.dirname(__file__), 'tokens.db')
EXPIRATION_MINUTES = 60

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS publish_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token TEXT UNIQUE,
            created_at DATETIME
        )''')
        conn.execute('''CREATE TABLE IF NOT EXISTS otp_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            otp TEXT,
            email TEXT,
            created_at DATETIME
        )''')

init_db()

def issue_publish_token():
    token = token_urlsafe(32)
    created_at = datetime.utcnow()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT INTO publish_tokens (token, created_at) VALUES (?, ?)" , (token, created_at))
    return token

def verify_publish_token(token: str) -> bool:
    if not token:
        return False
    cutoff = datetime.utcnow() - timedelta(minutes=EXPIRATION_MINUTES)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM publish_tokens WHERE created_at < ?", (cutoff,))
        cur = conn.execute("SELECT id FROM publish_tokens WHERE token=?", (token,))
        if cur.fetchone() is not None:
            # Token is valid, now delete it
            conn.execute("DELETE FROM publish_tokens WHERE token=?", (token,))
            return True
        else:
            return False

def store_otp(email: str, otp: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT INTO otp_codes (otp, email, created_at) VALUES (?, ?, ?)" , (otp, email, datetime.utcnow()))

def verify_otp(email: str, otp: str, expiry_minutes=10) -> bool:
    cutoff = datetime.utcnow() - timedelta(minutes=expiry_minutes)
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("SELECT id FROM otp_codes WHERE email=? AND otp=? AND created_at >= ?", (email, otp, cutoff))
        if cur.fetchone() is not None:
            conn.execute("DELETE FROM otp_codes WHERE email=? AND otp=?", (email, otp))
            return True
        return False

# ---- Helper Functions ----
def mask_string(s: str, start: int = 1, end: int = None, mask_until: str = None) -> str:
    if not isinstance(s, str) or not s:
        return ""

    if end is not None:
        if start >= 0 and start < end and end <= len(s):
            return s[:start] + '*' * (end - start) + s[end:]
        else:
            return s

    if mask_until is not None:
        if start == 1 and len(s) >= 3:
            start = 2
        end = s.find(mask_until, start)
        if end == -1 or len(s) < 2:
            return s
    else:
        at_index = s.find('@')
        if at_index == -1 or len(s) < 2:
            return s
        end = at_index
        start = 1

    return s[:start] + '*' * (end - start) + s[end:]

def format_message_admin(name:str, recipient: str, message: str, address: str, address2: str, phone: str):
    """Formats the email body for the admin."""
    escaped_message = html.escape(message)
    email_template = f"""<!doctype html><html xmlns=http://www.w3.org/1999/xhtml><meta content="text/html; charset=UTF-8" http-equiv=Content-Type><meta content="width=device-width,initial-scale=1" name=viewport><title>New Quote Request</title><body style=margin:0;padding:0;background-color:#f5f5f5;font-family:Arial,sans-serif;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%><table align=center border=0 cellpadding=0 cellspacing=0 role=presentation style=border-collapse:collapse width=100%><tr><td style="padding:40px 0" align=center><table align=center border=0 cellpadding=0 cellspacing=0 role=presentation style="width:100%;max-width:600px;background-color:#fff;border-radius:12px;box-shadow:0 4px 8px rgba(0,0,0,.05);border-spacing:0;border-collapse:collapse" class=container-table><tr><td style="text-align:center;padding:24px 20px;border-bottom:1px solid #e0e0e0" class=header><h1 style=color:#333;font-size:24px;margin:0>New Quote Request</h1><tr><td style=padding:20px class=content><p style="color:#555;font-size:16px;line-height:1.6;margin:0 0 16px">A new quote has been requested by a user.<p style="color:#555;font-size:16px;line-height:1.6;margin:0 0 16px"><strong><span style=color:#333>Name:</span></strong> {name}<p style="color:#555;font-size:16px;line-height:1.6;margin:0 0 16px"><strong><span style=color:#333>Recipient:</span></strong> {recipient}<p style="color:#555;font-size:16px;line-height:1.6;margin:0 0 16px"><strong><span style=color:#333>Address Line 1:</span></strong> {address}<p style="color:#555;font-size:16px;line-height:1.6;margin:0 0 16px"><strong><span style=color:#333>Address Line 2:</span></strong> {address2}<p style="color:#555;font-size:16px;line-height:1.6;margin:0 0 16px"><strong><span style=color:#333>Phone:</span></strong> {phone}<p style="color:#555;font-size:16px;line-height:1.6;margin:0 0 16px"><strong><span style=color:#333>Email:</span></strong> {recipient}<div class=message-box style="background-color:#f9f9f9;border:1px solid #e0e0e0;border-radius:8px;padding:16px;margin-top:16px"><p style="font-style:italic;color:#666;margin:0 0 16px"><strong><span style=font-style:normal;color:#333>Message:</span></strong><p style=font-style:italic;color:#666;margin:0>{escaped_message}</div></table></table>"""
    return email_template


def format_message_user(recipient:str, phone:str, mail:str, message:str):
    """Formats the email body for the user with masked info."""
    email = mask_string(mail, mask_until="@")
    phone = mask_string(phone, start=2, end=6)
    snippet = message[:100] + ("..." if len(message) > 1 else "You didn't type anything here")
    email_template = f"""<!doctype html><html xmlns=http://www.w3.org/1999/xhtml><meta content="text/html; charset=UTF-8"http-equiv=Content-Type><meta content="width=device-width,initial-scale=1"name=viewport><title>Quote Request Received</title><body style=margin:0;padding:0;background-color:#f5f5f5;font-family:Arial,sans-serif;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%><table align=center border=0 cellpadding=0 cellspacing=0 role=presentation style=border-collapse:collapse width=100%><tr><td style="padding:40px 0"align=center><table align=center border=0 cellpadding=0 cellspacing=0 role=presentation style="width:100%;max-width:600px;background-color:#fff;border-radius:12px;box-shadow:0 4px 8px rgba(0,0,0,.05);border-spacing:0;border-collapse:collapse"class=container-table><tr><td style="text-align:center;padding:24px 20px;border-bottom:1px solid #e0e0e0"class=header><h1 style=color:#333;font-size:24px;margin:0>Thanks for your Quote Request!</h1><tr><td style=padding:20px class=content><p style="color:#555;font-size:16px;line-height:1.6;margin:0 0 16px">Hi, we have received your request for a quotation. An admin will reach out to you soon!<div class=collected-info-box style="background-color:#f9f9f9;border:1px solid #e0e0e0;border-radius:8px;padding:16px;margin-top:24px"><p style="color:#666;font-size:14px;margin:0 0 8px;line-height:1.5;font-weight:700">Information we collected:<p style="font-size:14px;margin:0 0 8px;color:#555"><strong>Phone:</strong> {phone}<p style="font-size:14px;margin:0 0 8px;color:#555"><strong>Email:</strong> {email}<p style="font-size:14px;margin:0 0 8px;color:#555"><strong>Your Message Snippet:</strong><p style=font-style:italic;color:#666;font-size:14px;margin:0;line-height:1.5>"{snippet}"</div></table></table>"""
    return email_template

def send_to(recipient, subject, body):
    port = 465
    context = ssl.create_default_context()
    try:
        msg = MIMEText(body, 'html')
        msg['Subject'] = subject
        msg['From'] = username
        msg['To'] = recipient
        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login(username, password)
            server.sendmail(username, recipient, msg.as_string())
            print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

# --- Routes using token verification ---
@api.route('/api/request_new_token', methods=['GET'])
@login_required
def request_new_token():
    if not current_user.is_authenticated or current_user.role != 'admin':
        return jsonify({"error": "Unauthorized"}), 401
    token = issue_publish_token()
    return jsonify({"publish_token": token})

@api.route('/api/unauth_token', methods=['GET'])
def unauth_token():
    token = issue_publish_token()
    return jsonify({"publish_token": token})

@api.route('/api/send_email', methods=['POST','GET'])
def send_email():
    try:
        auth_header = request.headers.get("Publish-Token", "")
        if not verify_publish_token(auth_header):
            return jsonify({"error": "CSRF token missing or invalid"}), 403
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        name = html.escape(data.get("name", ""))
        message = html.escape(data.get("message", ""))
        recipient = html.escape(data.get("recipient", ""))
        address1 = html.escape(data.get("address1", "N/A"))
        address2 = html.escape(data.get("address2", "N/A"))
        phone = html.escape(data.get("phone", "N/A"))

        if not recipient:
            return jsonify({"error": "Missing email field"}), 400

        escaped_address = f"{address1}\n{address2}" if address2 != "N/A" else address1
        make_temp_account({"name": name, "email": recipient, "phone": phone, "address": escaped_address})

        # Import local functions correctly
        from . import api as this_module

        message_ad = this_module.format_message_admin(name, recipient, message, address1, address2, phone)
        send_to(admin, "New Quote Request", message_ad)

        message_us = this_module.format_message_user(recipient, phone, recipient, message)
        send_to(recipient, "Quote Request Received", message_us)

        return jsonify({"success": True})

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": str(e)}), 500

@csrf.exempt
@api.route('/api/publish_product', methods=['POST'])
@login_required
def publish_product():
    if not current_user.is_authenticated or current_user.role != 'admin':
        return jsonify({"error": "Unauthorized"}), 401
    auth_header = request.headers.get("Publish-Token", "")
    if not verify_publish_token(auth_header):
        return jsonify({"error": "CSRF token missing or invalid"}), 403

    name = request.form.get("name")
    description = request.form.get("description")
    tags_json = request.form.get("tags", "[]")
    tags = json.loads(tags_json)
    image = request.files.get("image")

    if not name or not description:
        return jsonify({"error": "Missing product data"}), 400
    if not image:
        return jsonify({"error": "Image is required"}), 400

    try:
        validFileName = secure_filename(image.filename)
        authorizedFileUrl = upload_and_optimize_file(image, validFileName)
        new_product = Product.add_product(name=name, description=description, image_url=authorizedFileUrl, tags=tags)
        return jsonify({"success": True, "product": new_product.to_dict()}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    
@csrf.exempt
@api.route('/api/edit_product/<int:product_id>', methods=['POST'])
@login_required
def edit_product(product_id):
    if not current_user.is_authenticated or current_user.role != 'admin':
        return jsonify({"error": "Unauthorized"}), 401
    auth_header = request.headers.get("Publish-Token", "")
    if not verify_publish_token(auth_header):
        return jsonify({"error": "Publish token missing or invalid"}), 403

    product = Product.get_product_by_id(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    name = request.form.get("name")
    description = request.form.get("description")
    tags_json = request.form.get("tags", "[]")
    tags = json.loads(tags_json)
    image = request.files.get("image")
    
    image_url = product.image_url

    if image:
        delete_file_by_url(product.image_url)
        try:
            validFileName = secure_filename(image.filename)
            image_url = upload_and_optimize_file(image, validFileName)
        except Exception as e:
            return jsonify({"success": False, "error": f"Failed to upload new image: {e}"}), 500

    try:
        updated_product = Product.edit_product(
            product_id=product_id,
            name=name,
            description=description,
            image_url=image_url,
            tags=tags
        )
        return jsonify({"success": True, "product": updated_product.to_dict()}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@csrf.exempt
@api.route('/api/delete_product/<int:product_id>', methods=['DELETE'])
@login_required
def delete_product_api(product_id):
    if not current_user.is_authenticated or current_user.role != 'admin':
        return jsonify({"error": "Unauthorized"}), 401
    auth_header = request.headers.get("Publish-Token", "")
    if not verify_publish_token(auth_header):
        return jsonify({"error": "Publish token missing or invalid"}), 403

    product = Product.get_product_by_id(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    delete_file_by_url(product.image_url)
    
    if Product.delete_product(product_id):
        return jsonify({"success": True, "message": "Product deleted"}), 200
    else:
        return jsonify({"success": False, "error": "Failed to delete product from database"}), 500

@api.route('/api/generate_otp', methods=['POST'])
def generate_otp():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({"error": "Email required"}), 400
    otp = str(random.randint(100000, 999999))
    store_otp(email, otp)
    # send email using send_to(email, ...)
    return jsonify({"success": True, "otp": otp})

@api.route('/api/products')
def get_products_grouped_by_tags():
    """ Returns a paginated list of categories, each with all their products.
    One page = N categories, with full product lists. """
    page = request.args.get('page', 1, type=int)
    per_page = 1
    tags_pagination = Tags.query.paginate(page=page, per_page=per_page, error_out=False)
    categories = []
    for tag in tags_pagination.items:
        products = Product.query.join(Product.tags).filter(Tags.id == tag.id).all()
        categories.append({
            'name': tag.name,
            'products': [
                {
                    'name': product.name,
                    'description': product.description,
                    'image_url': product.image_url,
                    'tags': [t.name for t in product.tags]
                } for product in products
            ]
        })
    return jsonify({'categories': categories, 'has_next': tags_pagination.has_next})

@api.route('/api/products_all')
def get_all_products_paginated():
    """Returns a paginated list of all products for the admin panel."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    products_pagination = Product.query.order_by(Product.id.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    products_list = [
        {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'image_url': product.image_url,
            'tags': [tag.name for tag in product.tags]
        }
        for product in products_pagination.items
    ]
    return jsonify({
        'products': products_list,
        'has_next': products_pagination.has_next,
        'page': products_pagination.page,
        'per_page': products_pagination.per_page,
        'total': products_pagination.total
    })

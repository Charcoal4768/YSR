from email.mime.text import MIMEText
import os
import html
import random
from secrets import token_urlsafe
from flask import Blueprint, jsonify, json, request, session
from flask_login import login_required, current_user
from mainSite.services.storage_service_gcp import upload_file
from mainSite.services.temporary_account_service import make_temp_account
from werkzeug.utils import secure_filename
from mainSite.models import Tags, User, Product, product_tags
from mainSite import db, csrf
import smtplib, ssl
import dotenv
dotenv.load_dotenv()

api = Blueprint('api', __name__)
admin = os.environ.get("EMAIL_ADDR_ADMIN")
username = os.environ.get("EMAIL_ADDR")
password = os.environ.get("EMAIL_APP_PASS")

def issue_publish_token():
    """Generates and stores a unique token for API publishing."""
    token = token_urlsafe(32)
    session['publish_token'] = token
    return token

def mask_string(s: str, start: int = 1, end: int = None, mask_until: str = None) -> str:
    """
    Masks a string based on either a static range or a dynamic delimiter.
    Handles None and non-string inputs gracefully.
    """
    if not isinstance(s, str) or not s:
        return ""

    if end is not None:
        if start >= 0 and start < end and end <= len(s):
            first_part = s[:start]
            masked_part = '*' * (end - start)
            last_part = s[end:]
            return first_part + masked_part + last_part
        else:
            return s

    if mask_until is not None:
        if start == 1 and len(s) >= 3:
            start = 2
        
        end = s.find(mask_until, start)
        
        if end == -1 or len(s) < 2:
            return s
            
    elif mask_until is None:
        at_index = s.find('@')
        if at_index == -1 or len(s) < 2:
            return s
        end = at_index
        start = 1
        
    if end is not None and start >= 0 and start < end and end <= len(s):
        first_part = s[:start]
        masked_part = '*' * (end - start)
        last_part = s[end:]
        return first_part + masked_part + last_part
    
    return s

def send_to(recipient, subject, body):
    """Sends an email using a secure SSL connection with HTML content."""
    port = 465
    context = ssl.create_default_context()
    try:
        # Create a MIMEText object with HTML content
        msg = MIMEText(body, 'html')
        msg['Subject'] = subject
        msg['From'] = username
        msg['To'] = recipient
        
        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login(username, password)
            # The .as_string() method formats the message correctly for sending
            server.sendmail(username, recipient, msg.as_string())
            print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

def format_message_admin(name:str, recipient: str, message: str, address: str, address2: str, phone: str):
    """Formats the email body for the admin."""
    escaped_message = html.escape(message)
    email_template = f"""<!doctype html><html xmlns=http://www.w3.org/1999/xhtml><meta content="text/html; charset=UTF-8" http-equiv=Content-Type><meta content="width=device-width,initial-scale=1" name=viewport><title>New Quote Request</title><body style=margin:0;padding:0;background-color:#f5f5f5;font-family:Arial,sans-serif;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%><table align=center border=0 cellpadding=0 cellspacing=0 role=presentation style=border-collapse:collapse width=100%><tr><td style="padding:40px 0" align=center><table align=center border=0 cellpadding=0 cellspacing=0 role=presentation style="width:100%;max-width:600px;background-color:#fff;border-radius:12px;box-shadow:0 4px 8px rgba(0,0,0,.05);border-spacing:0;border-collapse:collapse" class=container-table><tr><td style="text-align:center;padding:24px 20px;border-bottom:1px solid #e0e0e0" class=header><h1 style=color:#333;font-size:24px;margin:0>New Quote Request</h1><tr><td style=padding:20px class=content><p style="color:#555;font-size:16px;line-height:1.6;margin:0 0 16px">A new quote has been requested by a user.<p style="color:#555;font-size:16px;line-height:1.6;margin:0 0 16px"><strong><span style=color:#333>Name:</span></strong> {name}<p style="color:#555;font-size:16px;line-height:1.6;margin:0 0 16px"><strong><span style=color:#333>Recipient:</span></strong> {recipient}<p style="color:#555;font-size:16px;line-height:1.6;margin:0 0 16px"><strong><span style=color:#333>Address Line 1:</span></strong> {address}<p style="color:#555;font-size:16px;line-height:1.6;margin:0 0 16px"><strong><span style=color:#333>Address Line 2:</span></strong> {address2}<p style="color:#555;font-size:16px;line-height:1.6;margin:0 0 16px"><strong><span style=color:#333>Phone:</span></strong> {phone}<p style="color:#555;font-size:16px;line-height:1.6;margin:0 0 16px"><strong><span style=color:#333>Email:</span></strong> {recipient}<div class=message-box style="background-color:#f9f9f9;border:1px solid #e0e0e0;border-radius:8px;padding:16px;margin-top:16px"><p style="font-style:italic;color:#666;margin:0 0 16px"><strong><span style=font-style:normal;color:#333>Message:</span></strong><p style=font-style:italic;color:#666;margin:0>{escaped_message}</div></table></table>"""
    return email_template

def format_message_user(recipient:str, phone:str, mail:str, message:str):
    """Formats the email body for the user with masked info."""
    email = mask_string(mail, mask_until="@")
    phone = mask_string(phone, start=2, end=6)
    snippet = message[:100] + ("..." if len(message) > 100 else "You didn't type anything here")
    email_template = f"""<!doctypehtml><html xmlns=http://www.w3.org/1999/xhtml><meta content="text/html; charset=UTF-8"http-equiv=Content-Type><meta content="width=device-width,initial-scale=1"name=viewport><title>Quote Request Received</title><body style=margin:0;padding:0;background-color:#f5f5f5;font-family:Arial,sans-serif;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%><table align=center border=0 cellpadding=0 cellspacing=0 role=presentation style=border-collapse:collapse width=100%><tr><td style="padding:40px 0"align=center><table align=center border=0 cellpadding=0 cellspacing=0 role=presentation style="width:100%;max-width:600px;background-color:#fff;border-radius:12px;box-shadow:0 4px 8px rgba(0,0,0,.05);border-spacing:0;border-collapse:collapse"class=container-table><tr><td style="text-align:center;padding:24px 20px;border-bottom:1px solid #e0e0e0"class=header><h1 style=color:#333;font-size:24px;margin:0>Thanks for your Quote Request!</h1><tr><td style=padding:20px class=content><p style="color:#555;font-size:16px;line-height:1.6;margin:0 0 16px">Hi, we have received your request for a quotation. An admin will reach out to you soon!<div class=collected-info-box style="background-color:#f9f9f9;border:1px solid #e0e0e0;border-radius:8px;padding:16px;margin-top:24px"><p style="color:#666;font-size:14px;margin:0 0 8px;line-height:1.5;font-weight:700">Information we collected:<p style="font-size:14px;margin:0 0 8px;color:#555"><strong>Phone:</strong> {phone}<p style="font-size:14px;margin:0 0 8px;color:#555"><strong>Email:</strong> {email}<p style="font-size:14px;margin:0 0 8px;color:#555"><strong>Your Message Snippet:</strong><p style=font-style:italic;color:#666;font-size:14px;margin:0;line-height:1.5>"{snippet}"</div></table></table>"""
    return email_template

def format_otp_email(otp):
    """Generates an HTML email for an OTP."""
    email_template = f"""<!doctype html><html xmlns=http://www.w3.org/1999/xhtml><meta content="text/html; charset=UTF-8" http-equiv=Content-Type><meta content="width=device-width,initial-scale=1" name=viewport><title>Your OTP Code</title><body style=margin:0;padding:0;background-color:#f5f5f5;font-family:Arial,sans-serif;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%><table align=center border=0 cellpadding=0 cellspacing=0 role=presentation style=border-collapse:collapse width=100%><tr><td style="padding:40px 0" align=center><table align=center border=0 cellpadding=0 cellspacing=0 role=presentation style="width:100%;max-width:600px;background-color:#fff;border-radius:12px;box-shadow:0 4px 8px rgba(0,0,0,.05);border-spacing:0;border-collapse:collapse" class=container-table><tr><td style="text-align:center;padding:24px 20px;border-bottom:1px solid #e0e0e0" class=header><h1 style=color:#333;font-size:24px;margin:0>Your One-Time Password (OTP)</h1><tr><td style=padding:20px class=content><p style="color:#555;font-size:16px;line-height:1.6;margin:0 0 16px">Use the following OTP to complete your action. This code is valid for the next 10 minutes.<div class=otp-box style="background-color:#f9f9f9;border:1px solid #e0e0e0;border-radius:8px;padding:16px;margin-top:16px;text-align:center"><span style="font-size:24px;font-weight:bold;color:#333;letter-spacing:4px">{otp}</span></div><p style="color:#999;font-size:12px;line-height:1.6;margin-top:24px">If you did not request this code, please ignore this email.</table></table>"""
    return email_template

def gen_OTP_email():
    """Generates a one-time password and sends an email with it."""
    otp = random.randint(100000, 999999)
    email_content = format_otp_email(otp)
    #Note for future me: hook this up to redis to manage otp expiriation and stuff, or do some postgres shit
    send_to("user@example.com", "Your OTP Code", email_content)

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
        # CSRF token validation
        auth_header = request.headers.get("Publish-Token", "")
        token = session.get("publish_token")
        if not token or auth_header != token:
            return jsonify({"error": "CSRF token missing or invalid"}), 403
        
        # Safely retrieve form data as a JSON object
        data = request.get_json()
        print(data)
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        name = html.escape(data.get("name", ""))
        message = html.escape(data.get("message", ""))
        recipient = html.escape(data.get("recipient", ""))
        address1 = html.escape(data.get("address1", "N/A"))
        address2 = html.escape(data.get("address2", "N/A"))
        phone = html.escape(data.get("phone", "N/A"))

        # Basic validation for essential fields after retrieval
        if not recipient:
            return jsonify({"error": "Missing email field"}), 400
        
        # Merge addresses
        escaped_address = f"{address1}\n{address2}" if address2 != "N/A" else address1
        
        # Create temporary account
        make_temp_account({"name": name, "email": recipient, "phone": phone, "address": escaped_address})

        # Send admin and user emails
        try:
            message_ad = format_message_admin(name, recipient, message, address1, address2, phone)
            send_to(admin, "New Quote Request", message_ad)
        except Exception as e:
            return jsonify({"error": "Failed to send email to admin"}), 500

        try:
            message_us = format_message_user(recipient, phone, recipient, message)
            send_to(recipient, "Quote Request Received", message_us)
        except Exception as e:
            return jsonify({"error": "Failed to send email"}), 500

        print("Proccess done successfully")
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
    token = session.get("publish_token")
    print(token)
    if not token or auth_header != token:
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
        authorizedFileUrl = upload_file(image, validFileName)
        new_product = Product.add_product(name=name, description=description, image_url=authorizedFileUrl, tags=tags)
        return jsonify({"success": True, "product": new_product.to_dict()}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    
@api.route('/api/products')
def get_products_grouped_by_tags():
    """
    Returns a paginated list of categories, each with all their products.
    One page = N categories, with full product lists.
    """
    page = request.args.get('page', 1, type=int)
    per_page = 2
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
                }
                for product in products
            ]
        })
    return jsonify({'categories': categories, 'has_next': tags_pagination.has_next})

import os
from secrets import token_urlsafe
from flask import Blueprint, jsonify, json, request, session
from flask_login import login_required, current_user
from mainSite.services.storage_service_gcp import upload_file
from mainSite.services.temporary_account_service import make_temp_account
from werkzeug.utils import secure_filename
from mainSite.models import Tags, User, Product, product_tags
from mainSite import db, csrf
from sqlalchemy.orm import joinedload
import smtplib
import dotenv
dotenv.load_dotenv()

api = Blueprint('api', __name__)
recipient = os.environ.get("EMAIL_RECIPIENT")
username = os.environ.get("EMAIL_USERNAME")
password = os.environ.get("EMAIL_PASSWORD")

def issue_publish_token():
    token = token_urlsafe(32)
    session['publish_token'] = token
    return token

@api.route('/api/request_new_token', methods=['GET'])
@login_required
def request_new_token():
    if not current_user.is_authenticated or current_user.role != 'admin':
        return jsonify({"error": "Unauthorized"}), 401
    token = issue_publish_token()
    return jsonify({"publish_token": token})

@api.route('/api/send_email', methods=['POST'])
# @login_required
def send_email():
    auth_header = request.headers.get("X-CSRF-Token", "")
    token = session.get("publish_token")
    if not token or auth_header != token:
        return jsonify({"error": "CSRF token missing or invalid"}), 403
    data = json.loads(request.data)
    message = data.get("message")
    subject = message[:78]
    make_temp_account(data)

    if not recipient or not subject or not message:
        return jsonify({"error": "Missing fields"}), 400

    try:
        with smtplib.SMTP("smtp.example.com") as server:
            server.login("username", "password")
            server.sendmail("from@example.com", recipient, f"Subject: {subject}\n\n{message}")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"success": True})

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

    # Now we get the data from request.form and the file from request.files
    name = request.form.get("name")
    description = request.form.get("description")
    tags_json = request.form.get("tags", "[]") # Get tags as JSON string
    tags = json.loads(tags_json)
    image = request.files.get("image")
    print(image)

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
    Returns a paginated list of products as JSON.
    """
    page = request.args.get('page', 1, type=int)
    per_page = 5  # Items per page
    
    # Use joinedload to eagerly load the products for each tag
    pagination = Tags.query.options(joinedload(Tags.product)).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    # Serialize the products and their tags into a JSON-friendly format
    product_list = {}
    # {category: [{product_data}, ...], category2: [{...}], ...}
    for tag in pagination.items:
        category = tag.name
        product_list[category] = []
        for product in tag.product:
            product_data = {
                'name': product.name,
                'description': product.description,
                'image_url': product.image_url,
                'tags': [p_tag.name for p_tag in product.tags]
            }
            product_list[category].append(product_data)

    return jsonify({
        'categories': product_list,
        'has_next': pagination.has_next
    })

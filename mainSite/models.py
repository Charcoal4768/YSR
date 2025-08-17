from . import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(150), nullable=False)
    address = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'
    
    @classmethod
    def get_user_by_email(cls, email:str):
        return cls.query.filter_by(email=email).first()
    @classmethod
    def get_user_by_id(cls, user_id:int):
        return cls.query.get(user_id)
    @classmethod
    def make_user(cls, email:str, username:str, password:str, phone:str=None, address:str=None):
        user = cls(email=email, username=username, password=password, phone=phone, address=address)
        db.session.add(user)
        db.session.commit()
        return user
    @classmethod
    def edit_user(cls, user_id:int, email:str=None, username:str=None, password:str=None, phone:str=None, address:str=None):
        user = cls.get_user_by_id(user_id)
        if user:
            if email:
                user.email = email
            if username:
                user.username = username
            if password:
                user.password = password
            if phone:
                user.phone = phone
            if address:
                user.address = address
            db.session.commit()
        return user

product_tags = db.Table('product_tags',
                        db.Column('product_id', db.Integer, db.ForeignKey('products.id'), primary_key=True),
                        db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True))

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    tags = db.relationship('Tag', secondary='product_tags', back_populates='products')

    def __repr__(self):
        return f'<Product {self.name}>'
    
    @classmethod
    def get_product_by_id(cls, product_id:int):
        return cls.query.get(product_id)
    @classmethod
    def get_products_by_tag(cls, tag_name:str):
        return cls.query.join(product_tags).join(Tag).filter(Tag.name == tag_name).all()
    @classmethod
    def add_product(cls, image_url:str, name:str, description:str, tags:list):
        product = cls(image_url=image_url, name=name, description=description)
        product.tags.extend(tags)
        db.session.add(product)
        db.session.commit()
        return product
    @classmethod
    def edit_product(cls, product_id:int, image_url:str, name:str, description:str, tags:list):
        product = cls.get_product_by_id(product_id)
        if product:
            if image_url:
                product.image_url = image_url
            if name:
                product.name = name
            if description:
                product.description = description
            if tags:
                product.tags = tags
            db.session.commit()
        return product
    @classmethod
    def delete_product(cls, product_id:int):
        product = cls.get_product_by_id(product_id)
        if product:
            db.session.delete(product)
            db.session.commit()
            return True
        return False

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    products = db.relationship('Product', secondary='product_tags', back_populates='tags')
    def __repr__(self):
        return f'<Tag {self.name}>'
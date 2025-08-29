from . import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=True)
    phone = db.Column(db.String(150), nullable=True)
    address = db.Column(db.String(150), nullable=True)
    role = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f'<User {self.username}>'
    
    @classmethod
    def get_user_by_email(cls, email:str):
        return cls.query.filter_by(email=email).first()
    @classmethod
    def get_user_by_id(cls, user_id:int):
        return cls.query.get(user_id)
    @classmethod
    def make_user(cls, email:str, username:str, password:str, phone:str=None, address:str=None, role:str='user'):
        user = cls(email=email, username=username, password=password, phone=phone, address=address, role=role)
        db.session.add(user)
        db.session.commit()
        return user
    @classmethod
    def temp_user(cls, email:str, username:str, phone:str, address: str, role:str='temp'):
        user = cls(email=email, username=username, phone=phone, address=address, role=role)
        db.session.add(user)
        db.session.commit()
        return user
    @classmethod
    def temp_to_full_account(cls, temp_user, password:str):
        full_user = cls(
            email=temp_user.email,
            username=temp_user.username,
            password=password,
            phone=temp_user.phone,
            address=temp_user.address,
            role="user"
        )
        temp_user.delete(user_id=temp_user.id)
        db.session.add(full_user)
        db.session.commit()
        return full_user
    @classmethod
    def delete(cls, user_id:int):
        user = cls.get_user_by_id(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return True
        return False
    @classmethod
    def promote(cls, user_id:int, new_role:str):
        user = cls.get_user_by_id(user_id)
        if user:
            user.role = new_role
            db.session.commit()
            return True
        return False
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
                        db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True),
                        db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True))

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    tags = db.relationship('Tags', secondary='product_tags', back_populates='product', lazy='joined')

    def __repr__(self):
        return f'<Product {self.name}>'
        
    def to_dict(self):
        return {
            "id": self.id,
            "image_url": self.image_url,
            "name": self.name,
            "description": self.description,
            "tags": [tag.name for tag in self.tags]
        }
    
    @classmethod
    def get_product_by_id(cls, product_id:int):
        return cls.query.get(product_id)
        
    @classmethod
    def get_products_by_tag(cls, tag_name:str):
        return cls.query.join(product_tags).join(Tags).filter(Tags.name == tag_name).all()
        
    @classmethod
    def add_product(cls, image_url:str, name:str, description:str, tags:list):
        product = cls(image_url=image_url, name=name, description=description)
        tag_objects = []
        unique_tags = list(set(tags))

        for tag_str in unique_tags:
            tag = Tags.query.filter_by(name=tag_str).first()
            if not tag:
                tag = Tags(name=tag_str)
                db.session.add(tag)
            tag_objects.append(tag)
        product.tags.extend(tag_objects)
        db.session.add(product)
        db.session.commit()
        return product
        
    @classmethod
    def edit_product(cls, product_id:int, name:str=None, description:str=None, image_url:str=None, tags:list=None):
        product = cls.get_product_by_id(product_id)
        if product:
            if image_url:
                product.image_url = image_url
            if name:
                product.name = name
            if description:
                product.description = description
            if tags is not None:
                product.tags.clear() # Remove existing tags
                tag_objects = []
                unique_tags = list(set(tags))

                for tag_str in unique_tags:
                    tag = Tags.query.filter_by(name=tag_str).first()
                    if not tag:
                        tag = Tags(name=tag_str)
                        db.session.add(tag)
                    tag_objects.append(tag)
                product.tags.extend(tag_objects)
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

class Tags(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    product = db.relationship('Product', secondary='product_tags', back_populates='tags')
    def __repr__(self):
        return f'<Tag {self.name}>'

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(250))
    quantity = db.Column(db.Integer, default=0, nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=True)

    def __repr__(self):
        return f"<Product {self.id} {self.name}>"

class Location(db.Model):
    __tablename__ = 'location'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(250))
    # relationship to products so we can count products per location easily
    products = db.relationship('Product', backref='location', lazy='dynamic')

    def __repr__(self):
        return f"<Location {self.id} {self.name}>"

class ProductMovement(db.Model):
    __tablename__ = 'product_movement'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    from_location = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=True)
    to_location = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    qty = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Movement {self.id} P:{self.product_id} {self.from_location}->{self.to_location} Q:{self.qty}>"

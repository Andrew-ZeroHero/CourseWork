from initial import *

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False, unique=True)
    birth_date = db.Column(db.Date, nullable=False)
    login = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='outsider')  # outsider, manager, courier

class Delivery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), nullable=False)  # 'waiting', 'in_process', 'delivered'
    address = db.Column(db.String(200), nullable=False)
    customer_phone = db.Column(db.String(15), nullable=False)
    order_number = db.Column(db.String(100), nullable=False)
    order_content = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DeliveryLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    delivery_id = db.Column(db.Integer, db.ForeignKey('delivery.id'), nullable=False)
    courier_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    delivery_date = db.Column(db.DateTime, default=datetime.utcnow)
    confirmation_date = db.Column(db.DateTime)
    confirmed = db.Column(db.Boolean, default=False)

    delivery = db.relationship('Delivery', backref='logs')
    courier = db.relationship('User', backref='deliveries')

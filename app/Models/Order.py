from .. import db
from .ProductsOrder import ProductsOrders
from app.exceptions import ValidationError


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float, nullable=False)
    manufacturing_date = db.Column(db.Date)
    manufacturing_time = db.Column(db.Time)

    products = db.relationship('Product',
                               secondary=ProductsOrders.__tablename__,
                               backref=db.backref('orders', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan',
                               single_parent=True)

    def to_json(self):
        json_order = {
            'url': url_for('api.get_order', id=self.id),
            'price': self.price,
            'manufacturing_date': self.manufacturing_date,
            'manufacturing_time': self.manufacturing_time,
            'products': self.products
        }
        return json_order

    @staticmethod
    def from_json(json_order):
        price = json_order.get('price')
        manufacturing_date = json_order.get('manufacturing_date')
        manufacturing_time = json_order.get('manufacturing_time')
        products = json_order.get('products')
        Order.check_order_details(price, manufacturing_time, manufacturing_date, products)  # raise ValidationError
        return Order(price=price,
                     manufacturing_time=manufacturing_time,
                     manufacturing_date=manufacturing_date,
                     products=products)

    @staticmethod
    def check_order_details(price, date, time, products):
        if price is None or price == '':
            raise ValidationError('Price does not have a detail')
        elif date is None or date == '':
            raise ValidationError('Date does not have a  detail')
        elif time is None or time == '':
            raise ValidationError('Time does not have a  detail')
        elif products is None:
            raise ValidationError('Products does not have a  detail')

    def __init__(self, **kwargs):
        super(Order, self).__init__(**kwargs)
        if self.products is not None:
            self.calc_total_price(self)

    @staticmethod
    def calc_total_price(target):
        price = 0
        for product in target.products:
            price += product.price
        target.price = price

    def __repr__(self):
        return '<Order %r>' % self.id


db.event.listen(Order.products, 'set', Order.calc_total_price)

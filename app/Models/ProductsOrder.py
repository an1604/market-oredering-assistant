from .. import db
from ..exceptions import ValidationError


class ProductsOrders(db.Model):
    __tablename__ = 'productOrder'
    order_id = db.Column('order_id', db.Integer, db.ForeignKey('orders.id'),
                         primary_key=True)
    product_id = db.Column('product_id', db.Integer, db.ForeignKey('products.id'),
                           primary_key=True)

    def to_json(self):
        products_order_json = {
            'order_id': self.order_id,
            'product_id': self.product_id
        }
        return products_order_json

    @staticmethod
    def from_json(json_products_order):
        order_id = json_products_order.get('order_id')
        product_id = json_products_order.get('product_id')

        ProductsOrders.check_details(order_id, product_id)
        return ProductsOrders(product_id=product_id,
                              order_id=order_id)

    @staticmethod
    def check_details(order_id, product_id):
        if product_id is None or product_id == '':
            raise ValidationError('product does not have a detail')
        elif order_id is None or order_id == '':
            raise ValidationError('order does not have a detail')

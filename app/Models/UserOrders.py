from .. import db
from ..exceptions import ValidationError


class UserOrders(db.Model):
    __tablename__ = 'userOrders'
    user_id = db.Column('user_id', db.Integer, db.ForeignKey('users.id'),
                        primary_key=True)
    order_id = db.Column('order_id', db.Integer, db.ForeignKey('orders.id'),
                         primary_key=True)

    def to_json(self):
        user_orders_json = {
            'order_id': self.order_id,
            'user_id': self.user_id
        }
        return user_orders_json

    @staticmethod
    def from_json(json_user_orders):
        order_id = json_user_orders.get('order_id')
        user_id = json_user_orders.get('user_id')

        ProductsOrders.check_details(order_id, user_id)
        return ProductsOrders(user_id=user_id,
                              order_id=order_id)

    @staticmethod
    def check_details(order_id, user_id):
        if user_id is None or user_id == '':
            raise ValidationError('user does not have a detail')
        elif order_id is None or order_id == '':
            raise ValidationError('order does not have a detail')

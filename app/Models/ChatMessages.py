from .. import db
from ..exceptions import ValidationError
from datetime import datetime
from .Message import Message
class ChatMessages(db.Model):
    __tablename__ = 'chatMessages'
    message_id = db.Column('message_id', db.Integer, db.ForeignKey('messages.id'),
                         primary_key=True)
    chat_id = db.Column('chat_id', db.Integer, db.ForeignKey('chats.id'),
                           primary_key=True)
    def to_json(self):
        products_order_json = {
            'message_id': self.message_id,
            'chat_id': self.chat_id
        }
        return products_order_json

    @staticmethod
    def from_json(json_products_order):
        message_id = json_products_order.get('message_id')
        chat_id = json_products_order.get('chat_id')

        ProductsOrders.check_details(order_id, product_id)
        return ProductsOrders(message_id=message_id,
                              chat_id=chat_id)

    @staticmethod
    def check_details(chat_id, message_id):
        if message_id is None or message_id == '':
            raise ValidationError('message does not have a detail')
        elif chat_id is None or chat_id == '':
            raise ValidationError('chat does not have a detail')

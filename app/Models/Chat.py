from .. import db
from .ChatMessages import ChatMessages


class Chat(db.Model):
    __tablename__ = 'chats'
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                        unique=False)
    messages = db.relationship('Message',
                               secondary=ChatMessages.__tablename__,
                               backref=db.backref('users', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan',
                               single_parent=True)

    @staticmethod
    def from_json(json_chat):
        user_id = json_chat.get('user_id')
        messages = json_chat.get('messages')
        return Chat(user_id=user_id,
                    messages=messages)

    def to_json(self):
        json_chat = {
            'user_id': self.user_id,
            'messages': [message.to_jason() for message in self.messages]
        }
        return json_chat

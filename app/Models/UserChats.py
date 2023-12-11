from .. import db


class UserChats(db.Model):
    __tablename__ = 'userChats'
    user_id = db.Column('user_id', db.Integer, db.ForeignKey('users.id'),
                        primary_key=True)
    chat_id = db.Column('chat_id', db.Integer, db.ForeignKey('chats.id'),
                        primary_key=True)

    def to_json(self):
        userchat_json = {
            'user_id': self.user_id,
            'chat_id': self.chat_id
        }
        return userchat_json

    @staticmethod
    def from_json(userchat_json):
        user_id = userchat_json.get('user_id')
        chat_id = userchat_json.get('chat_id')
        return UserChats(user_id=user_id, chat_id=chat_id)

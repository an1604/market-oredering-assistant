from ..exceptions import ValidationError
from .. import db
from werkzeug.security import generate_password_hash, check_password_hash


class UserMarkets(db.Model):
    __tablename__ = 'userMarkets'
    user_id = db.Column('user_id', db.Integer, db.ForeignKey('users.id'),
                        primary_key=True)
    market_id = db.Column('market_id', db.Integer, db.ForeignKey('markets.id'),
                          primary_key=True)
    market_login_username = db.Column('username', db.String(64))
    market_login_password_hash = db.Column('password', db.String(255))

    @property
    def market_login_password(self):
        raise AttributeError('password is not a readable attribute')

    @market_login_password.setter
    def market_login_password(self, password):
        self.market_login_password_hash = generate_password_hash(password)

    def to_json(self):
        user_markets_json = {
            'user_id': self.user_id,
            'market_id': self.market_id,
            'market_login_password_hash': self.market_login_password_hash,
            'market_login_username': self.market_login_username
        }
        return user_markets_json

    @staticmethod
    def from_json(user_markets_json):
        user_id = user_markets_json.get('user_id')
        market_id = user_markets_json.get('market_id'),
        market_login_password_hash = user_markets_json.get('market_login_password_hash')
        market_login_username = user_markets_json.get('market_login_username')
        UserMarkets.check_details(user_id, market_id, market_login_password_hash, market_login_username)
        return UserMarkets(user_id=user_id, market_id=market_id,
                           market_login_password_hash=market_login_password_hash,
                           market_login_username=market_login_username)

    @staticmethod
    def check_details(user_id, market_id, market_login_password_hash
                      , market_login_username):
        if user_id is None or user_id == '':
            raise ValidationError('user does not have a detail')
        elif market_id is None or market_id == '':
            raise ValidationError('market does not have a detail')
        elif market_login_password_hash is None or market_login_password_hash == '':
            raise ValidationError('market login password does not have a detail')
        elif market_login_username is None or market_login_username == '':
            raise ValidationError('market login username  does not have a detail')

from .. import db
from app.exceptions import ValidationError

class Market(db.Model):
    __tablename__ = 'markets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    home_page = db.Column(db.String(128), unique=True)
    login_page = db.Column(db.String(128), unique=True)
    thumbnail = db.Column(db.String(128), unique=True)

    def __init__(self, **kwargs):
        super(Market, self).__init__(**kwargs)
        if self.name is None:
            self.name = 'Shufersal'

    @staticmethod
    def add_new_market(market_name, login_page, home_page, thumbnail):
        market = Market(name=market_name, home_page=home_page, login_page=login_page, thumbnail=thumbnail)
        db.session.add(market)
        db.session.commit()
        return market

    def to_json(self):
        json_market = {
            'name': self.name,
            'home_page': self.home_page,
            'login_page': self.login_page,
            'thumbnail': self.thumbnail
        }
        return json_market

    @staticmethod
    def from_json(json_market):
        name = json_market.get('name')
        home_page = json_market.get('json_product')
        login_page = json_market.get('login_page')
        thumbnail = json_market.get('thumbnail')
        Market.check_market_details(name, home_page, login_page, thumbnail)
        return Market(name=name, login_page=login_page,
                      home_page=home_page, thumbnail=thumbnail)

    @staticmethod
    def check_market_details(name, home_page, login_page, thumbnail):
        if name is None or name == '':
            raise ValidationError('name does not have a detail')
        elif home_page is None or home_page == '':
            raise ValidationError('home_page does not have a  detail')
        elif thumbnail is None or thumbnail == '':
            raise ValidationError('thumbnail does not have a  detail')
        elif login_page is None or login_page == '':
            raise ValidationError('login_page does not have a  detail')

    def __repr__(self):
        return '<Market %r>' % self.name

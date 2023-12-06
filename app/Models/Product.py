from .. import db
from app.exceptions import ValidationError

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    category = db.Column(db.String(64), unique=True)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(256), unique=True)
    buy_button = db.Column(db.String(64))
    description = db.Column(db.String(256), unique=True)

    def __init__(self, **kwargs):
        super(Product, self).__init__(**kwargs)

    def to_json(self):
        json_product = {
            'url': url_for('api.get_product', id=self.id),
            'price': self.price,
            'image': self.image,
            'category': self.category,
            'description': self.description
        }
        return json_product

    @staticmethod
    def from_json(json_product):
        price = json_product.get('price')
        image = json_product.get('image')
        category = json_product.get('category')
        description = json_product.get('description')
        Product.check_product_details(price, category, image, description)  # raise ValidationError
        return Product(price=price,
                       image=image,
                       description=description,
                       category=category)

    @staticmethod
    def check_product_details(price, category, image, description):
        if price is None or price == '':
            raise ValidationError('Price does not have a detail')
        elif category is None or category == '':
            raise ValidationError('category does not have a  detail')
        elif image is None or image == '':
            raise ValidationError('image does not have a  detail')
        elif description is None or description == '':
            raise ValidationError('description does not have a  detail')

    def __repr__(self):
        return '<Product %r>' % self.name

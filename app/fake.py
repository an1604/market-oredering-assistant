from random import randint, uniform
from sqlalchemy.exc import IntegrityError
from faker import Faker
from . import db
from .Models.models import User, Order, Product, Post


def generate_products_for_orders_by_user(user_id, count=1):
    product_count = Product.query.count()
    product_in_order = set()
    order = []
    while count > 0:
        product = Product.query.filter_by(id=randint(1, product_count)).first()
        if product.id not in product_in_order:
            product_in_order.add(product.id)
            order.append(product)
            count -= 1
    return order


def users(count=100):
    fake = Faker()
    i = 0
    while i < count:
        u = User(email=fake.email(),
                 username=fake.user_name(),
                 password='password',
                 city=fake.city(),
                 member_since=fake.past_date(),
                 address=fake.address(),
                 confirmed=True,
                 location=fake.country())
        db.session.add(u)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()


def orders(count=100):
    print('inside orders...')
    fake = Faker()
    user_count = User.query.count()
    for i in range(user_count):
        u = User.query.offset(i).first()
        for j in range(count):
            products_list = generate_products_for_orders_by_user(u.id)
            order = Order(price=0.0,
                          manufacturing_date=fake.date(),
                          manufacturing_time=fake.time(),
                          products=products_list)

            u.orders.append(order)
            print('Order number {},for user id {}, wass successfully added!'.format(j,u.id))
        db.session.commit()


def products(cont=200):
    fake = Faker()
    for i in range(cont):
        p = Product(name=fake.name(),
                    category='food',
                    price=uniform(0.99, 99.99),
                    description=fake.text())
        db.session.add(p)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def posts(count=100):
    fake = Faker()
    user_count = User.query.count()
    for i in range(count):
        u = User.query.offset(randint(0, user_count - 1)).first()
        p = Post(body=fake.text(),
                 timestamp=fake.past_date(),
                 author=u)
        db.session.add(p)
    db.session.commit()
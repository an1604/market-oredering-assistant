import pdb

from .. import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, BadData
from flask import current_app
from datetime import datetime
import hashlib
from flask import request, url_for
import bleach
from markdown import markdown
from .UserOrders import UserOrders
from .UserMarkets import UserMarkets
from .Post import Post
from .Role import Role
from .Follow import Follow
from .Permission import Permission
from flask_login import UserMixin, AnonymousUserMixin


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(256))
    confirmed = db.Column(db.Boolean, default=False)
    avatar_hash = db.Column(db.String(32))
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    # Address for the shipping
    city = db.Column(db.String(50))
    address = db.Column(db.String(255))
    location = db.Column(db.String(64))

    # Relationships
    # user orders
    orders = db.relationship('Order',
                             secondary=UserOrders.__tablename__,
                             backref=db.backref('users', lazy='joined'),
                             lazy='dynamic',
                             cascade='all, delete-orphan',
                             single_parent=True)

    # user markets
    markets = db.relationship('Market',
                              secondary=UserMarkets.__tablename__,
                              backref=db.backref('users', lazy='joined'),
                              lazy='dynamic',
                              cascade='all, delete-orphan',
                              single_parent=True)

    posts = db.relationship('Post', backref='author', lazy='dynamic')

    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')

    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')

    comments = db.relationship('Comment',
                               backref='author',
                               lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.follow(self)
        if self.role is None:
            self.get_my_role()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = self.gravatar_hash()

    def __repr__(self):
        return '<User %r>' % self.username

    """Follow part----------------------------------------------------------"""

    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()

    def is_following(self, user):
        if user.id is None:
            return False
        return self.followed.filter_by(
            followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        if user.id is None:
            return False
        return self.followers.filter_by(
            follower_id=user.id).first() is not None

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    """End Follow part--------------------------------------------------------"""
    """Password Handler-----------------------------------------------"""

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def reset_password(token, password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        user.password = password
        db.session.add(user)
        return True

    """End Password Handler-----------------------------------------------"""

    """Roles-------------------------------------"""

    def get_my_role(self):
        if self.email == current_app.config['FLASKY_ADMIN']:
            self.role = Role.query.filter_by(name='Administrator').first()
        if self.role is None:
            self.role = Role.query.filter_by(default=True).first()

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    """End Roles---------------------------------------------------"""

    """RESTfull api-------------------------------------------"""

    def to_json(self):
        json_user = {
            'url': url_for('api.get_user', id=self.id),
            'username': self.username,
            'member_since': self.member_since,
            'last_seen': self.last_seen,
            'posts_url': url_for('api.get_user_posts', id=self.id),
            'followed_posts_url': url_for('api.get_user_posts', id=self.id),
            'post_count': self.posts.count(),
            'order_count': self.orders.count(),
            'market_count': self.markets.count()
        }
        return json_user

    """End RESTfull api---------------------------------------------------"""

    """posts-------------------------------------------------"""

    @property
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id == Post.author_id) \
            .filter(Follow.follower_id == self.id)

    """End posts---------------------------------------------------"""

    """Gravatar ----------------------------------------------------"""

    def gravatar_hash(self):
        return hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()

    def gravatar(self, size=100, default='identicon', rating='g'):
        """In this method we created an avatar image for user.
        Args:
            size - The size of the avatar.
            default -The default image generator for users who have no avatars registered with the Gravatar service.
             rating -Image rating. Options are "g", "pg", "r", and "x"
        """
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'

        hash = self.avatar_hash or self.gravatar_hash()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    """End Gravatar ----------------------------------------------------"""

    """Confirmation---------------------------------"""

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({
            'confirm': self.id
        }).decode('utf-8')

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        decoded_payload = None
        try:
            decoded_payload = s.loads(token.encode('utf-8'))
        except BadSignature as e:
            if e.payload is not None:
                try:
                    decoded_payload = s.load_payload(e.payload)
                except BadData:
                    return False
        if decoded_payload.get('confirm') != self.id:
            return False
        self.confirmed = True
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({
            'reset': self.id
        }).decode('utf-8')

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({
            'change_email': self.id,
            'new_email': new_email
        }).decode('utf-8')

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')

        if self.query.filter_by(email=new_email).first() is not None:
            return False

        self.email = new_email
        self.avatar_hash = self.gravatar_hash()
        db.session.add(self)
        return True

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id}).decode('utf-8')

    @staticmethod
    def verify_auth_token(email_or_token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    """End Confirmation---------------------------------"""

    # Pinging the db when the user come back to the app
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


login_manager.anonymous_user = AnonymousUser

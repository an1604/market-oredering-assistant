from . import api
from ..Models.models import User, Post
from flask import jsonify, request, current_app, url_for


@api.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_json())


# Return all the blog posts written by a user.
@api.route('/users/<int:id>/posts/', methods=['GET'])
def get_user_posts(id):
    user = User.query.get_or_404(id)
    return jsonify({
        'user': user.id,
        'posts': [post.to_json() for post in user.posts]
    })


# Return all orders from existing user
@api.route('/users/<int:id>/orders/', methods=['GET'])
def get_user_orders(id):
    user = User.query.get_or_404(id)
    return jsonify({'user': user.id,
                    'orders': [order.to_json() for order in user.orders]
                    })


# Return all markets from existing user
@api.route('/users/<int:id>/markets/', methods=['GET'])
def get_user_markets(id):
    user = User.query.get_or_404(id)
    return jsonify({'user': user.id,
                    'markets': [market.to_json() for market in user.markets]
                    })


@api.route('/users/<int:id>/chats/', methods=['GET'])
def get_user_chats(id):
    user = User.query.get_or_404(id)
    return jsonify({
        'user': user.id,
        'chats': [chat.to_json() for chat in user.chats]
    })


# Return all the blog posts followed by a user.
@api.route('/users/<int:id>/timeline/')
def get_posts_by_followed(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = user.followed_posts.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_user_followed_posts', id=id, page=page - 1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_user_followed_posts', id=id, page=page + 1)
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })

from . import api
from ..Models.models import User
from flask import g, jsonify


@api.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = User.get_or_404(id)
    return jsonify(user.to_json())


# Return all the blog posts written by a user.
@api.route('/users/<int:id>/posts/', methods=['GET'])
def get_user_posts(id):
    user = User.get_or_404(id)
    return jsonify({
        'user': user.id,
        'posts': [post.to_json() for post in user.posts]
    })


# Return all the blog posts followed by a user.
@api.route('/users/<int:id>/timeline/', methods=['GET'])
def get_posts_by_followed(id):
    user = User.get_or_404(id)
    users_followed = user.followed
    return jsonify({
        'user': [get_user_posts(followed.id) for followed in users_followed]
    })

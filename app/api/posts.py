from . import api
from ..Models.models import Post, Permission
from flask import g, jsonify, request, current_app,url_for
from .. import db
from .decorators import permission_required, admin_required
from .comments import get_next_prev_from_pagination


# Create a new blog post.
@api.route('/posts/', methods=['POST'])
@permission_required(Permission.WRITE)
def new_post():
    post = Post.from_json(request.json)
    post.author = g.current_user
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json()), 201, \
        {'Location': url_for('api.get_post', id=post.id)}


# Return all the blog posts.
@api.route('/posts/')
def get_posts():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.paginate(
        page=page, per_page=int(current_app.config['FLASKY_POSTS_PER_PAGE']),
        error_out=False)
    posts = pagination.items
    next, prev = get_next_prev_from_pagination(pagination)
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


# Return a blog post.
@api.route('/posts/<int:id>')
def get_post(id):
    post = Post.query.get_or_404(id)
    return jsonify(post.to_json())


# Modify a blog post.
@api.route('/posts/<int:id>', methods=['PUT'])
@permission_required(Permission.WRITE)
@admin_required
def edit_post(id):
    post = Post.query.get_or_404(id)
    post.body = request.json.get('body', post.body)
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json())
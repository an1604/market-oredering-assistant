from . import api
from flask import g, request, jsonify, current_app
from ..Models.models import Post, Permission
from ..Models.models import Comment
from .decorators import permission_required, admin_required
from .. import db


# Given pagination object, return the next and prev pages URLs
def get_next_prev_from_pagination(pagination):
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_comments', page=page - 1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_comments', page=page + 1)
    return next, prev


# Return the comments on a blog post.
@api.route('/posts/<int:id>/comments/', methods=['GET'])
def get_post_comments(id):
    post = Post.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page=page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    next, prev = get_next_prev_from_pagination(pagination)
    return jsonify({
        'comment ': [comment.to_json() for comment in comments],
        'perv': prev,
        'next': next,
        'count': pagination.total
    })


# Add a comment to a blog post.
@api.route('/posts/<int:id>/comments/', methods=['POST'])
@permission_required(Permission.COMMENT)
def new_comment(id):
    post = Post.query.get_or_404(id)
    comment = Comment.from_jason(request.json)
    comment.author = g.current_user
    comment.post = post
    db.session.add(comment)
    db.session.commit()
    return jsonify(comment.to_json()), 201, \
        {'Location': url_for('api.get_comment', id=comment.id)}


# Return all the comments.
@api.route('/comments/', methods=['GET'])
def get_comments():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    next, prev = get_next_prev_from_pagination(pagination)
    return jsonify({
        'comments': [comment.to_json() for comment in comments],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


# Return a comment.
@api.route('/comments/<int:id>')
def get_comment(id):
    comment = Comment.query.get_or_404(id)
    return jsonify(comment.to_json())
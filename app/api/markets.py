import flask

from . import api
from flask import g, jsonify, request
from .. import db
from ..Models.models import Market, Permission
from .decorators import permission_required, admin_required


# Create a new market
@api.route('/markets/', methods=['POST'])
@permission_required(Permission.ADMIN)
def new_market():
    market = Market.from_json(request.json)
    db.session.add(market)
    db.session.commit()
    return jsonify(market.to_json()), 201, \
        {'Location': url_for('api.get_market', id=post.id)}


# Return all the markets
@api.route('/markets/')
def get_markets():
    markets = Market.query.all()
    return jsonify({
        'markets': [market.to_json() for market in markets]
    })


# Return a market
@api.route('/markets/<int:id>')
def get_market(id):
    market = Market.query.get_or_404(id)
    return jsonify(market.to_json())


# Modify a market
@api.route('/markets/<int:id>', methods=['PUT'])
@permission_required(Permission.ADMIN)
@admin_required
def edit_market(id):
    market = Market.query.get_or_404(id)
    market = request.json.get('name', market.name)
    market = request.json.get('thumbnail', market.thumbnail)
    market = request.json.get('login_page', market.login_page)
    market = request.json.get('home_page', market.home_page)
    db.session.add(market)
    db.session.commit()
    return jsonify(market.to_json())


# DELETE a market
@api.route('/markets/<int:id>', methods=['DELETE'])
@permission_required(Permission.ADMIN)
@admin_required
def delete_market(id):
    market = Market.query.get_or_404(id)
    db.session.delete(market)
    db.session.commit()
    flask.flash('Market successfully deleted.')
    return flask.url_for('main.user',
                         username=g.current_user.username)
import flask

from ..Models.models import Order, User
from . import api
from .. import db
from flask import request, jsonify, g, url_for
from flask_login import login_required


# Create a new order
@api.route('/orders/', methods=['POST'])
def new_order():
    order = Order.from_json(request.json)
    user = g.current_user
    user.orders.append(order)
    db.session.add(order, user)
    db.session.commit()
    return jsonify(order.to_json()), 201, \
        {'Location': url_for('api.get_order',
                             id=order.id)}


# Return all the orders
@api.route('/orders')
def get_orders():
    orders = Order.query.all()
    return jsonify({
        'order': [order.to_json() for order in orders]
    })


# Return an order
@api.route('/orders/<int:id>')
def get_order(id):
    order = Order.get_or_404(id)
    return jsonify(order.to_json())


# Modify an order
@api.route('/orders/<int:id>', methods=['PUT'])
def edit_order(id):
    order = Order.get_or_404(id)
    order = request.json.get('manufacturing_time', order.manufacturing_time)
    order = request.json.get('manufacturing_time', order.manufacturing_date)
    order = request.json.get('products', order.products)
    db.session.add(order)
    db.session.commit()
    return jsonify(order.to_json())


# Delete an order
@api.route('/orders/<int:id>', methods=['DELETE'])
@login_required
def delete_order(id):
    order = Order.get_or_404(id)
    db.session.delete(order)
    db.session.commit()
    flask.flash('Order deleted!')
    return url_for('main.user',
                   username=g.current_user.username)
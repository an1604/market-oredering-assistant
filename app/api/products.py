from . import api
from ..Models.models import Product, Permission
from flask import g, jsonify, request, url_for
from .. import db
from .decorators import permission_required


# Create a new product
@api.route('/products/', methods=['POST'])
@permission_required(Permission.ADMIN)
def new_product():
    product = Product.from_json(request.json)
    db.session.add(product)
    db.session.commit()
    return jsonify(post.to_json()), 201, \
        {'Location': url_for('api.get_product', id=post.id)}


# Return all the products
@api.route('/products/')
def get_products():
    products = Product.query.all()
    return jsonify({
        'products': [product.to_json() for product in products]
    })


# Return a product
@api.route('/products/<int:id>')
def get_product(id):
    product = Product.get_or_404(id)
    return jsonify({'product': product.to_json()})


# Edit a product
@api.route('/products/<int:id>', methods=['PUT'])
def edit_product(id):
    product = Product.get_or_404(id)
    product = request.json.get('name', product.name)
    product = request.json.get('image', product.image)
    product = request.json.get('price', product.price)
    product = request.json.get('description', product.description)
    db.session.add(product)
    db.session.commit()
    return jsonify(product.to_json())


# Delete a product
@api.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return url_for('main.user',
                   username=g.current_user.username)
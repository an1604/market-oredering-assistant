from . import api
from flask import g, request, jsonify
from ..Models.models import Chat, User


@api.route('/chats', methods=['GET'])
def get_chats():
    chats = Chat.query.all()
    return jsonify({
        'chats': [chat.to_json() for chat in chats]
    })


@api.route('/chats', methods=['POST'])
def create_chat():
    chat = Chat.from_json(request.json)
    db.session.add(chat)
    db.session.commit()
    return jsonify({
        'chat': chat.to_json()
    })


@api.route('/chats/<int:id>', methods=['GET'])
def get_chat(id):
    chat = Chat.query.get_or_404(id)
    return jsonify({
        'chat': chat.to_json()
    })


@api.route('/chats/<int:id>', methods=['PUT'])
def update_chat(id):
    chat = Chat.query.get_or_404(id)
    if request.json is not None:
        chat.from_json(request.json)
        db.session.commit()
        return jsonify({
            'chat': chat.to_json()
        })


@api.route('/chats/<int:id>', methods=['DELETE'])
def delete_chat(id):
    chat = Chat.query.get_or_404(id)
    db.session.delete(chat)
    db.session.commit()
    return jsonify({
        'chat': chat.to_json()
    })


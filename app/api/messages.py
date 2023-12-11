from . import api
from flask import jsonify
from ..Models.models import Message, Chat


@api.route('/messages/<int:id>', methods=['GET'])
def get_message(id):
    message = Message.query.get_or_404(id)
    return jsonify(message.to_jason())


@api.route('/chats/<int:chat_id>/messages', methods=['GET'])
def get_all_messages_from_chat(chat_id):
    chat = Chat.query.get_or_404(chat_id)
    return jsonify({
        'messages': [message.to_jason() for message in chat.messages]
    })


@api.route('/chats/<int:chat_id>/message', methods=['POST'])
def create_message(chat_id):
    chat = Chat.query.get_or_404(chat_id)
    message = Message.from_jason(request.json)
    chat.messages.append(message)
    db.session.add(message)
    db.session.commit()
    return jsonify(message.to_jason(), 201,
                   {'Location': url_for('api.get_message', id=message.id)})


@api.route('/messages', methods=['GET'])
def get_all_messages():
    messages = Message.query.all()
    return jsonify({
        'messages': [message.to_jason() for message in messages]
    })



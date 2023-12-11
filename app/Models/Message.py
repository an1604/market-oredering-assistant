from .. import db
from ..exceptions import ValidationError
import bleach
from markdown import markdown
from flask import url_for


class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)

    @staticmethod
    def from_jason(json_comment):
        body = json_comment.get('body')
        if body is None or body == '':
            raise ValidationError('comment does not have a body')
        return Comment(body=body)

    def to_jason(self):
        json_comment = {
            'url': url_for('api.get_message', id=self.id),
            'body': self.body,
            'body_html': self.body_html,
        }
        return json_comment

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i',
                        'strong']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))


db.event.listen(Message.body, 'set', Message.on_changed_body)

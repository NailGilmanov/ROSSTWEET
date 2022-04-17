from flask import jsonify, abort
from flask_restful import Resource
from . import db_session
from .twits import Twits
from .reqparse import twits_parser


def abort_if_twit_not_found(twit_id):
    session = db_session.create_session()
    news = session.query(Twits).get(twit_id)
    if not news:
        abort(404, message=f"Twit {twit_id} not found")


class TwitResource(Resource):
    def get(self, twit_id):
        abort_if_twit_not_found(twit_id)
        session = db_session.create_session()
        twit = session.query(Twits).get(twit_id)
        return jsonify({'twit': twit.to_dict(
            only=('title', 'content', 'user_id', 'created_date', 'is_private'))})

    def delete(self, twit_id):
        abort_if_twit_not_found(twit_id)
        session = db_session.create_session()
        twit = session.query(Twits).get(twit_id)
        session.delete(twit)
        session.commit()
        return jsonify({'success': 'OK'})


class TwitsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        twit = session.query(Twits).all()
        return jsonify({'twits': [item.to_dict(
            only=('title', 'content', 'created_date', 'user.name')) for item in twit]})

    def post(self):
        args = twits_parser.parse_args()
        session = db_session.create_session()
        twit = Twits(
            title=args['title'],
            content=args['content'],
            user_id=args['user_id'],
            is_private=args['is_private']
        )
        session.add(twit)
        session.commit()
        return jsonify({'success': 'OK'})
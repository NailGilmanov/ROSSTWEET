from flask import jsonify, abort
from flask_restful import Resource
from . import db_session
from .comments import Comment
from .reqparse import comments_parser


def abort_if_comment_not_found(twit_id, comment_id):
    session = db_session.create_session()
    news = session.query(Comment).filter(Comment.twit_id == twit_id,
                                          Comment.id == comment_id).first()
    if not news:
        abort(404, message=f"Comment {comment_id} not found")


class CommentResource(Resource):
    def get(self, twit_id, comment_id):
        abort_if_comment_not_found(twit_id, comment_id)
        session = db_session.create_session()
        twit = session.query(Comment).get(twit_id)
        return jsonify({'twit': twit.to_dict(
            only=('title', 'content', 'user_id', 'created_date', 'is_private'))})

    def delete(self, twit_id, comment_id):
        abort_if_comment_not_found(twit_id, comment_id)
        session = db_session.create_session()
        twit = session.query(Comment).filter(Comment.twit_id == twit_id,
                                          Comment.id == comment_id).first()
        session.delete(twit)
        session.commit()
        return jsonify({'success': 'OK'})


class CommentsListResource(Resource):
    def get(self, twit_id):
        session = db_session.create_session()
        comments = session.query(Comment).filter(Comment.twit_id == twit_id).all()
        return jsonify({'comments': [item.to_dict(
            only=('content', 'created_date', 'user.name')) for item in comments]})

    def post(self, twit_id):
        args = comments_parser.parse_args()
        session = db_session.create_session()
        comment = Comment(
            content=args['content'],
            user_id=args['user_id'],
            twit_id=twit_id
        )
        session.add(comment)
        session.commit()
        return jsonify({'success': 'OK'})
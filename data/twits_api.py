import flask

from . import db_session
from .twits import Twits
from .comments import Comment
from flask import jsonify, request

blueprint = flask.Blueprint(
    'twits_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/twits')
def get_twits():
    db_sess = db_session.create_session()
    twits = db_sess.query(Twits).all()
    return jsonify(
        {
            'twit':
                [item.to_dict(only=('title', 'content', 'created_date', 'is_private', 'user.name'))
                 for item in twits]
        }
    )


@blueprint.route('/api/twits/<int:twit_id>', methods=['GET'])
def get_one_twit(twit_id):
    db_sess = db_session.create_session()
    twit = db_sess.query(Twits).get(twit_id)
    if not twit:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'twit': twit.to_dict(only=('title', 'content',
                                       'created_date', 'is_private', 'user.name'))
        }
    )


@blueprint.route('/api/twits', methods=['POST'])
def create_twit():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['title', 'content', 'user_id', 'is_private']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    twit = Twits(
        title=request.json['title'],
        content=request.json['content'],
        user_id=request.json['user_id'],
        is_private=request.json['is_private']
    )
    db_sess.add(twit)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/twits/<int:twit_id>', methods=['DELETE'])
def delete_twit(twit_id):
    db_sess = db_session.create_session()
    twit = db_sess.query(Twits).get(twit_id)
    if not twit:
        return jsonify({'error': 'Not found'})
    db_sess.delete(twit)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/comments/<int:twit_id>')
def get_comments(twit_id):
    db_sess = db_session.create_session()
    comments = db_sess.query(Comment).filter(Comment.twit_id == twit_id).all()
    if comments:
        return jsonify(
            {
                'comments':
                    [item.to_dict(only=('content', 'created_date', 'user.name'))
                     for item in comments]
            }
        )
    else:
        return jsonify({'error': 'Not found'})


@blueprint.route('/api/comments/<int:twitt_id>/<int:comment_id>', methods=['GET'])
def get_one_comment(twitt_id, comment_id):
    db_sess = db_session.create_session()
    comment = db_sess.query(Comment).filter(Comment.twit_id == twitt_id,
                                            Comment.id == comment_id).first()
    if comment:
        return jsonify(
            {
                'comment': comment.to_dict(only=('content', 'created_date', 'user.name'))
            }
        )
    else:
        return jsonify({'error': 'Not found'})


@blueprint.route('/api/comments/<int:twit_id>', methods=['POST'])
def create_comment(twit_id):
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['content', 'user_id']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    comment = Comment(
        content=request.json['content'],
        user_id=request.json['user_id'],
        twit_id=twit_id,
    )
    db_sess.add(comment)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/comments/<int:twit_id>/<int:comment_id>', methods=['DELETE'])
def delete_comment(twit_id, comment_id):
    db_sess = db_session.create_session()
    comment = db_sess.query(Comment).filter(Comment.twit_id == twit_id,
                                          Comment.id == comment_id).first()
    if not comment:
        return jsonify({'error': 'Not found'})
    db_sess.delete(comment)
    db_sess.commit()
    return jsonify({'success': 'OK'})

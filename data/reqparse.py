from flask_restful import reqparse

twits_parser = reqparse.RequestParser()
twits_parser.add_argument('title', required=True)
twits_parser.add_argument('content', required=True)
twits_parser.add_argument('is_private', required=True, type=bool)
twits_parser.add_argument('user_id', required=True, type=int)

comments_parser = reqparse.RequestParser()
comments_parser.add_argument('content', required=True)
comments_parser.add_argument('user_id', required=True, type=int)
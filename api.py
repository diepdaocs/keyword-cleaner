from flask import request
from flask_restplus import Api, Resource

from app import app
from keyword_cleaner import KeywordCleaner

api = Api(app, doc='/doc/', version='1.0', title='Keyword Cleaning')

kw_cleaner = KeywordCleaner()
ns = api.namespace('keyword', 'Keyword Cleaning')


@ns.route('/clean')
class KeywordCleaner(Resource):
    """
    Keyword Cleaner
    """

    @api.doc(params={'keyword': 'Keyword'})
    def post(self):
        """
        Post keyword to clean
        """
        result = {
            'ok': True,
            'keyword': {}
        }
        try:
            result['keyword'] = kw_cleaner.process(request.values.get('keyword'))
        except Exception as e:
            result['ok'] = False
            result['message'] = e
            return result, 500

        return result, 200

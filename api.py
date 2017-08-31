import re
from flask import request
from flask_restplus import Api, Resource

from app import app
from keyword_cleaner import KeywordCleaner
from util.log import get_logger

logger = get_logger('KeywordCleaningAPI')

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
            logger.exception(e)
            result['ok'] = False
            result['message'] = e.message
            return result, 500

        return result, 200

ns_char = api.namespace('replace', 'Replace Characters')


@ns_char.route('/character')
class ReplaceCharacters(Resource):
    """
    Replace Characters
    """
    @api.doc(params={'chars': 'Characters (multiple)'})
    @api.doc(params={'replace_char': 'Replace character (single), use `\s` for space when call from this UI'})
    def post(self):
        """
        Add replace characters
        """
        result = {
            'ok': True
        }
        try:
            chars = request.values.get('chars')
            if not chars:
                raise ValueError('Parameter `chars` is empty')

            replace_char = request.values.get('replace_char', '')
            if '\s' in replace_char:
                replace_char = replace_char.replace('\s', ' ')

            kw_cleaner.add_replace_chars(chars, replace_char)
        except Exception as e:
            logger.exception(e)
            result['ok'] = False
            result['message'] = e.message
            return result, 500

        return result, 200

    def get(self):
        """
        Get replace characters
        """
        result = {
            'ok': True,
            'replace_chars': {}
        }
        try:
            result['replace_chars'] = kw_cleaner.get_replace_chars()
        except Exception as e:
            logger.exception(e)
            result['ok'] = False
            result['message'] = e.message
            return result, 500

        return result, 200

    @api.doc(params={'chars': 'Characters to be removed, use `\s` for space when call from this UI'})
    def delete(self):
        """
        Delete replace characters
        """
        result = {
            'ok': True
        }
        try:
            chars = request.values.get('chars')
            if not chars:
                raise ValueError('Parameter `chars` is empty')
            if '\s' in chars:
                chars = chars.replace('\s', ' ')

            kw_cleaner.remove_replace_chars(chars)
        except Exception as e:
            logger.exception(e)
            result['ok'] = False
            result['message'] = e.message
            return result, 500

        return result, 200

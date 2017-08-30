# coding=utf-8
import re
from multiprocessing import Pool, cpu_count

from util.io import RedisClient


def _clean(keyword, replace_chars):
    """
    Clean up keywords
    :param keyword: keyword
    :return: clean keyword with statistics info
    """
    '''
    1) Remove any of the following characters.. Replace with a space
    ! = ? @ % ^ *; ~ `, (){} <> | [] " - .
    '''
    for char, replace in replace_chars.items():
        keyword = keyword.replace(char, replace)

    '''
    # 2) Remove all non-ascii characters. replace with space
    # ©2012
    # • silver
    '''
    keyword = re.sub(r'[^\x00-\x7F]+', ' ', keyword)
    '''
    # 3) Remove Tab found within the keyword strings. replace with space
    '''
    keyword = re.sub(r'\t+', ' ', keyword)
    '''
    4) Remove any string that matches the following.. replace with nothing
    site:
    url:
    allinurl:
    allintitle:
    '''
    keyword = re.sub(r'(site:|url:|allinurl:|allintitle:)', '', keyword)
    '''
    5) Remove EXCESSIVE spaces .. meaning if more than 2 spaces found
    '''
    keyword = re.sub(r'\s+', ' ', keyword)
    '''
    6) Remove leading and trailing spaces (Trim)
    '''
    keyword = keyword.strip()

    return keyword


def _process(keyword, replace_chars):
    original = keyword
    cleaned = _clean(keyword, replace_chars)
    return {
        'original': original,
        'cleaned': cleaned,
        'char_count': len(cleaned),
        'word_count': len(cleaned.split())
    }


def _process_with_tracking((keyword, replace_chars, job_id)):
    redis = RedisClient().get_instance()
    result = _process(keyword, replace_chars)
    redis.hincrby(job_id, 'progress')
    return result


class KeywordCleaner(object):
    _REDIS_REMOVE_CHAR_KEY = 'keyword-cleaning:removed-char'

    def __init__(self, job_id=None):
        self.job_id = job_id
        self.redis = RedisClient.get_instance()
        self.add_replace_chars('!=?@%^*;~`,(){}<>|[]\'"-.', ' ')

    def process_batch(self, keywords):
        pool = Pool(cpu_count() * 2)
        replace_chars = self.get_replace_chars()
        tasks = ((k, replace_chars, self.job_id) for k in keywords)
        result = pool.map(_process_with_tracking, tasks)
        pool.close()
        pool.terminate()
        return result

    def process(self, keyword):
        return _process(keyword, self.get_replace_chars())

    def clean(self, keyword):
        return _clean(keyword, self.get_replace_chars())

    def add_replace_chars(self, remove_chars, replace_char):
        for char in remove_chars:
            self.redis.hset(self._REDIS_REMOVE_CHAR_KEY, char, replace_char)

    def get_replace_chars(self):
        return self.redis.hgetall(self._REDIS_REMOVE_CHAR_KEY)

    def remove_replace_chars(self, chars):
        self.redis.hdel(self._REDIS_REMOVE_CHAR_KEY, *chars)

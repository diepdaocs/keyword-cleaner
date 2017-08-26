# coding=utf-8
import re
from multiprocessing import Pool, cpu_count

from util.io import RedisClient


def _clean(keyword):
    """
    Clean up keywords
    :param keyword: keyword
    :return: clean keyword with statistics info
    """
    '''
    1) Remove any of the following characters.. Replace with a space
    ! = ? @ % ^ *; ~ `, (){} <> | [] " - .
    '''
    keyword = re.sub(r'[!=?@%^*;~`,(){}<>|\[\]\'"\-.]', ' ', keyword)
    '''
    # 2) Remove all non-ascii characters. replace with space
    # ©2012
    # • silver
    '''
    keyword = re.sub(r'[^\x00-\x7F]+', ' ', keyword)
    '''
    # 3) Remove Tab found within the keyword strings. replace with space
    '''
    keyword = re.sub(r'[\t]', ' ', keyword)
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


def _process(keyword):
    original = keyword
    cleaned = _clean(keyword)
    return {
        'original': original,
        'cleaned': cleaned,
        'char_count': len(cleaned),
        'word_count': len(cleaned.split())
    }


def _process_with_tracking((keyword, job_id)):
    redis = RedisClient().get_instance()
    result = _process(keyword)
    redis.hincrby(job_id, 'progress')
    return result


class KeywordCleaner(object):
    def __init__(self, job_id=None):
        self.job_id = job_id

    def process_batch(self, keywords):
        pool = Pool(cpu_count() * 2)
        tasks = ((k, self.job_id) for k in keywords)
        result = pool.map(_process_with_tracking, tasks)
        pool.close()
        pool.terminate()
        return result

    @staticmethod
    def process(keyword):
        return _process(keyword)

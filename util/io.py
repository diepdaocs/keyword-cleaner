from redis import StrictRedis


class RedisClient(object):
    __instance = None

    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            return StrictRedis(db=8)
        return cls.__instance

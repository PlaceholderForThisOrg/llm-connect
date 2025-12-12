import redis

from llm_connect.configs.redis import HOST, PORT

Redis = redis.asyncio.Redis(host=HOST, port=PORT)

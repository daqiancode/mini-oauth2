import redis.asyncio as aredis
from app.config import settings

redis_client = aredis.from_url(settings.REDIS_URL) if not settings.IS_REDIS_CLUSTER else aredis.RedisCluster.from_url(settings.REDIS_URL)
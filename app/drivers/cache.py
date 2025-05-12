import redis
from app.config import settings
from urllib.parse import urlparse
redis_url = urlparse(settings.REDIS_URL)
redis_client = redis.Redis(host=redis_url.hostname, password=redis_url.password, port=redis_url.port, db=redis_url.path.strip('/'), decode_responses=True)




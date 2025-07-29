from redis.asyncio import Redis

# Для LIFO (первым пришел, последним ушел) можно оставаться с LPUSH + BRPOP.
# Для FIFO (первым пришел, первым ушел) предпочтительнее использовать RPUSH + BLPOP,


class BaseQueueRepo:
    def __init__(self, queue_name: str, redis_client: Redis):
        self.redis_client = redis_client
        self.queue_name = queue_name

    async def count(self) -> int:
        return await self.redis_client.llen(self.queue_name)

    async def delete(self) -> int:
        return await self.redis_client.delete(self.queue_name)

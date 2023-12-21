import aiohttp
import aioredis

from app.settings import settings


class CurrencyService:
    def __init__(self, redis: aioredis.Redis):
        self.redis = redis

    async def get_exchange_rate(self):
        # try to get cached rate
        rate = await self.redis.get('exchange_rate')
        if rate:
            return float(rate)

        # get dollar rate from url
        async with aiohttp.ClientSession() as session:
            async with session.get(settings.CBR_API_URL) as response:
                data = await response.json()
                rate = data['Valute']['USD']['Value']

                # store to cache for 5 minutes
                await self.redis.set('exchange_rate', rate, ex=300)

        return rate

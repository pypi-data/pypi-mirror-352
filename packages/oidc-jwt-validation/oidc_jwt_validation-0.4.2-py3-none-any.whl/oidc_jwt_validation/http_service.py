from logging import Logger
from .http_singleton import SingletonAiohttp
import os


APPLICATION_JSON = 'application/json'
HEADERS = {'Content-type': APPLICATION_JSON, 'Accept': APPLICATION_JSON}


class ServiceGet:
    def __init__(self, logger: Logger):
        self.logger = logger
        self.proxy = os.getenv("https_proxy", None)
        self.http_timeout = int(os.getenv("http_timeout", "30"))

    async def get_async(self, url):
        logger = self.logger
        session = SingletonAiohttp.get_aiohttp_client(self.http_timeout)
        logger.debug(f"begin request: {url}")
        async with session.get(url, allow_redirects=True, proxy=self.proxy) as response:
            logger.debug(f"end request: {url}")
            status = str(response.status)
            logger.debug(f"status: {status}")
            if status == "200":
                result = await response.json()
                logger.debug(result)
                return result
            else:
                body = await response.text()
                logger.debug(body)
                raise Exception("OIDC info not found")
        return response

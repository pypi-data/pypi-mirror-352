from http import HTTPStatus
from urllib.parse import urlencode
import aiohttp


HTTP_STATUS_SUCCESS = 200


class HttpAgent:
    def __init__(self, logger, default_timeout):
        self.logger = logger
        self.default_timeout = default_timeout

        self.ssl_context = None

    async def request(self, url: str, method: str, headers: dict = None, params: dict = None, data: dict = None):
        if not headers:
            headers = {}

        if params:
            url += '?' + urlencode(params)

        data = urlencode(data).encode() if data else None

        self.logger.debug(
            f"[http-request] url: {url}, headers: {headers}, params: {params}, data: {data}, timeout: {self.default_timeout}")

        try:
            if not url.startswith("http"):
                url = f"http://{url}"

            connector = aiohttp.TCPConnector()
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.default_timeout),
                                             connector=connector) as session:
                async with session.request(method, url, headers=headers, data=data) as response:
                    if response.status == HTTPStatus.OK:
                        return await response.read(), None
                    else:
                        error_msg = f"HTTP error: {response.status} - {response.reason}"
                        self.logger.debug(f"[http-request] {error_msg}")
                        return None, error_msg

        except aiohttp.ClientError as e:
            self.logger.warning(f"[http-request] client error: {e}")
            return None, e
        except Exception as e:
            self.logger.warning(f"[http-request] unexpected error: {e}")
            return None, e

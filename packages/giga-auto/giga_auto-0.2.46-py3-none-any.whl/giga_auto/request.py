from typing import Union

import requests

from giga_auto.logger import log

DEFAULT_TIMEOUT = 60


class RequestBase(object):

    def __init__(self, base_url: str = '', expect_code=200):
        """
        :param base_url: The base URL of the API
        """
        self.base_url = base_url.rstrip('/')
        self._session = requests.Session()
        self._session.timeout = DEFAULT_TIMEOUT
        self.expect_code = expect_code

    @log
    def _request(self, method, url, **kwargs):
        response = None
        if not url.startswith('http'):
            url = f'{self.base_url}{url}' if 'route' in self.base_url else f'{self.base_url}/{url.lstrip("/")}'
        try:
            response = self._session.request(method.upper(), url, **kwargs)
            return response
        except requests.RequestException as e:
            if response:
                raise Exception(f"HTTP request failed with error: {e}\n response: {response.text}")
            raise e

    def request(self, method, url, **kwargs) -> Union[dict, list, str]:
        response = self._request(method, url, **kwargs)
        try:
            response = response.json()
        except ValueError as e:
            raise Exception(f"Response body is not a JSON: {response.text}, error: {e}")
        if 'code' in response:
            if response['code'] != self.expect_code:
                raise Exception(f"Response error: {response}")
        return response

    def get(self, url, **kwargs) -> Union[dict, list, str]:
        return self.request('GET', url, **kwargs)

    def post(self, url, **kwargs) -> Union[dict, list, str]:
        return self.request('POST', url, **kwargs)

    def put(self, url, **kwargs) -> Union[dict, list, str]:
        return self.request('PUT', url, **kwargs)

    def delete(self, url, **kwargs) -> Union[dict, list, str]:
        return self.request('DELETE', url, **kwargs)

    def patch(self, url, **kwargs) -> Union[dict, list, str]:
        return self.request('PATCH', url, **kwargs)

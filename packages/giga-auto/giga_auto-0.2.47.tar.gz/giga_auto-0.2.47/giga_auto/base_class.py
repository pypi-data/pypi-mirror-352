from giga_auto.request import RequestBase


class ApiBase(RequestBase):
    def __init__(self, **env):
        self.host = env.get('host', '')
        super().__init__(self.host, env.get('expect_code', 200))
        self.headers = env.get('headers', {})

    def set_headers(self, headers):
        self.headers = headers

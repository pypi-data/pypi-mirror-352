import requests


class ServerFetcher:

    def __init__(self, domain, token, program):
        self.domain = domain
        self.token = token
        self.program = program

        self.session = ResponseCheckingSession()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })

    def _make_request(self, method, url, **kwargs):
        if self._is_v2_endpoint(url):
            try:
                return self.session.request(method, url, **kwargs)
            except HttpError as e:
                if e.status_code in (401, 403):
                    self.post_login()
                    return self.session.request(method, url, **kwargs)
        else:
            kwargs['headers'] = {
                'Authorization': f'Token {self.token}',
                'Content-Type': 'application/json',
            }
            response = requests.request(method, url, **kwargs)
            if not 200 <= response.status_code < 300:
                raise HttpError(response)
            return response

    def _is_v2_endpoint(self, url: str) -> bool:
        return url.startswith(f'{self.domain}/v2/')

    def post_login(self) -> None:
        self.session.post(
            f'{self.domain}/v2/auth/login',
            json={'token': self.token}
        )

    def request_get(self, url, params=None):
        if params is None:
            params = {}
        return self._make_request('GET', url, params=params)

    def request_post(self, url, data):
        return self._make_request('POST', url, json=data)

    def post_log_error(self, exception, traceback):
        self.request_post(f'{self.domain}/v2/logs/errors', {
            'program': self.program,
            'exception': exception,
            'traceback': traceback,
        })
        return self.request_post(f'{self.domain}/logs/errors/', {
            'program': self.program,
            'exception': exception,
            'traceback': traceback,
        })


class ResponseCheckingSession(requests.Session):
    
    def request(self, method, url, *args, **kwargs):
        response = super().request(method, url, *args, **kwargs)
        if not 200 <= response.status_code < 300:
            raise HttpError(response)
        return response


class HttpError(requests.exceptions.RequestException):

    def __init__(self, response: requests.Response):
        self.response = response
        self.status_code = response.status_code
        self.text = response.text
        self.url = response.url
        self.method = response.request.method
        self.headers = response.headers
        super().__init__(f"HTTP {response.status_code} {response.reason}: {response.text}")
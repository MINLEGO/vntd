from curl_cffi import requests, BrowserTypeLiteral
import random

from ..model import Proxy


class SessionMixin:
    def __init__(
        self,
        base_url: str,
        proxy: Proxy | None = None,
        impersonate: BrowserTypeLiteral = None,
        request_verify: bool = True,
        **kwargs,
    ):
        self.base_url = base_url.rstrip("/")
        self.session = self._init_session(
            base_url=self.base_url,
            proxy=proxy,
            impersonate=impersonate,
            request_verify=request_verify,
        )
        self._proxy = proxy
        self._impersonate = impersonate
        super().__init__(**kwargs)

    def _generate_user_agent(self) -> str:
        return random.choice(
            [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            ]
        )

    def _init_session(
        self,
        base_url: str,
        proxy: Proxy | None = None,
        impersonate: BrowserTypeLiteral = None,
        request_verify: bool = True,
    ) -> requests.Session:
        """
        Initializes an HTTP session with optional proxy configuration and browser impersonation.
        """
        if impersonate is None:  # Pick a random browser client
            impersonate = random.choice(["safari", "chrome", "firefox"])

        session = requests.Session(impersonate=impersonate)

        session.headers.update(
            {
                "User-Agent": self._generate_user_agent(),
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
                "Origin": base_url,
                "Referer": f"{base_url}/",
            }
        )
        if proxy:
            session.proxies = {"http": proxy.url, "https": proxy.url}

        session.get(f"{base_url}/", verify=request_verify)  # Init cookies
        return session

    @property
    def proxy(self) -> Proxy:
        return self._proxy

    @proxy.setter
    def proxy(self, value: Proxy):
        if value:
            if isinstance(value, Proxy):
                self.session.proxies = {"http": value.url, "https": value.url}
            else:
                raise TypeError("Proxy must be an instance of the vntd.Proxy")
        else:
            self.session.proxies = {}
        self._proxy = value

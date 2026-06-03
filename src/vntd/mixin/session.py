from curl_cffi import requests, BrowserTypeLiteral
import random

from fake_useragent import UserAgent

from ..model import Proxy
from ..exceptions import InvalidValue


DEFAULT_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
]

_UA = UserAgent(platforms=["desktop"])

_BROWSER_MAP: dict[str | None, list[str]] = {
    "chrome": ["Chrome"],
    "firefox": ["Firefox"],
    "safari": ["Safari"],
    "edge": ["Edge"],
}


class SessionMixin:
    def __init__(
        self,
        base_url: str,
        proxy: Proxy | None = None,
        impersonate: BrowserTypeLiteral = None,
        user_agent: str | None = None,
        user_agents: list[str] | None = None,
        request_verify: bool = True,
        **kwargs,
    ):
        self.base_url = base_url.rstrip("/")
        self._user_agent = user_agent
        self._user_agents = user_agents
        self.session = self._init_session(
            base_url=self.base_url,
            proxy=proxy,
            impersonate=impersonate,
            user_agent=user_agent,
            user_agents=user_agents,
            request_verify=request_verify,
        )
        self._proxy = proxy
        self._impersonate = impersonate
        super().__init__(**kwargs)

    def _select_user_agent(
        self,
        user_agent: str | None,
        user_agents: list[str] | None,
        impersonate: BrowserTypeLiteral = None,
    ) -> str:
        if user_agent and user_agents:
            raise InvalidValue("Provide either user_agent or user_agents, not both.")
        if user_agent:
            return user_agent
        if user_agents:
            if not all(isinstance(value, str) for value in user_agents):
                raise InvalidValue("user_agents must be a list of strings.")
            return random.choice(user_agents)

        # Try fake-useragent with browser-coherent selection
        try:
            browsers = _BROWSER_MAP.get(impersonate, list(_BROWSER_MAP.values())[0])
            browser = random.choice(browsers)
            return getattr(_UA, browser.lower(), _UA.random)
        except Exception:
            pass

        return random.choice(DEFAULT_USER_AGENTS)

    def _init_session(
        self,
        base_url: str,
        proxy: Proxy | None = None,
        impersonate: BrowserTypeLiteral = None,
        user_agent: str | None = None,
        user_agents: list[str] | None = None,
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
                "User-Agent": self._select_user_agent(
                    user_agent, user_agents, impersonate
                ),
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

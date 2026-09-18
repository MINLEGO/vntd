from curl_cffi import requests, BrowserTypeLiteral
from html import unescape
from http.cookies import SimpleCookie
import random
import re

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


def _header_value(headers, name: str) -> str | None:
    """Read a response or session header without depending on its casing."""
    if headers is None:
        return None

    try:
        value = headers.get(name)
    except (AttributeError, TypeError):
        value = None
    if isinstance(value, str):
        return value

    try:
        for key, value in headers.items():
            if str(key).lower() == name.lower() and isinstance(value, str):
                return value
    except (AttributeError, TypeError):
        pass
    return None


def _cookie_value(cookies, name: str) -> str | None:
    """Read one cookie from dict-like and cookie-jar containers."""
    if cookies is None:
        return None

    try:
        value = cookies.get(name)
    except (AttributeError, KeyError, TypeError):
        value = None
    if isinstance(value, str):
        return value

    try:
        for key, value in cookies.items():
            if str(key) == name and isinstance(value, str):
                return value
    except (AttributeError, TypeError):
        pass
    return None


def _extract_cookie(response, session, name: str) -> str | None:
    """Extract a cookie from the response, session jar, or Set-Cookie header."""
    for cookies in (
        getattr(response, "cookies", None),
        getattr(session, "cookies", None),
    ):
        value = _cookie_value(cookies, name)
        if value:
            return value

    set_cookie = _header_value(getattr(response, "headers", None), "Set-Cookie")
    if set_cookie:
        parsed = SimpleCookie()
        parsed.load(set_cookie)
        morsel = parsed.get(name)
        if morsel is not None:
            return morsel.value
    return None


def _extract_csrf_token(html: str) -> str | None:
    """Extract an optional CSRF token from common Vinted bootstrap markup."""
    if not isinstance(html, str) or not html:
        return None

    patterns = (
        r'<meta[^>]+name=["\']csrf[-_]?token["\'][^>]+content=["\']([^"\']+)',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']csrf[-_]?token["\']',
        r'["\']csrf[-_]?token["\']\s*[:=]\s*["\']([^"\']+)',
        r'["\']csrfToken["\']\s*[:=]\s*["\']([^"\']+)',
        r'\bcsrf[-_]?token\b\s*[:=]\s*["\']([^"\']+)',
    )
    for pattern in patterns:
        match = re.search(pattern, html, flags=re.IGNORECASE | re.DOTALL)
        if match:
            return unescape(match.group(1))
    return None


def _capture_bootstrap_identity(session, response) -> None:
    """Attach bootstrap cookies and request tokens to the current session."""
    access_token = _extract_cookie(response, session, "access_token_web")
    anon_id = _header_value(getattr(response, "headers", None), "X-Anon-Id")
    if not anon_id:
        anon_id = _extract_cookie(response, session, "anon_id")

    csrf_token = _header_value(getattr(response, "headers", None), "X-Csrf-Token")
    if not csrf_token:
        csrf_token = _extract_csrf_token(getattr(response, "text", ""))

    headers = getattr(session, "headers", None)
    if headers is None:
        return

    if access_token:
        existing_cookie = _header_value(headers, "Cookie")
        cookie_parts = [
            part.strip()
            for part in (existing_cookie or "").split(";")
            if part.strip()
            and not part.strip().lower().startswith("access_token_web=")
        ]
        cookie_parts.append(f"access_token_web={access_token}")
        headers["Cookie"] = "; ".join(cookie_parts)
    if anon_id:
        headers["X-Anon-Id"] = anon_id
    if csrf_token:
        headers["X-Csrf-Token"] = csrf_token


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

        response = session.get(f"{base_url}/", verify=request_verify)  # Init cookies
        _capture_bootstrap_identity(session, response)
        return session

    def _request_headers(self) -> dict | None:
        """Copy session headers for requests that target another Vinted host."""
        try:
            headers = dict(self.session.headers)
        except (AttributeError, TypeError, ValueError):
            return None
        return headers or None

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

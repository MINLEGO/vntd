from curl_cffi import BrowserTypeLiteral
import curl_cffi

from .mixin import SessionMixin, SearchMixin, UserMixin, AdMixin
from .model import Proxy
from .exceptions import AccessDeniedError, RequestError, NotFoundError


class Client(SessionMixin, SearchMixin, UserMixin, AdMixin):
    def __init__(
        self,
        base_url: str = "https://www.vinted.fr",
        proxy: Proxy | None = None,
        impersonate: BrowserTypeLiteral = None,
        user_agent: str | None = None,
        user_agents: list[str] | None = None,
        request_verify: bool = True,
        timeout: float = 30.0,
        max_retries: int = 3,
    ):
        """
        Initializes a Vinted Client instance with optional proxy, browser impersonation,
        and SSL verification settings.

        Args:
            base_url (str, optional): Base Vinted domain to target (e.g., "https://www.vinted.fr"). Defaults to "https://www.vinted.fr".
            proxy (Proxy | None, optional): Proxy configuration to use for the client. If provided, it will be applied to all requests. Defaults to None.
            impersonate (BrowserTypeLiteral, optional): Browser type to impersonate for requests (e.g., "firefox", "chrome", "edge", "safari"). If None, a random browser type will be chosen.
            user_agent (str | None, optional): Explicit User-Agent string to use for requests.
            user_agents (list[str] | None, optional): List of User-Agent strings to rotate from.
            request_verify (bool, optional): Whether to verify SSL certificates when sending requests. Defaults to True.
            timeout (float, optional): Maximum time in seconds to wait for a request before timing out. Defaults to 30.
            max_retries (int, optional): Maximum number of times to retry a request in case of anti-bot failures. Defaults to 3.
        """
        self.base_url = base_url.rstrip("/")

        super().__init__(
            base_url=self.base_url,
            proxy=proxy,
            impersonate=impersonate,
            user_agent=user_agent,
            user_agents=user_agents,
            request_verify=request_verify,
        )

        self.request_verify = request_verify
        self.timeout = timeout
        self.max_retries = max_retries

    def _fetch(
        self,
        method: str,
        url: str,
        payload: dict | None = None,
        params: dict | None = None,
        max_retries: int = -1,
        expect_json: bool = True,
    ):
        """
        Internal method to send an HTTP request using the configured session.

        Args:
            method (str): HTTP method to use (e.g., "GET", "POST").
            url (str): Full URL of the API endpoint.
            payload (dict | None, optional): JSON payload to send with the request. Used for POST/PUT methods. Defaults to None.
            params (dict | None, optional): Query string parameters. Defaults to None.
            max_retries (int, optional): Number of times to retry the request in case of failure. Defaults to 3.
            expect_json (bool, optional): Whether to parse the response as JSON. Defaults to True.

        Raises:
            AccessDeniedError: Raised when the request is blocked by anti-bot protection (HTTP 403/429).
            RequestError: Raised for any other non-successful HTTP response.

        Returns:
            dict | str: Parsed JSON response from the server, or raw text if expect_json is False.
        """
        if max_retries == -1:
            max_retries = self.max_retries

        response: curl_cffi.Response = self.session.request(
            method=method,
            url=url,
            params=params,
            json=payload,
            verify=self.request_verify,
            timeout=self.timeout,
        )
        if response.ok:
            return response.json() if expect_json else response.text
        elif response.status_code in (403, 429):
            if max_retries > 0:
                self.session = self._init_session(
                    base_url=self.base_url,
                    proxy=self._proxy,
                    impersonate=self._impersonate,
                    user_agent=self._user_agent,
                    user_agents=self._user_agents,
                    request_verify=self.request_verify,
                )  # Re-init session
                return self._fetch(
                    method=method,
                    url=url,
                    payload=payload,
                    params=params,
                    max_retries=max_retries - 1,
                    expect_json=expect_json,
                )
            raise AccessDeniedError(
                "Access blocked by anti-bot protection. Try reducing request frequency or changing proxy."
            )
        elif response.status_code in (404, 410):
            raise NotFoundError("Unable to find the requested resource.")
        else:
            raise RequestError(
                f"Request failed with status code {response.status_code}."
            )

    def _fetch_text(self, url: str, max_retries: int = -1) -> str:
        return self._fetch(
            method="GET",
            url=url,
            max_retries=max_retries,
            expect_json=False,
        )

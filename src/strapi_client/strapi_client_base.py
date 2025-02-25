from pydantic import SecretStr
import httpx


class StrapiClientBase:
    """Base class with common logic for Strapi clients."""

    base_url: str
    timeout: httpx.Timeout | None = None
    _token: SecretStr | None = None

    def __init__(
            self,
            base_url: str,
            token: str | None = None,
            timeout: httpx.Timeout | None = None
    ) -> None:
        self.base_url = base_url.rstrip('/') + '/'
        if token:
            self._token = SecretStr(token)
        self.timeout = timeout

    @property
    def api_url(self) -> str:
        return self.base_url + 'api/'

    @property
    def _auth_header(self) -> dict[str, str]:
        if self._token is None:
            raise ValueError("Authorization token is not set, use authorize() method first")
        return {"Authorization": "Bearer " + self._token.get_secret_value()}

    @staticmethod
    def _check_response(res: httpx.Response, message: str) -> None:
        if not (200 <= res.status_code < 300):
            raise RuntimeError(f"{message} error {res.status_code}: {res.reason_phrase}")

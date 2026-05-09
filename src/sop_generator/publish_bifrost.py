import httpx
from pydantic import ValidationError

from .models import PublishResult


class PublishError(Exception):
    """Raised when Bifrost returns a 2xx response that is not a successful publish."""


class BifrostPublisher:
    def __init__(
        self,
        base_url: str,
        token: str | None = None,
        client: httpx.Client | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.client = client or httpx.Client()

    def publish_halo(self, payload: dict) -> PublishResult:
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        response = self.client.post(
            f"{self.base_url}/api/sop/halo/publish",
            json=payload,
            headers=headers,
        )
        response.raise_for_status()
        try:
            result = PublishResult.model_validate(response.json())
        except (ValueError, ValidationError) as exc:
            raise PublishError("Invalid publish response from Bifrost.") from exc

        if not result.ok:
            raise PublishError(result.message or "Bifrost reported publish failure.")

        return result

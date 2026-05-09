import httpx

from .models import PublishResult


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
        return PublishResult.model_validate(response.json())

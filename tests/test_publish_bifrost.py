import httpx

from sop_generator.publish_bifrost import BifrostPublisher


def test_publish_halo_posts_contract():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/sop/halo/publish"
        assert request.headers["authorization"] == "Bearer token"
        return httpx.Response(
            200,
            json={"ok": True, "kb_article_id": "123", "url": "https://halo.test/kb/123"},
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    result = BifrostPublisher("https://bifrost.test", token="token", client=client).publish_halo(
        {"title": "Reset MFA", "html": "<h1>Reset MFA</h1>"}
    )
    assert result.ok is True
    assert result.kb_article_id == "123"


def test_publish_halo_omits_authorization_without_token():
    def handler(request: httpx.Request) -> httpx.Response:
        assert "authorization" not in request.headers
        return httpx.Response(200, json={"ok": True})

    client = httpx.Client(transport=httpx.MockTransport(handler))

    result = BifrostPublisher("https://bifrost.test", client=client).publish_halo(
        {"title": "Reset MFA", "html": "<h1>Reset MFA</h1>"}
    )

    assert result.ok is True


def test_publish_halo_raises_for_error_response():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"ok": False, "message": "Halo publish failed"})

    client = httpx.Client(transport=httpx.MockTransport(handler))

    try:
        BifrostPublisher("https://bifrost.test", client=client).publish_halo({"title": "Reset MFA"})
    except httpx.HTTPStatusError as exc:
        assert exc.response.status_code == 500
    else:
        raise AssertionError("Expected HTTPStatusError")

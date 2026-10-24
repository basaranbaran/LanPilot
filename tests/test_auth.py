import pytest

from app import MIN_PIN_LENGTH, create_app, generate_pin

from conftest import PIN

PROTECTED_POSTS = ["/click", "/type", "/key", "/alttab", "/alttab_tab", "/alttab_release", "/logout"]


def test_root_redirects_to_login_without_session(client):
    response = client.get("/")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")


@pytest.mark.parametrize("path", PROTECTED_POSTS)
def test_protected_posts_return_401_and_touch_nothing(client, desktop, path):
    response = client.post(path, json={"x": 0.5, "y": 0.5, "text": "hi", "key": "enter"})
    assert response.status_code == 401
    assert desktop.calls == []


def test_video_feed_requires_login(client):
    assert client.get("/video_feed").status_code == 401


def test_login_page_is_public(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b'name="pin"' in response.data


def test_wrong_pin_is_rejected(client):
    response = client.post("/login", data={"pin": "000000"})
    assert response.status_code == 401
    assert b"Wrong PIN" in response.data
    assert client.get("/").status_code == 302


def test_missing_pin_is_rejected(client):
    assert client.post("/login", data={}).status_code == 401


def test_non_ascii_pin_does_not_crash(client):
    assert client.post("/login", data={"pin": "çğüşö123"}).status_code == 401


def test_correct_pin_opens_session(client):
    response = client.post("/login", data={"pin": PIN})
    assert response.status_code == 302
    assert client.get("/").status_code == 200


def test_session_cookie_flags(client):
    cookie = client.post("/login", data={"pin": PIN}).headers["Set-Cookie"]
    assert "HttpOnly" in cookie
    assert "SameSite=Strict" in cookie


def test_logout_ends_session_and_releases_alt(authed, desktop):
    assert authed.post("/logout").status_code == 200
    assert ("key_up", "alt") in desktop.calls
    assert authed.post("/key", json={"key": "enter"}).status_code == 401


def test_lockout_after_five_failures_even_with_correct_pin(client, clock):
    for _ in range(5):
        assert client.post("/login", data={"pin": "000000"}).status_code == 401
    response = client.post("/login", data={"pin": PIN})
    assert response.status_code == 429
    assert int(response.headers["Retry-After"]) > 0
    assert client.get("/").status_code == 302


def test_lockout_expires(client, clock):
    for _ in range(5):
        client.post("/login", data={"pin": "000000"})
    clock.now += 301
    assert client.post("/login", data={"pin": PIN}).status_code == 302


def test_global_limit_blocks_other_addresses(app, clock):
    for i in range(20):
        other = app.test_client()
        other.environ_base["REMOTE_ADDR"] = f"10.0.0.{i}"
        assert other.post("/login", data={"pin": "000000"}).status_code == 401
    fresh = app.test_client()
    fresh.environ_base["REMOTE_ADDR"] = "10.0.1.1"
    assert fresh.post("/login", data={"pin": PIN}).status_code == 429


def test_successful_login_resets_ip_counter(client):
    for _ in range(4):
        client.post("/login", data={"pin": "000000"})
    assert client.post("/login", data={"pin": PIN}).status_code == 302
    client.post("/logout")
    for _ in range(4):
        assert client.post("/login", data={"pin": "000000"}).status_code == 401


def test_security_headers(client):
    headers = client.get("/login").headers
    assert headers["Cache-Control"] == "no-store"
    assert headers["X-Frame-Options"] == "DENY"
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert "frame-ancestors 'none'" in headers["Content-Security-Policy"]


def test_short_pin_is_refused(desktop):
    with pytest.raises(ValueError):
        create_app(controller=desktop, pin="12345")


def test_generated_pin_shape():
    pins = {generate_pin() for _ in range(50)}
    assert len(pins) > 1
    assert all(len(p) == MIN_PIN_LENGTH and p.isdigit() for p in pins)

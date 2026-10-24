import pytest

from app import ALLOWED_KEYS, MAX_TEXT_LENGTH


def test_index_gets_screen_size(authed):
    html = authed.get("/").get_data(as_text=True)
    assert 'data-screen-width="1920"' in html
    assert 'data-screen-height="1080"' in html


def test_click_maps_fraction_to_pixels(authed, desktop):
    assert authed.post("/click", json={"x": 0.5, "y": 0.25}).status_code == 200
    assert desktop.calls == [("click", 960, 270)]


def test_click_on_far_edge_stays_on_screen(authed, desktop):
    authed.post("/click", json={"x": 1, "y": 1})
    assert desktop.calls == [("click", 1919, 1079)]


@pytest.mark.parametrize("payload", [
    {}, {"x": 0.5}, {"x": "0.5", "y": 0.5}, {"x": -0.1, "y": 0.5}, {"x": 0.5, "y": 1.01},
    {"x": True, "y": 0.5}, {"x": None, "y": 0.5}, {"x": [0.5], "y": 0.5},
])
def test_click_rejects_bad_coordinates(authed, desktop, payload):
    assert authed.post("/click", json=payload).status_code == 400
    assert desktop.calls == []


def test_click_rejects_nan(authed, desktop):
    response = authed.post("/click", data='{"x": NaN, "y": 0.5}', content_type="application/json")
    assert response.status_code == 400
    assert desktop.calls == []


def test_type_forwards_text(authed, desktop):
    assert authed.post("/type", json={"text": "hello"}).status_code == 200
    assert desktop.calls == [("write", "hello")]


@pytest.mark.parametrize("payload", [{}, {"text": ""}, {"text": 5}, {"text": ["a"]}])
def test_type_rejects_bad_text(authed, desktop, payload):
    assert authed.post("/type", json=payload).status_code == 400
    assert desktop.calls == []


def test_type_limit(authed, desktop):
    assert authed.post("/type", json={"text": "a" * MAX_TEXT_LENGTH}).status_code == 200
    assert authed.post("/type", json={"text": "a" * (MAX_TEXT_LENGTH + 1)}).status_code == 400
    assert len(desktop.calls) == 1


@pytest.mark.parametrize("key", sorted(ALLOWED_KEYS))
def test_allowed_keys_are_pressed(authed, desktop, key):
    assert authed.post("/key", json={"key": key}).status_code == 200
    assert desktop.calls == [("press", key)]


@pytest.mark.parametrize("key", ["win", "ctrl", "f4", "ENTER", "", None, 7, ["enter"]])
def test_other_keys_are_rejected(authed, desktop, key):
    assert authed.post("/key", json={"key": key}).status_code == 400
    assert desktop.calls == []


def test_form_encoded_post_is_not_accepted(authed, desktop):
    """Cross-site forms cannot send JSON, so requiring it blocks CSRF-style posts."""
    response = authed.post("/key", data={"key": "enter"})
    assert response.status_code == 400
    assert desktop.calls == []


def test_non_object_json_is_rejected(authed, desktop):
    assert authed.post("/key", json=["enter"]).status_code == 400
    assert authed.post("/click", json=5).status_code == 400
    assert desktop.calls == []


def test_oversized_body_is_rejected(authed, desktop):
    response = authed.post("/type", json={"text": "a" * 20_000})
    assert response.status_code == 413
    assert desktop.calls == []


def test_alt_tab_sequence(authed, desktop):
    assert authed.post("/alttab").status_code == 200
    assert authed.post("/alttab_tab").status_code == 200
    assert authed.post("/alttab_release").status_code == 200
    assert desktop.calls == [
        ("key_down", "alt"), ("press", "tab"), ("press", "tab"), ("key_up", "alt"),
    ]


def test_controller_failure_returns_500_without_details(authed, desktop):
    desktop.fail_next = True
    response = authed.post("/key", json={"key": "enter"})
    assert response.status_code == 500
    assert response.get_json() == {"status": "error", "message": "Could not send input to the PC."}


def test_video_feed_streams_mjpeg_frames(authed):
    response = authed.get("/video_feed")
    assert response.mimetype == "multipart/x-mixed-replace"
    assert b"--frame" in response.get_data()
    assert b"fake-jpeg" in response.get_data()

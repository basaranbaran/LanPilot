"""LanPilot: control your PC from a phone over a local network or Tailscale."""
from __future__ import annotations

import argparse
import hmac
import io
import math
import os
import secrets
import socket
import time
from datetime import timedelta
from typing import Callable, Dict, Iterator, List, Optional, Protocol, Tuple

from flask import (
    Flask,
    Response,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

MIN_PIN_LENGTH = 6
MAX_PIN_LENGTH = 128
MAX_TEXT_LENGTH = 200
SESSION_HOURS = 12

# Keys the phone UI may press. Anything else is rejected instead of forwarded to PyAutoGUI.
ALLOWED_KEYS = frozenset({
    "enter", "backspace", "delete", "tab", "esc", "space",
    "up", "down", "left", "right", "home", "end", "pageup", "pagedown",
})


class Controller(Protocol):
    """What the web layer needs from the desktop. Tests replace this with a fake."""

    width: int
    height: int

    def click(self, x: int, y: int) -> None: ...
    def write(self, text: str) -> None: ...
    def press(self, key: str) -> None: ...
    def key_down(self, key: str) -> None: ...
    def key_up(self, key: str) -> None: ...
    def frames(self) -> Iterator[bytes]: ...


class DesktopController:
    """Real controller built on PyAutoGUI and mss. Imported lazily so tests run headless."""

    def __init__(self) -> None:
        import pyautogui

        pyautogui.FAILSAFE = False
        self._gui = pyautogui
        self.width, self.height = pyautogui.size()

    def click(self, x: int, y: int) -> None:
        self._gui.moveTo(x, y)
        self._gui.click()

    def write(self, text: str) -> None:
        self._gui.write(text, interval=0.05)

    def press(self, key: str) -> None:
        self._gui.press(key)

    def key_down(self, key: str) -> None:
        self._gui.keyDown(key)

    def key_up(self, key: str) -> None:
        self._gui.keyUp(key)

    def frames(self) -> Iterator[bytes]:
        """Captures the screen and yields JPEG frames at 75% scale."""
        import mss
        from PIL import Image

        new_size = (int(self.width * 0.75), int(self.height * 0.75))
        with mss.mss() as sct:
            monitor = {"top": 0, "left": 0, "width": self.width, "height": self.height}
            while True:
                try:
                    shot = sct.grab(monitor)
                    img = Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")
                    buf = io.BytesIO()
                    img.resize(new_size).save(buf, format="JPEG", quality=70)
                    yield buf.getvalue()
                except Exception as e:
                    print(f"Stream Error: {e}")
                    time.sleep(0.1)


class AttemptLimiter:
    """Locks a key out after too many failures inside a sliding window."""

    def __init__(self, max_failures: int, window_seconds: float,
                 clock: Callable[[], float] = time.monotonic) -> None:
        self.max_failures = max_failures
        self.window = window_seconds
        self._clock = clock
        self._failures: Dict[str, List[float]] = {}

    def _recent(self, key: str) -> List[float]:
        cutoff = self._clock() - self.window
        recent = [t for t in self._failures.get(key, []) if t > cutoff]
        if recent:
            self._failures[key] = recent
        else:
            self._failures.pop(key, None)
        return recent

    def retry_after(self, key: str) -> float:
        """Seconds until the key may try again, or 0 if it is not locked."""
        recent = self._recent(key)
        if len(recent) < self.max_failures:
            return 0.0
        return max(0.0, recent[0] + self.window - self._clock())

    def fail(self, key: str) -> None:
        self._recent(key)
        self._failures.setdefault(key, []).append(self._clock())

    def reset(self, key: str) -> None:
        self._failures.pop(key, None)


def generate_pin() -> str:
    return f"{secrets.randbelow(10 ** MIN_PIN_LENGTH):0{MIN_PIN_LENGTH}d}"


def _is_fraction(value: object) -> bool:
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and 0 <= value <= 1)


def _error(message: str, status: int):
    return jsonify({"status": "error", "message": message}), status


def get_ip_addresses() -> Tuple[List[str], List[str], List[str]]:
    """Retrieves all IPv4 addresses associated with the host."""
    ip_list: List[str] = []
    tailscale_ips: List[str] = []
    local_ips: List[str] = []
    try:
        hostname = socket.gethostname()
        _, _, ips = socket.gethostbyname_ex(hostname)
        for ip in ips:
            if not ip.startswith("127."):
                ip_list.append(ip)
                # Tailscale IPs start with 100.x.x.x
                if ip.startswith("100."):
                    tailscale_ips.append(ip)
                else:
                    local_ips.append(ip)
    except Exception as e:
        print(f"Error getting IPs: {e}")
    return ip_list, tailscale_ips, local_ips


def create_app(controller: Optional[Controller] = None, pin: Optional[str] = None,
               clock: Callable[[], float] = time.monotonic) -> Flask:
    pin = pin if pin is not None else generate_pin()
    if not MIN_PIN_LENGTH <= len(pin) <= MAX_PIN_LENGTH:
        raise ValueError(f"PIN must be {MIN_PIN_LENGTH} to {MAX_PIN_LENGTH} characters long.")
    pin_bytes = pin.encode("utf-8")
    desktop: Controller = controller if controller is not None else DesktopController()

    app = Flask(__name__, static_folder=None)
    # A fresh key per start: sessions never outlive the process.
    app.secret_key = secrets.token_bytes(32)
    app.config.update(
        SESSION_COOKIE_NAME="lanpilot_session",
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Strict",
        PERMANENT_SESSION_LIFETIME=timedelta(hours=SESSION_HOURS),
        MAX_CONTENT_LENGTH=16 * 1024,
    )
    ip_limiter = AttemptLimiter(max_failures=5, window_seconds=300, clock=clock)
    global_limiter = AttemptLimiter(max_failures=20, window_seconds=600, clock=clock)

    @app.before_request
    def require_login():
        if request.endpoint == "login" or session.get("auth"):
            return None
        if request.method == "GET" and request.path == "/":
            return redirect(url_for("login"))
        return _error("Authentication required", 401)

    @app.after_request
    def harden_headers(response: Response) -> Response:
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = "frame-ancestors 'none'"
        return response

    def body() -> dict:
        """JSON object body. Requiring JSON also blocks cross-site form posts."""
        data = request.get_json(silent=True)
        return data if isinstance(data, dict) else {}

    def run(action: Callable[[], None]):
        try:
            action()
        except Exception as e:
            print(f"Input Error: {e}")
            return _error("Could not send input to the PC.", 500)
        return jsonify({"status": "success"})

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "GET":
            if session.get("auth"):
                return redirect(url_for("index"))
            return render_template("login.html", error=None)

        ip = request.remote_addr or "unknown"
        wait = max(ip_limiter.retry_after(ip), global_limiter.retry_after("*"))
        if wait > 0:
            seconds = math.ceil(wait)
            return (render_template("login.html",
                                    error=f"Too many attempts. Try again in {seconds} s."),
                    429, {"Retry-After": str(seconds)})

        # One character past the maximum, so an over-long guess can never match by truncation.
        candidate = request.form.get("pin", "")[:MAX_PIN_LENGTH + 1].encode("utf-8")
        if hmac.compare_digest(candidate, pin_bytes):
            ip_limiter.reset(ip)
            session.clear()
            session["auth"] = True
            session.permanent = True
            return redirect(url_for("index"))

        ip_limiter.fail(ip)
        global_limiter.fail("*")
        return render_template("login.html", error="Wrong PIN."), 401

    @app.route("/logout", methods=["POST"])
    def logout():
        session.clear()
        try:
            desktop.key_up("alt")  # never leave Alt held after locking
        except Exception as e:
            print(f"Input Error: {e}")
        return jsonify({"status": "success"})

    @app.route("/")
    def index():
        return render_template(
            "index.html",
            pc_screen_width=desktop.width,
            pc_screen_height=desktop.height,
        )

    @app.route("/video_feed")
    def video_feed():
        def stream() -> Iterator[bytes]:
            for frame in desktop.frames():
                yield (b"--frame\r\n"
                       b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")
        return Response(stream(), mimetype="multipart/x-mixed-replace; boundary=frame")

    @app.route("/click", methods=["POST"])
    def click():
        data = body()
        x, y = data.get("x"), data.get("y")
        if not (_is_fraction(x) and _is_fraction(y)):
            return _error("x and y must be numbers between 0 and 1.", 400)
        px = min(int(x * desktop.width), desktop.width - 1)
        py = min(int(y * desktop.height), desktop.height - 1)
        return run(lambda: desktop.click(px, py))

    @app.route("/type", methods=["POST"])
    def type_text():
        text = body().get("text")
        if not isinstance(text, str) or not text:
            return _error("text must be a non-empty string.", 400)
        if len(text) > MAX_TEXT_LENGTH:
            return _error(f"text is limited to {MAX_TEXT_LENGTH} characters.", 400)
        return run(lambda: desktop.write(text))

    @app.route("/key", methods=["POST"])
    def press_key():
        key = body().get("key")
        if not isinstance(key, str) or key not in ALLOWED_KEYS:
            return _error("Key is not allowed.", 400)
        return run(lambda: desktop.press(key))

    @app.route("/alttab", methods=["POST"])
    def alt_tab():
        """Opens Alt-Tab menu and keeps Alt key pressed."""
        def action() -> None:
            desktop.key_down("alt")
            desktop.press("tab")
        return run(action)

    @app.route("/alttab_tab", methods=["POST"])
    def alt_tab_navigate():
        """Presses Tab while Alt is held to navigate through windows."""
        return run(lambda: desktop.press("tab"))

    @app.route("/alttab_release", methods=["POST"])
    def alt_tab_release():
        """Releases Alt key to select the current window."""
        return run(lambda: desktop.key_up("alt"))

    return app


def print_banner(host: str, port: int, pin: str, pin_from_env: bool) -> None:
    print("\n" + "=" * 50)
    print("🚀 LanPilot is Launching!")
    print("=" * 50 + "\n")

    if host in ("0.0.0.0", "::"):
        ips, tailscale_ips, local_ips = get_ip_addresses()
        if not ips:
            print("⚠️  No network interface found! You might only be able to connect via localhost.")
        # Show Tailscale IPs first (if available) for remote access
        if tailscale_ips:
            print("🌍 Tailscale VPN (Remote Access):")
            for ip in tailscale_ips:
                print(f"   🔒 http://{ip}:{port}")
            print()
        if local_ips:
            print("📱 Local Network (Same WiFi):")
            for ip in local_ips:
                print(f"   👉 http://{ip}:{port}")
            print()
        print(f"   💻 Local access: http://127.0.0.1:{port}")
    else:
        print(f"   👉 http://{host}:{port}")

    print()
    if pin_from_env:
        print("🔑 PIN: taken from the LANPILOT_PIN environment variable")
    else:
        print(f"🔑 PIN: {pin}   (new one on every start; set LANPILOT_PIN to keep your own)")
    print("=" * 50 + "\n")


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="0.0.0.0",
                        help="Interface to bind (default: 0.0.0.0, all interfaces).")
    parser.add_argument("--port", type=int, default=5000, help="Port to listen on (default: 5000).")
    args = parser.parse_args(argv)

    env_pin = os.environ.get("LANPILOT_PIN")
    if env_pin is not None and not MIN_PIN_LENGTH <= len(env_pin) <= MAX_PIN_LENGTH:
        parser.error(f"LANPILOT_PIN must be {MIN_PIN_LENGTH} to {MAX_PIN_LENGTH} characters long.")
    pin = env_pin or generate_pin()

    app = create_app(pin=pin)
    print_banner(args.host, args.port, pin, pin_from_env=bool(env_pin))
    app.run(host=args.host, port=args.port, threaded=True)


if __name__ == "__main__":
    main()

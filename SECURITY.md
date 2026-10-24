# Security Policy

LanPilot gives a phone full mouse and keyboard control of a PC and streams its screen, so security bugs matter here.

## Supported versions

Only the latest release receives fixes.

## Reporting a vulnerability

Please do not open a public issue. Use GitHub's private reporting instead:
[Security → Report a vulnerability](https://github.com/basaranbaran/LanPilot/security/advisories/new).

Include what you did, what you expected, and what happened. You will get a first reply within a week.

## What LanPilot protects

- **PIN login.** Every route except `/login` needs a session. A random 6-digit PIN is generated on each start, or you can set your own with `LANPILOT_PIN` (at least 6 characters).
- **Brute-force lockout.** 5 wrong PINs lock an address out for 5 minutes. 20 wrong PINs from any addresses pause all logins for 10 minutes.
- **Session cookie.** Signed, `HttpOnly`, `SameSite=Strict`, valid for 12 hours, and invalidated on every restart.
- **Input validation.** Clicks must be coordinates between 0 and 1. Typed text is capped at 200 characters. Only a short list of keys can be pressed (Enter, Backspace, arrows, and similar). Request bodies must be JSON and are capped at 16 KB.

## What it does not protect

- **No TLS.** Traffic is plain HTTP, so the PIN and the screen stream can be read by anyone who can sniff your network. Use it on a network you trust, or over Tailscale, which encrypts the link. Do not expose the port to the internet.
- **Trusted users only.** Anyone who has the PIN controls the PC with your privileges.
- **Built-in Flask server.** It is the development server. Keep LanPilot off untrusted networks.

To limit exposure, bind to a single interface: `python app.py --host 100.x.y.z` (your Tailscale address) or `--host 127.0.0.1`.

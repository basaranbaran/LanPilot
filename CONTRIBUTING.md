# Contributing to LanPilot

Thanks for your interest in LanPilot! Bug reports, ideas, docs fixes and code are all welcome.

## Getting started

1. Fork the repo and clone your fork.
2. Create a branch for your change:
   ```bash
   git checkout -b fix/short-description
   ```
3. Install the dev requirements and run the tests:
   ```bash
   pip install -r requirements-dev.txt
   python -m pytest
   ```
   The web layer talks to the desktop through a small `Controller` interface, so the tests use a fake one and never move your real mouse.
4. Make your change, add or update tests if behavior changes, and run the tests again.
5. Push your branch and open a pull request against `main`.

CI runs the same tests on Python 3.9 and 3.12 for every pull request.

## Pull request guidelines

- Keep each PR focused on one thing. Small PRs are reviewed faster.
- For anything bigger than a small fix, please open an issue first so we can agree on the approach.
- Describe what changed and why. Screenshots help for UI changes.
- Make sure the tests pass.

## Reporting bugs and requesting features

Use the [issue templates](https://github.com/basaranbaran/LanPilot/issues/new/choose). Please include your OS, Python version and how you connect (local Wi-Fi or Tailscale).

## Security issues

Please do not open a public issue. Follow [SECURITY.md](SECURITY.md) instead.

## Good first contributions

- Try LanPilot on macOS or Linux and report what works and what does not.
- Improve the docs, screenshots or translations.
- Add tests.

Look for issues labeled `good first issue` and `help wanted`.

By contributing, you agree that your contributions are licensed under the [MIT License](LICENSE).

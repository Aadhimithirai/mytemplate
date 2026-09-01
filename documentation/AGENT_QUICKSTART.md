# Agent Quickstart

Use this when you want to get productive in this repo with minimal context.

## 1) Setup

```bash
cd /Users/sumukh/code/MyTemplate
python3 -m venv env
source env/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 2) Initialize Local Data

```bash
MYTEMPLATE_ENV=dev ./manage.py resetdb
```

This seeds:
- `user@example.com` / `test`
- `admin@example.com` / `admin`

## 3) Run App

```bash
FLASK_APP=manage flask --debug run
```

Open [http://localhost:5000](http://localhost:5000)

## 4) Validate Changes

```bash
# Fast smoke tests
make agent-smoke

# Full tracked tests + coverage (recommended)
make agent-test

# Optional: full test discovery (also includes untracked local tests)
MYTEMPLATE_ENV=test ./manage.py test --coverage
```

## 5) High-Signal File Locations

- App factory and blueprint wiring: `mytemplate/__init__.py`
- Environment configs: `mytemplate/settings.py`
- Auth + signup/login: `mytemplate/controllers/auth.py`
- Dashboard routes: `mytemplate/controllers/dashboard/`
- API resources: `mytemplate/api/`
- Core models: `mytemplate/models/`
- Templates: `mytemplate/templates/`
- Tests: `tests/`

## Troubleshooting

- `flask run` cannot find app:
  - Ensure `FLASK_APP=manage`
- Tests fail with config mismatch:
  - Ensure `MYTEMPLATE_ENV=test`
- OAuth/Stripe paths not working locally:
  - Load local env vars from `.env.local` (see `.env.local.sample`)

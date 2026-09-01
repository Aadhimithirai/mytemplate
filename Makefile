.PHONY: help env deps browsers resetdb run clean lint security test test-ui build check \
        agent-setup agent-resetdb agent-smoke agent-test

VENV_PYTHON=env/bin/python
PYTEST=MYTEMPLATE_ENV=test $(VENV_PYTHON) -m pytest
ARTIFACTS=artifacts
AGENT_TEST_FILES=$(shell git ls-files 'tests/*.py')

help:
	@echo "  Development"
	@echo "    env           create a virtualenv in ./env and install dependencies"
	@echo "    browsers      install the Chromium build Playwright drives"
	@echo "    resetdb       drop, recreate and seed the development database"
	@echo "    run           start the development server on :5000"
	@echo "    clean         remove caches, build output and reports"
	@echo ""
	@echo "  Quality pipeline (all reports land in ./$(ARTIFACTS))"
	@echo "    lint          static analysis with Ruff"
	@echo "    security      security scan with Bandit"
	@echo "    test          backend tests with pytest, JUnit XML + coverage"
	@echo "    test-ui       browser tests with Playwright, JUnit XML"
	@echo "    build         run everything, always write reports, fail if any step failed"
	@echo ""
	@echo "  First time: make env && make browsers && make build"

env:
	python3 -m venv env
	$(VENV_PYTHON) -m pip install --upgrade pip
	$(VENV_PYTHON) -m pip install -r requirements.txt

deps:
	$(VENV_PYTHON) -m pip install -r requirements.txt

browsers:
	$(VENV_PYTHON) -m playwright install chromium

resetdb:
	MYTEMPLATE_ENV=dev FLASK_APP=manage $(VENV_PYTHON) -m flask resetdb

run:
	MYTEMPLATE_ENV=dev FLASK_APP=manage $(VENV_PYTHON) -m flask run

clean:
	find . -path ./env -prune -o -name '__pycache__' -type d -print0 | xargs -0 rm -rf
	find . -path ./env -prune -o -name '*.pyc' -print0 | xargs -0 rm -f
	rm -rf $(ARTIFACTS) .pytest_cache .ruff_cache .coverage coverage_report

$(ARTIFACTS):
	@mkdir -p $(ARTIFACTS)/tests $(ARTIFACTS)/coverage $(ARTIFACTS)/lint $(ARTIFACTS)/security

# ---------------------------------------------------------------- checks ----
# Each target writes a machine-readable report AND prints a readable summary,
# so a failure is visible in the console without opening a file.

lint: $(ARTIFACTS)
	@echo "==> Ruff"
	@$(VENV_PYTHON) -m ruff check --output-format=json --output-file=$(ARTIFACTS)/lint/ruff.json . || true
	$(VENV_PYTHON) -m ruff check --output-format=concise . | tee $(ARTIFACTS)/lint/ruff.txt

security: $(ARTIFACTS)
	@echo "==> Bandit"
	@$(VENV_PYTHON) -m bandit -r mytemplate -f json -o $(ARTIFACTS)/security/bandit.json --quiet || true
	$(VENV_PYTHON) -m bandit -r mytemplate --quiet | tee $(ARTIFACTS)/security/bandit.txt

test: $(ARTIFACTS)
	@echo "==> pytest (backend)"
	$(PYTEST) tests -m "not ui" \
		--junitxml=$(ARTIFACTS)/tests/junit-backend.xml \
		--cov=mytemplate \
		--cov-report=term-missing \
		--cov-report=xml:$(ARTIFACTS)/coverage/coverage.xml \
		--cov-report=html:$(ARTIFACTS)/coverage/html \
		--cov-fail-under=80

test-ui: $(ARTIFACTS)
	@echo "==> Playwright (UI)"
	$(PYTEST) tests/ui -m ui --junitxml=$(ARTIFACTS)/tests/junit-ui.xml

# ----------------------------------------------------------------- build ----
# Runs every check, collects every report, then fails if anything failed.
# Steps deliberately do not short-circuit: a lint failure must not hide a
# test failure, because a partial report set is the least useful outcome.

build:
	@rm -rf $(ARTIFACTS)
	@mkdir -p $(ARTIFACTS)/tests $(ARTIFACTS)/coverage $(ARTIFACTS)/lint $(ARTIFACTS)/security
	@status=0; \
	$(MAKE) --no-print-directory lint    || status=1; \
	$(MAKE) --no-print-directory security || status=1; \
	$(MAKE) --no-print-directory test    || status=1; \
	$(MAKE) --no-print-directory test-ui || status=1; \
	echo ""; \
	echo "================= build artifacts ================="; \
	find $(ARTIFACTS) -type f -not -path '*/coverage/html/*' | sort | sed 's/^/  /'; \
	echo "  $(ARTIFACTS)/coverage/html/index.html  (+$$(find $(ARTIFACTS)/coverage/html -type f | wc -l) files)"; \
	echo "==================================================="; \
	if [ $$status -ne 0 ]; then echo "BUILD FAILED"; else echo "BUILD PASSED"; fi; \
	exit $$status

check: build

# ------------------------------------------------------- agent shortcuts ----

agent-setup: env

agent-resetdb:
	@if [ ! -x "$(VENV_PYTHON)" ]; then echo "Run 'make env' first."; exit 1; fi
	MYTEMPLATE_ENV=dev $(VENV_PYTHON) manage.py resetdb

agent-smoke:
	@if [ ! -x "$(VENV_PYTHON)" ]; then echo "Run 'make env' first."; exit 1; fi
	$(PYTEST) -q tests/test_urls.py tests/test_login.py

agent-test:
	@if [ ! -x "$(VENV_PYTHON)" ]; then echo "Run 'make env' first."; exit 1; fi
	$(PYTEST) --cov-report=term-missing --cov=mytemplate $(AGENT_TEST_FILES)

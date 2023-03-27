.PHONY: dev-env-setup
dev-env-setup:
	poetry install
	poetry run pre-commit install
	echo -e "---=== DONE: DEV ENV SETUP ===---"

.PHONY: test-coverage
test-coverage:
	export PYTHONHASHSEED=0
	poetry run pytest -v --cov pidge --cov-fail-under 80

.PHONY: test
test:
	export PYTHONHASHSEED=0
	poetry run pytest

.PHONY: lint
lint:
	poetry run pre-commit run --all-files

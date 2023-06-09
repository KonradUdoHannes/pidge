.PHONY: dev-env-setup
dev-env-setup:
	poetry install
	poetry run pre-commit install
	echo -e "---=== DONE: DEV ENV SETUP ===---"

.PHONY: test-coverage
test-coverage:
	poetry run pytest -v --cov pidge --cov-fail-under 80


.PHONY: test-coverage-html
test-coverage-html:
	poetry run pytest -v --cov pidge --cov-fail-under 80 --cov-report=html

.PHONY: test
test:
	poetry run pytest

.PHONY: lint
lint:
	poetry run pre-commit run --all-files


.PHONY: web-ui
web-ui:
	poetry run python -m pidge

.PHONY:build-docker-image
build-docker-image:
	docker build -t pidge:latest .

.PHONY:deploy-docker
deploy-docker:
	docker run -d --rm -p 5006:5006 pidge:latest


.PHONY:build
build:
	poetry build -f sdist


.PHONY:upload-test
upload-test: build
	version=$$(sed -n -r "s/^version = \"([^\"]*)\"/\1/p" pyproject.toml); poetry run twine upload --repository testpypi dist/pidge-$$version.tar.gz


.PHONY:upload
upload: build
	version=$$(sed -n -r "s/^version = \"([^\"]*)\"/\1/p" pyproject.toml); poetry run twine upload dist/pidge-$$version.tar.gz

V = 0
Q = $(if $(filter 1,$V),,@)
M = $(shell printf "\033[34;1mepr-python ▶\033[0m")

.PHONY: install
install: ;$(info $(M) installing epr...) @ ## Installs epr into a virtualenv called epr-python
	$Q python3 -m venv $(DESTDIR).virtualenvs/epr-python && \
	$Q $(DESTDIR).virtualenvs/epr-python/bin/python3 -m pip install \
				-e .

.PHONY: megalint
megalint: ; $(info $(M) running megalinter...) @ ## Run megalinter
	$Q ruff format -v src/epr/ tests/ && ruff check --fix -v src/epr/ tests/

.PHONY: tests
tests: ; $(info $(M) running tests...) @ ## Run tests
	$Q tox --recreate

.PHONY: release
release: ; $(info $(M) running tox...) @ ## Run tox
	$Q tox -e release

.PHONY: wheel
wheel: ; $(info $(M) creating sdist bdist_wheel...) @ ## Create an sdist bdist_wheel
	$Q pip install --upgrade build && python -m build --sdist --wheel

.PHONY: clean
clean: ; $(info $(M) cleaning...)	@ ## Cleanup everything
	@rm -rvf bin tools vendor build dist
	@rm -rvf *.egg-info *.egg .pytest_cache .ruff_cache .tox .coverage src/*.egg-info 
	@rm -rvf src/epr/__pycache__ tests/__pycache__ tests/unit/__pycache__

.PHONY: help
help:
	@grep -E '^[ a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

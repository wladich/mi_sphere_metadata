define help
Available targets:
	pylint
	flake8
	mypy
	check
	venv [path=PATH_TO_VENV]
		create venv for development
		default path=./venv
	common arguments:
		python=PYTHON3_EXECUTABLE, defaults to python3
endef
export help

path?=./venv
python?=python3


help:
	@echo "$$help"

pylint:
	pylint ./*.py tests

black:
	black --diff --check -q ./*.py tests

flake8:
	flake8 *.py tests

test:
	pytest tests

check: pylint black flake8
	@echo All checks passed.

.PHONY: venv
venv:
	@echo Will install at $(path)
	$(python) -m venv $(path)
	SETUPTOOLS_ENABLE_FEATURES="legacy-editable" $(path)/bin/pip install -e ".[test]"

clean:
	rm -rf ./mypy_cache ./*.egg-info ./.mypy_cache ./__pycache__ ./.pytest_cache ./venv ./build
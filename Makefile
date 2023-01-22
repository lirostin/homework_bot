VENV = venv
PYTHON = py -3.9
PROJECT_NAME = *.py

.ONESHELL:

ACTIVATE_WINDOWS:=. $(VENV)/Scripts/activate
ACTIVATE_LINUX:=. $(VENV)/bin/activate

setup:
	$(PYTHON) -m venv $(VENV)
	$(ACTIVATE_WINDOWS)
	pip install --upgrade pip
	pip install -r requirements.txt
	touch .env

clean:
	rm -rf venv

lint:
	isort ${PROJECT_NAME}
	black  --line-length 79 ${PROJECT_NAME}
	flake8 ${PROJECT_NAME} 

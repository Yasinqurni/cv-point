SHELL := /bin/bash

VENV := .venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

.PHONY: venv install run run-prod clean help

venv:
	python3 -m venv $(VENV)

install: venv
	$(PY) -m pip install --upgrade pip setuptools wheel
	$(PIP) install -r requirements.txt

run:
	$(PY) -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-prod:
	$(PY) -m uvicorn app.main:app --host 0.0.0.0 --port 8000

clean:
	rm -rf $(VENV)

help:
	@echo "make venv       # create virtual env"
	@echo "make install    # upgrade pip & install requirements"
	@echo "make run        # run dev server with reload"
	@echo "make run-prod   # run server without reload"
	@echo "make clean      # remove venv"

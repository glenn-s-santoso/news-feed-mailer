# Makefile – helper tasks for development / setup

.PHONY: help venv uv poetry clean run pre-commit-install lint

ifeq ($(OS),Windows_NT)
VENV_PY := $(VENV_DIR)/Scripts/activate
else
VENV_PY := $(VENV_DIR)/bin/activate
endif

PYTHON ?= python
VENV_DIR ?= .venv

help:
	@echo "Available targets:"
	@echo "Setup (pick ONE of the following):"
	@echo "  venv       – Create $(VENV_DIR) and install deps with classic pip"
	@echo "  uv         – Same as venv but using 'uv' for much faster installs"
	@echo "  poetry     – Install dependencies via Poetry (manages its own venv)"
	@echo "  run     – run the application (expects env + deps ready)"
	@echo "  clean   – remove $(VENV_DIR) and Poetry virtualenv"
	@echo "  pre-commit-install – install pre-commit hooks"
	@echo "  lint     – run ruff and black checks"

# ------------------------------------------------------------------------------
# Classic venv + pip
# ------------------------------------------------------------------------------
venv:
	@echo "Creating classic venv and installing requirements.txt ..."
	$(PYTHON) -m venv $(VENV_DIR)
	source $(VENV_PY)
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

# ------------------------------------------------------------------------------
# uv (rust-based installer) – much faster, still uses a venv
# ------------------------------------------------------------------------------
uv:
	@echo "Creating venv with 'uv' and installing requirements.txt ..."
	$(PYTHON) -m pip install --upgrade uv
	uv venv $(VENV_DIR)
	source $(VENV_PY)
	uv pip install -r requirements.txt

# ------------------------------------------------------------------------------
# Poetry – uses pyproject.toml / poetry.lock
# ------------------------------------------------------------------------------
poetry:
	@echo "Installing project via Poetry ..."
	$(PYTHON) -m pip install --upgrade poetry
	poetry env activate
	poetry install

# ------------------------------------------------------------------------------
# Convenience targets
# ------------------------------------------------------------------------------
run:
	@echo "Running news-mailer..."
	$(PYTHON) -m src.news_mailer.main

pre-commit-install:
	@echo "Installing pre-commit hooks..."
	@if command -v uv >NUL 2>&1 ; then \
		uv pip install pre-commit ; \
	else \
		python -m pip install --upgrade pre-commit ; \
	fi
	pre-commit install

lint:
	@echo "Running ruff and black checks..."
	@echo "Running pre-commit on modified (unstaged) files...";
	@changes="$(shell git diff --name-only)"; \
	if [ -n "$$changes" ]; then \
	  pre-commit run --files $$changes; \
	else \
	  echo "No unstaged changes to lint."; \
	fi

clean:
	@echo "Cleaning up..."
	rmdir /s /q $(VENV_DIR) 2> NUL || true
	poetry env remove --all 2> NUL || true

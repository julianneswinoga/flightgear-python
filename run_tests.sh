#!/bin/bash
set -e

python3.6 -m venv --clear .venv
. ./.venv/bin/activate
pip3 install -U pip
pip3 install -U poetry
poetry update
poetry build
poetry install
pytest --cov-report term-missing:skip-covered --cov=flightgear_python tests/

#!/bin/bash
set -e

if [ "$1" = 'clean' ]; then
  python3.6 -m venv --clear .venv
fi

. ./.venv/bin/activate

if [ "$1" = 'clean' ]; then
  pip3 install -U pip
  pip3 install -U poetry
  poetry update -vvv
fi
poetry build
poetry install
pytest --cov-report term-missing:skip-covered --cov=flightgear_python tests/

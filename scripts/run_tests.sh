#!/bin/bash
set -e

if [ "$1" = 'clean' ]; then
  python3 -m venv --clear .venv
fi

. ./.venv/bin/activate

if [ "$1" = 'clean' ]; then
  pip3 install -U pip
  pip3 install -U poetry
  pip3 install -U Cython
#  poetry update -vvv
fi

# Remove clean from args
for arg in "$@"; do
  shift
  [ "$arg" = "clean" ] && continue
  set -- "$@" "$arg"
done

poetry install
poetry build
pytest --cov-report term-missing:skip-covered --cov=flightgear_python tests/ "$@"

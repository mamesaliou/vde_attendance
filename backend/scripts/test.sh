#!/usr/bin/env bash

set -e
set -x

# Exécuter les tests avec les options souhaitées
python -m pytest tests/ \
    --cov=app \
    --cov-report=term \
    --cov-report=html \
    --cov-config=.coveragerc \
    --disable-warnings \
    -p no:warnings \
    -W ignore::DeprecationWarning:passlib.* \
    -W ignore::MovedIn20Warning:sqlalchemy.* \
    -W ignore::DeprecationWarning:crypt


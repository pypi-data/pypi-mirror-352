#!/usr/bin/env bash

python puppeteers/avanti/manage.py prep --noinput
python puppeteers/noi/manage.py prep --noinput

BASE_SITE=avanti npm test
BASE_SITE=noi npm test

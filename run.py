#!/usr/bin/env python
from os import environ

from app import app

app.run(host='0.0.0.0', port=80)

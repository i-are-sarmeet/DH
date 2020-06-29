#!/bin/bash

if [[ "$(python3 -m pip -V)" =~ "pip" ]]
then
  python3 -m pip install --user virtualenv
  python3 -m venv env
  source env/bin/activate
  python -m pip install -r requirements.txt
  python main.py
else
  echo "Python 3 and pip required"
fi
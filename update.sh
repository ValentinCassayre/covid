#!/bin/bash

git pull
/usr/local/bin/python3.7 fetch_data.py
/usr/local/bin/python3.7 covid2.py

#!/bin/bash

git pull
./env/bin/python3 fetch_data.py
./env/bin/python3 covid2.py

#!/bin/bash

git pull
python3.7 fetch_data.py
python3.7 covid.py

#!/bin/bash

# Set working directory
# shellcheck disable=SC2164
cd /Users/deepak.prakash/Documents/deepak/sankalp

# Activate virtual environment
source /Users/deepak.prakash/Documents/deepak/sankalp/venv/bin/activate

# Run the Python script with nohup and redirect output
nohup python scheduler.py > /Users/deepak.prakash/Documents/deepak/sankalp/logs/scheduler.log 2>&1 &
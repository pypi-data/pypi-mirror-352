#!/bin/bash

# Set working directory
# shellcheck disable=SC2164
cd /Users/deepak.prakash/Documents/deepak/sankalp_project

# Activate virtual environment


# Run the Python script with nohup and redirect output
nohup /Users/deepak.prakash/Documents/deepak/sankalp_project/venv/bin/python  -m sankalp.scheduler_manager.py > /Users/deepak.prakash/Documents/deepak/sankalp_project/sankalp/logs/scheduler.log 2>&1 &
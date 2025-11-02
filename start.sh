#!/bin/bash

# ==============================================================================
# CKB Bijar Spellchecker - Production Start Script for Toolforge
# ==============================================================================
# This script is the single entry point for starting the production server.
# It navigates to the application directory and then starts the Gunicorn server
# with production-ready settings.

# --- USAGE ---
# This script is executed by the Toolforge webservice command.
#
# Command to run from the project root (~/):
# webservice --image=python:3.13 bash start.sh
#
# To make this script executable (run once):
# chmod +x start.sh
# ------------------------------------------------------------------------------

# 1. Change to the directory where app.py and the .env file are located.
cd www/python/src

# 2. Execute the production server.
# This command assumes a .env file exists in this directory to provide configuration.
gunicorn app:app \
    --workers=4 \
    --bind=0.0.0.0 \
    --timeout=120 \
    --log-level=info \
    --access-logfile='-' \
    --error-logfile='-'
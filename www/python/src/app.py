# -*- coding: utf-8 -*-
"""
CKB Bijar Spellchecker Flask Application - Main Entry Point
This file initializes the Flask app, registers the API routes (Blueprints),
and loads the necessary data into memory before starting the server.
"""

import os
import psutil
from flask import Flask

# --- IMPORTS FROM OUR MODULES ---
from spellchecker import spellchecker_logic as logic
from spellchecker.database import get_db_connection
from spellchecker.routes import api_blueprint

# --- APPLICATION SETUP ---
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY") # Read from .env

# Conditionally enable CORS for development only
if os.getenv("FLASK_ENV") == "development":
    from flask_cors import CORS
    CORS(app)
    print("✅ CORS enabled for local development.")

# Register all the API endpoints from our routes file
app.register_blueprint(api_blueprint)

# --- STARTUP LOGIC ---
# This code now runs in both development and production modes.
# Load all data into the in-memory cache at startup for high performance.
with get_db_connection() as conn:
    logic.load_all_data_into_memory(conn)

# --- MEASURE AND PRINT MEMORY USAGE TO MONITER ---
process = psutil.Process(os.getpid())
memory_mb = process.memory_info().rss / (1024 * 1024)  # Convert bytes to megabytes
print(f"✅ Application ready. Memory usage: {memory_mb:.2f} MB")

# --- MAIN EXECUTION (FOR LOCAL DEVELOPMENT ONLY) ---
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)

# -*- coding: utf-8 -*-
"""
CKB Bijar Spellchecker Flask Application - Main Entry Point
This file initializes the Flask app, registers the API routes (Blueprints),
and loads the necessary data into memory before starting the server.
"""

import os
import json
import psutil
from flask import Flask
from flask_cors import CORS

# --- IMPORTS FROM OUR MODULES ---
from spellchecker import spellchecker_logic as logic
from spellchecker.database import get_db_connection
from spellchecker.routes import api_blueprint

# --- APPLICATION SETUP ---
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY") # Read from .env

# --- CORS CONFIGURATION ---
# Enable CORS for all API routes to allow cross-origin requests.
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Register all the API endpoints from our routes file
app.register_blueprint(api_blueprint)

# --- STARTUP LOGIC ---
# This code now runs in both development and production modes.
# Load all data into the in-memory cache at startup for high performance.
with get_db_connection() as conn:
    logic.load_all_data_into_memory(conn)

# --- Load the pre-calculated data using a robust, absolute path ---
# This ensures the file is found regardless of where the app is started from.
try:
    # Get the absolute path to the directory containing this app.py file
    app_root = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(app_root, 'static', 'data', 'word_counts.json')
    with open(json_path, "r", encoding="utf-8") as f:
        logic.linguistic_data['word_counts'] = json.load(f)
except FileNotFoundError:
    # Provide a clear, universal instruction for all users.
    print("WARNING: word_counts.json not found. Run 'python run.py generate_stats' (or 'python3' on Linux/Toolforge).")
    logic.linguistic_data['word_counts'] = {}

# --- MEASURE AND PRINT MEMORY USAGE TO MONITER ---
process = psutil.Process(os.getpid())
memory_mb = process.memory_info().rss / (1024 * 1024)  # Convert bytes to megabytes
print(f"✅ Application ready. Memory usage: {memory_mb:.2f} MB")

# --- MAIN EXECUTION (FOR LOCAL DEVELOPMENT ONLY) ---
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)

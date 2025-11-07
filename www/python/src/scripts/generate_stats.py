# -*- coding: utf-8 -*-
"""
CKB Bijar Spellchecker - Statistics Generation Script
This script pre-calculates word count statistics and saves them to a JSON file.
To run this script, use `python run.py generate_stats` from the project root.
"""

import json
import os

# This script is run by run.py, so 'src' is already in the path.
from spellchecker import spellchecker_logic as logic
from spellchecker.database import get_db_connection
from spellchecker.data_loader import calculate_and_cache_word_counts

print("Loading all linguistic data from the database...")
with get_db_connection() as conn:
    logic.load_all_data_into_memory(conn)

print("Starting the word count calculation. This may take a while...")
calculate_and_cache_word_counts(logic.linguistic_data)
print("Calculation complete.")

# --- Save the results using a robust, absolute path ---
# This ensures the file is saved in the correct location every time.
# Get the directory of the current script (src/scripts)
script_dir = os.path.dirname(os.path.abspath(__file__))
# Go up one level to get the 'src' directory
src_dir = os.path.dirname(script_dir)
# Define the final output path
output_path = os.path.join(src_dir, "static", "data", "word_counts.json")

# Create the directory if it doesn't exist
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(logic.linguistic_data['word_counts'], f, ensure_ascii=False)

print(f"Success! Saved pre-calculated stats to {output_path}")
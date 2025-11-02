import sys
import os
import runpy
import Levenshtein

# Add the 'src' directory to Python's path so it can find our packages
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'www', 'python', 'src'))

# --- Main Execution ---
if len(sys.argv) < 2:
    print("Error: Please specify which script to run. e.g., 'export_words'")
    sys.exit(1)

# Clean the requested script name from user input
script_name = sys.argv[1].replace('.py', '')
script_module = f"scripts.{script_name}"

try:
    # Pass the remaining arguments to the target script
    sys.argv = sys.argv[1:]
    runpy.run_module(script_module, run_name="__main__")

except ImportError:
    print(f"Error: No script named '{script_name}' found.")

    # --- "Did you mean" suggestion logic ---
    scripts_dir = os.path.join(os.path.dirname(__file__), 'www', 'python', 'src', 'scripts')
    
    # Find all valid .py scripts in the scripts directory
    available_scripts = [
        f.replace('.py', '') for f in os.listdir(scripts_dir)
        if f.endswith('.py') and not f.startswith('__')
    ]
    
    # Calculate the Levenshtein distance to find the closest match
    best_match = min(available_scripts, key=lambda s: Levenshtein.distance(script_name, s))
    
    # Only suggest if the typo is reasonably close (distance of 2 or less)
    if Levenshtein.distance(script_name, best_match) <= 2:
        print(f"Did you mean '{best_match}'?")
    
    sys.exit(1)
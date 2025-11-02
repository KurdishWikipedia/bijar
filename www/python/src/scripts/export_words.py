# -*- coding: utf-8 -*-
"""
CKB Bijar Spellchecker - Custom Dictionary Exporter

A command-line tool to generate and export word lists by calling the
generation logic from the data_loader module.

--- USAGE EXAMPLES ---
# Export ALL words to the default file (word_list.txt)
python export_words.py

# Export only stems and verbs to a custom file
python export_words.py --stems --verbs -o custom_verb_list.txt

# Export only derived words (stem + suffix combinations)
python export_words.py --derived

# See all available options
python export_words.py --help
"""

import argparse
from typing import Dict, Set, List

from spellchecker.data_loader import load_linguistic_data, generate_all_word_sets
from spellchecker.database import get_db_connection

def write_words_to_file(word_list: List[str], filename: str):
    """Sorts and writes a list of words to a UTF-8 encoded text file."""
    print(f"\nWriting {len(word_list):,} unique words to '{filename}'...")
    try:
        with open(filename, "w", encoding="utf-8") as f:
            for word in sorted(word_list):
                f.write(word + "\n")
        print("\n---")
        print("✅ Success!")
        print(f"The file '{filename}' has been created successfully.")
        print("---\n")
    except IOError as e:
        print(f"Error: Could not write to file. {e}")

def setup_arg_parser() -> argparse.ArgumentParser:
    """Sets up the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Custom word list exporter for the CKB Bijar Spellchecker.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('-s', '--stems', action='store_true', help="Export only base stems.")
    parser.add_argument('-d', '--derived', action='store_true', help="Export only derived words (stem + suffix combinations).")
    parser.add_argument('-v', '--verbs', action='store_true', help="Export all generated verb forms.")
    parser.add_argument('-p', '--particles', action='store_true', help="Export particles (prepositions, etc.).")
    parser.add_argument('-o', '--output', default='word_list.txt', help="Specify the output filename (default: word_list.txt).")
    return parser

def main():
    """Main execution function."""
    parser = setup_arg_parser()
    args = parser.parse_args()

    print("Initializing and connecting to the database...")
    with get_db_connection() as conn:
        linguistic_data = load_linguistic_data(conn)
    print("Linguistic data has been loaded into memory.")

    # Get all word sets from the single authoritative function.
    all_word_sets = generate_all_word_sets(linguistic_data)

    # Determine which categories to export. If none are specified, export all.
    export_all = not (args.stems or args.derived or args.verbs or args.particles)
    
    master_word_set: Set[str] = set()
    stats: Dict[str, int] = {}

    # --- Build the master list and stats based on user selection ---
    if args.stems or export_all:
        stats['Stems'] = len(all_word_sets['stems'])
        master_word_set.update(all_word_sets['stems'])
        
    if args.derived or export_all:
        stats['Derived Words (Stem+Suffix)'] = len(all_word_sets['derived'])
        master_word_set.update(all_word_sets['derived'])

    if args.verbs or export_all:
        stats['Verb Forms'] = len(all_word_sets['verbs'])
        master_word_set.update(all_word_sets['verbs'])
        
    if args.particles or export_all:
        stats['Particles'] = len(all_word_sets['particles'])
        master_word_set.update(all_word_sets['particles'])

    if not master_word_set:
        print("\nNo words were generated based on your selection. Nothing to export.")
        return

    # --- Print Statistics ---
    sum_of_categories = sum(stats.values())
    total_unique = len(master_word_set)
    overlap_count = sum_of_categories - total_unique

    print("\n--- Export Statistics ---")
    for category, count in stats.items():
        print(f"- {category:<28}: {count:>10,}")
    print("-------------------------")
    print(f"- {'Sum of Categories':<28}: {sum_of_categories:>10,}")
    
    # Only show the overlap information if there actually is an overlap
    if overlap_count > 0:
        print(f"- {'Overlaps (removed)':<28}: {-overlap_count:>10,}")
    
    print("-------------------------")
    print(f"- {'Total Unique Words':<28}: {total_unique:>10,}")
    print("-------------------------")

    write_words_to_file(list(master_word_set), args.output)


# --- MAIN EXECUTION ---
if __name__ == '__main__':
    main()

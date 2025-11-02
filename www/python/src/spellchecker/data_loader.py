# -*- coding: utf-8 -*-
"""
CKB Bijar Spellchecker - Data Loader & Generator
This module is responsible for connecting to the database, loading all
linguistic rules and performing on-demand generation of all
unique word sets for use by other parts of the application.
"""
from __future__ import annotations

from typing import Any, Dict, Set
from pymysql.connections import Connection
from pymysql.cursors import DictCursor
from .verb_engine import Verb

# --- Main Data Loading Function ---

def load_linguistic_data(db_conn: Connection[DictCursor]) -> Dict[str, Any]:
    """
    Connects to the DB and loads all raw linguistic rules.
    Word set generation is deferred to be run on-demand.
    """
    linguistic_data: Dict[str, Any] = {}
    cursor: DictCursor = db_conn.cursor()
    
    # --- 1. Load Raw Data from Database ---
    cursor.execute("SELECT prefix, id FROM verb_prefixes")
    all_prefixes_data = cursor.fetchall()
    cursor.execute("SELECT id, infinitive, past_stem, present_stem, is_transitive FROM verbs")
    verbs_from_db = cursor.fetchall()
    cursor.execute("SELECT verb_id, prefix_id FROM verb_prefix_link")
    prefix_links = cursor.fetchall()
    cursor.execute("SELECT word, sound_type, is_bad FROM stems")
    all_stems_data = cursor.fetchall()
    cursor.execute("SELECT suffix, applies_to_sound FROM suffixes")
    all_suffixes = cursor.fetchall()
    cursor.execute("SELECT word FROM particles")
    particles_set = {row['word'] for row in cursor.fetchall()}

    # --- 2. Process Data and Generate Verb Sets ---
    stems_map = {s['word']: s for s in all_stems_data}
    bad_words_set = {s['word'] for s in all_stems_data if s['is_bad']}
    
    prefix_id_map = {p['id']: p['prefix'] for p in all_prefixes_data}
    verb_id_map = {v['id']: v for v in verbs_from_db}
    valid_prefixes_map: Dict[str, Set[str]] = {}
    for link in prefix_links:
        verb = verb_id_map.get(link['verb_id'])
        prefix = prefix_id_map.get(link['prefix_id'])
        if verb and prefix:
            valid_prefixes_map.setdefault(verb['infinitive'], set()).add(prefix)

    verb_objects = [Verb(v['infinitive'], v['past_stem'], v['present_stem'], v['is_transitive'], valid_prefixes_map.get(v['infinitive'], set())) for v in verbs_from_db]
    all_generated_forms: Set[str] = {form for verb in verb_objects for form in verb.generate_all_conjugations()}

    # --- 3. Store the raw rules and base sets needed for on-demand generation
    linguistic_data['stems_map'] = stems_map
    linguistic_data['bad_words_set'] = bad_words_set
    linguistic_data['suffixes_list'] = all_suffixes
    linguistic_data['single_word_verb_forms'] = {f for f in all_generated_forms if " " not in f}
    linguistic_data['multi_word_verb_phrases'] = {f for f in all_generated_forms if " " in f}
    linguistic_data['verb_infinitives'] = {v['infinitive'] for v in verbs_from_db}
    linguistic_data['particles_set'] = particles_set
    linguistic_data['all_prefixes'] = {p['prefix'] for p in all_prefixes_data}
    
    # Empty cache for word_counts; filled on first API call
    linguistic_data['word_counts'] = None


    print("✅ Linguistic data loaded into memory.")
    cursor.close()
    return linguistic_data

# --- On-Demand Generation and Calculation Functions ---

def generate_all_word_sets(data: Dict[str, Any]) -> Dict[str, Set[str]]:
    """
    The single source of truth for generating all categories
    of unique word sets from the loaded linguistic rules.
    """
    print("Generating all unique word sets from rules...")
    
    # Stems
    stems_map = data.get('stems_map', {})
    stems_set = set(stems_map.keys())

    # Verbs
    verbs_set = data.get('single_word_verb_forms', set()).union(
        data.get('multi_word_verb_phrases', set())
    )
    
    # Particles
    particles_set = data.get('particles_set', set())
    
    # Derived Words (the expensive part)
    suffixes_list = data.get('suffixes_list', [])
    derived_words_set: Set[str] = set()
    # This loop is very fast as it's all in-memory.
    for stem_word, stem_info in stems_map.items():
        for suffix_info in suffixes_list:
            # Check if the stem's sound type is allowed by the suffix.
            if stem_info['sound_type'] in suffix_info.get('applies_to_sound', ''):
                # Apply the special rule.
                suffix = suffix_info.get('suffix', '')
                if not (stem_word.endswith('ە') and suffix.startswith(('ا', 'ە'))):
                    derived_words_set.add(stem_word + suffix)

    return {
        "stems": stems_set,
        "derived": derived_words_set,
        "verbs": verbs_set,
        "particles": particles_set
    }

def calculate_and_cache_word_counts(data: Dict[str, Any]):
    """
    Performs the one-time calculation for the API and caches it.
    It now uses the authoritative `generate_all_word_sets` function.
    """
    # 1. Get all the unique word sets.
    all_sets = generate_all_word_sets(data)

    # 2. Calculate the final, de-duplicated total.
    total_unique = len(all_sets['stems'].union(all_sets['derived'], all_sets['verbs'], all_sets['particles']))

    # 3. Store the final counts back into the main data dictionary.
    data['word_counts'] = {
        "stems": len(all_sets['stems']),
        "derived": len(all_sets['derived']),
        "verbs": len(all_sets['verbs']),
        "particles": len(all_sets['particles']),
        "total": total_unique
    }
    print("Word counts calculated and cached for future requests.")

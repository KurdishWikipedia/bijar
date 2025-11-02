# -*- coding: utf-8 -*-
"""
CKB Bijar Spellchecker - Main Orchestrator
This file initializes the application and orchestrates the core functions like
text checking and suggestion generation by delegating to the specialized engines.
"""
from __future__ import annotations

import re
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, NamedTuple
from pymysql.connections import Connection
from pymysql.cursors import DictCursor

# --- Import from our new, clean modules ---
from .data_loader import load_linguistic_data
from .suggestion_engine import SuggestionFinder

# --- DATA STRUCTURES ---
class ValidationResult(NamedTuple):
    is_correct: bool
    is_bad: bool = False

# Global cache to hold ALL data for high performance.
linguistic_data: Dict[str, Any] = {}

# --- INITIALIZATION ---
def load_all_data_into_memory(db_conn: Connection[DictCursor]):
    """Initializes the spellchecker by loading all data into the global cache."""
    global linguistic_data
    linguistic_data = load_linguistic_data(db_conn)

    linguistic_data['suggestion_cache'] = {}
    linguistic_data['suggestion_cache_created_at'] = datetime.now()

# --- CORE PUBLIC FUNCTIONS ---

def check_text_block(text_block: str) -> List[Dict[str, Any]]:
    """Analyzes a block of text and identifies problematic words."""
    problematic_words: List[Dict[str, Any]] = []
    words = list(re.finditer(r'\b[ئابپتجچحخدرڕزژسشعغفڤقکگلڵمنوۆھهەیێ]+\b', text_block))
    
    multi_word_phrases = linguistic_data.get('multi_word_verb_phrases', set())
    i = 0
    while i < len(words):
        match1 = words[i]
        word1 = match1.group(0)
        
        # Lookahead check for two-word verb phrases
        if i + 1 < len(words):
            match2 = words[i + 1]
            two_word_phrase = f"{word1} {match2.group(0)}"
            if two_word_phrase in multi_word_phrases:
                i += 2; continue

        if len(word1) <= 1:
            i += 1; continue

        validation = _is_word_correct_in_memory(word1)
        if not validation.is_correct:
            problematic_words.append({"word": word1, "start": match1.start(), "end": match1.end(), "type": "misspelled"})
        elif validation.is_bad:
            problematic_words.append({"word": word1, "start": match1.start(), "end": match1.end(), "type": "bad"})
        
        i += 1
        
    return problematic_words

def get_combined_suggestions(word: str, limit: int, max_distance: int) -> List[str]:
    """Generates suggestions for a single misspelled word, using caching for performance."""
    cache = linguistic_data.get('suggestion_cache', {})
    cache_key = f"{word}|{limit}|{max_distance}"

    if cache_key in cache:
        return cache[cache_key]

    start_time = time.perf_counter()
    finder = SuggestionFinder(word, limit, max_distance, linguistic_data)
    suggestions = finder.get_suggestions()
    end_time = time.perf_counter()
    duration_ms = (end_time - start_time) * 1000
    print(f"💡 Suggestion generation for '{word}' took {duration_ms:.2f} ms. (First time)")

    cache[cache_key] = suggestions
    
    # Delegate the cache management to a dedicated helper function.
    new_creation_time = _manage_suggestion_cache(cache, linguistic_data['suggestion_cache_created_at'])
    linguistic_data['suggestion_cache_created_at'] = new_creation_time

    return suggestions

# --- INTERNAL HELPER FUNCTIONS ---

def _manage_suggestion_cache(cache: Dict[str, List[str]], creation_time: datetime) -> datetime:
    """
    Checks the cache size and clears it if it exceeds the limit, logging details.
    Returns the new creation timestamp for the cache.
    """
    CACHE_LIMIT = 10000 # Your real limit would be 10000
    if len(cache) <= CACHE_LIMIT:
        return creation_time

    deletion_time = datetime.now()
    lifetime = deletion_time - creation_time
    
    creation_str = creation_time.strftime('%Y-%m-%d %H:%M:%S')
    deletion_str = deletion_time.strftime('%Y-%m-%d %H:%M:%S')

    cache_size_bytes = sys.getsizeof(cache) + sum(sys.getsizeof(k) + sys.getsizeof(v) for k, v in cache.items())
    
    # --- Smart Unit Display ---
    # Display in KB if the size is less than a megabyte, otherwise display in MB.
    if cache_size_bytes < (1024 * 1024):
        size_str = f"{cache_size_bytes / 1024:.2f} KB"
    else:
        size_str = f"{cache_size_bytes / (1024 * 1024):.2f} MB"
    
    print(f"ℹ️ Suggestion cache cleared. Freed approx. {size_str}. "
          f"Lifetime: {str(lifetime).split('.')[0]}. "
          f"(Created: {creation_str}, Deleted: {deletion_str})")
    
    cache.clear()
    return datetime.now()

def _is_word_correct_in_memory(word_to_check: str) -> ValidationResult:
    """Checks a single word against the cached linguistic rules."""
    if word_to_check in linguistic_data.get('particles_set', set()):
        return ValidationResult(is_correct=True)
    if word_to_check in linguistic_data.get('single_word_verb_forms', set()):
        return ValidationResult(is_correct=True)

    stems_map = linguistic_data.get('stems_map', {})
    if word_to_check in stems_map:
        return ValidationResult(is_correct=True, is_bad=word_to_check in linguistic_data.get('bad_words_set', set()))

    for suffix_info in linguistic_data.get('suffixes_list', []):
        suffix = suffix_info['suffix']
        if word_to_check.endswith(suffix):
            stem_part = word_to_check[:-len(suffix)]
            
            if stem_part in stems_map:
                if stems_map[stem_part]['sound_type'] in suffix_info['applies_to_sound']:
                    if stem_part.endswith('ە') and suffix.startswith(('ا', 'ە')): continue
                    return ValidationResult(is_correct=True, is_bad=stem_part in linguistic_data.get('bad_words_set', set()))
            
            if suffix.startswith(('ا', 'ە')):
                original_stem_guess = stem_part + 'ە'
                if original_stem_guess in stems_map:
                    return ValidationResult(is_correct=True, is_bad=original_stem_guess in linguistic_data.get('bad_words_set', set()))

    return ValidationResult(is_correct=False)

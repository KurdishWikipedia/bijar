# -*- coding: utf-8 -*-
"""
CKB Bijar Spellchecker - Suggestion Engine
This module is the "Detective" of the spellchecker. It contains the
SuggestionFinder class responsible for intelligently finding corrections.
"""

from typing import Any, Dict, List, Set, Tuple
import Levenshtein
from .constants import GROUP_1_PRONOUNS

class SuggestionFinder:
    """A self-contained engine to find suggestions for a single misspelled word."""
    def __init__(self, word: str, limit: int, max_distance: int, data: Dict[str, Any]):
        self.word = word
        self.limit = limit
        self.max_distance = max_distance
        self.candidates: Dict[str, float] = {}
        
        # --- Data setup ---
        self.stems_map: Dict[str, Any] = data.get('stems_map', {})
        self.stems_by_len: Dict[int, Set[str]] = {}
        for stem in self.stems_map:
            self.stems_by_len.setdefault(len(stem), set()).add(stem)

        self.multi_word_phrases: Set[str] = data.get('multi_word_verb_phrases', set())
        self.single_word_verb_forms: Set[str] = data.get('single_word_verb_forms', set())
        self.all_prefixes: Set[str] = data.get('all_prefixes', set())
        self.master_dictionary: Set[str] = {
            *self.stems_map.keys(),
            *data.get('verb_infinitives', set()),
            *self.single_word_verb_forms,
            *data.get('particles_set', set())
        }
        self.sorted_suffixes: List[Dict[str, Any]] = sorted(
            data.get('suffixes_list', []),
            key=lambda s: len(s.get('suffix', '')), 
            reverse=True
        )

    def get_suggestions(self) -> List[str]:
        """Main method to run the entire suggestion process."""
        self._find_simple_word_suggestions()
        self._find_stem_suffix_suggestions()
        self._find_structural_verb_suggestions()
        return self._rank_suggestions()

    def _add_candidate(self, candidate: str, distance: int, bonus: float = 1.0):
        """Calculates a smart score and adds the candidate."""
        score = Levenshtein.jaro_winkler(self.word, candidate)
        score *= (1.1 - (distance / (len(self.word) + 1)))
        if len(candidate) > len(self.word):
            score *= 0.9
        score *= bonus
        self.candidates[candidate] = max(self.candidates.get(candidate, 0.0), score)

    def _find_simple_word_suggestions(self):
        """Hypothesis A: The word is a simple misspelling of a base word."""
        for candidate in self.master_dictionary:
            if abs(len(self.word) - len(candidate)) > self.max_distance:
                continue
            dist = Levenshtein.distance(self.word, candidate)
            if dist <= self.max_distance:
                self._add_candidate(candidate, dist)

    def _find_stem_suffix_suggestions(self):
        """Hypothesis B: A definitive, high-speed, suffix-first search."""
        processed_pairs: Set[Tuple[str, str]] = set()
        min_stem_len = 2

        for i in range(min_stem_len, len(self.word)):
            hypothetical_stem = self.word[:i]
            hypothetical_suffix = self.word[i:]

            # The core optimization: loop through the small suffix list FIRST.
            for suffix_info in self.sorted_suffixes:
                real_suffix = suffix_info.get('suffix', '')
                if not real_suffix: continue

                # If the suffix is too different from the word's ending, skip entirely.
                suffix_dist = Levenshtein.distance(hypothetical_suffix, real_suffix)
                if suffix_dist > self.max_distance:
                    continue

                remaining_dist = self.max_distance - suffix_dist

                # --- Strategy 1: The General Search ---
                # Now that we have a plausible suffix, find a close stem.
                len_range = range(len(hypothetical_stem) - remaining_dist, len(hypothetical_stem) + remaining_dist + 1)
                for length in len_range:
                    for real_stem in self.stems_by_len.get(length, set()):
                        if (real_stem, real_suffix) in processed_pairs: continue
                        
                        if Levenshtein.distance(hypothetical_stem, real_stem) <= remaining_dist:
                            if self.stems_map[real_stem]['sound_type'] in suffix_info.get('applies_to_sound', ''):
                                reconstructed = (real_stem[:-1] if real_stem.endswith('ە') and real_suffix.startswith(('ا', 'ە')) else real_stem) + real_suffix
                                final_dist = Levenshtein.distance(self.word, reconstructed)
                                if final_dist <= self.max_distance:
                                    self._add_candidate(reconstructed, final_dist)
                                processed_pairs.add((real_stem, real_suffix))
                
                # --- Strategy 2: The "Tomato Fix" (fast and targeted) ---
                if real_suffix.startswith(('ا', 'ە')):
                    potential_e_stem = hypothetical_stem + 'ە'
                    if (potential_e_stem, real_suffix) in processed_pairs: continue
                    
                    if potential_e_stem in self.stems_map:
                        reconstructed = hypothetical_stem + real_suffix
                        final_dist = Levenshtein.distance(self.word, reconstructed)
                        if final_dist <= self.max_distance:
                            self._add_candidate(reconstructed, final_dist)
                        processed_pairs.add((potential_e_stem, real_suffix))
                                    
    def _find_structural_verb_suggestions(self):
        """Hypothesis C: The word is a compressed compound verb or needs a rule-based fix."""
        if self.word.startswith('ئە'):
            fix = self.word.replace('ئە', 'دە', 1)
            if fix in self.single_word_verb_forms:
                self.candidates[fix] = max(self.candidates.get(fix, 0.0), 1.01)

        for prefix in self.all_prefixes:
            for g1p in GROUP_1_PRONOUNS:
                base, ish_base = prefix + g1p, prefix + "یش" + g1p
                e_base, ish_e_base = base + 'ئە', ish_base + 'ئە'

                # Pattern 1: e.g., "ھەڵمگرت" -> "ھەڵم گرت"
                if self.word.startswith(base) and len(self.word) > len(base):
                    fix = f"{base} {self.word[len(base):]}"
                    if fix in self.multi_word_phrases:
                        self.candidates[fix] = max(self.candidates.get(fix, 0.0), 1.02)
                
                # Pattern 2: e.g., "ھەڵیشمگرت" -> "ھەڵیشم گرت"
                if self.word.startswith(ish_base) and len(self.word) > len(ish_base):
                    fix = f"{ish_base} {self.word[len(ish_base):]}"
                    if fix in self.multi_word_phrases:
                        self.candidates[fix] = max(self.candidates.get(fix, 0.0), 1.02)
                
                # Pattern 3: e.g., "ھەڵمدەگرت" -> "ھەڵم دەگرت"
                if self.word.startswith(e_base) and len(self.word) > len(e_base):
                    fix = f"{base} دە{self.word[len(e_base):]}"
                    if fix in self.multi_word_phrases:
                        self.candidates[fix] = max(self.candidates.get(fix, 0.0), 1.03)
                
                # Pattern 4: e.g., "ھەڵیشمدەگرت" -> "ھەڵیشم دەگرت"
                if self.word.startswith(ish_e_base) and len(self.word) > len(ish_e_base):
                    fix = f"{ish_base} دە{self.word[len(ish_e_base):]}"
                    if fix in self.multi_word_phrases:
                        self.candidates[fix] = max(self.candidates.get(fix, 0.0), 1.03)

    def _rank_suggestions(self) -> List[str]:
        """Ranks candidates by score and returns the top N results."""
        if not self.candidates:
            return []
        
        sorted_suggestions = sorted(self.candidates.items(), key=lambda item: item[1], reverse=True)
        return [item[0] for item in sorted_suggestions[:self.limit]]

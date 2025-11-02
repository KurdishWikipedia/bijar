# -*- coding: utf-8 -*-
"""
CKB Bijar Spellchecker - Verb Conjugation Engine
This file contains the Verb class, which is the core engine for generating
all valid verb forms based on linguistic rules.
"""

from typing import List, Set
from .constants import GROUP_1_PRONOUNS, GROUP_2_PRONOUNS, GROUP_3_PRONOUNS

# Defines grammatically impossible pronoun pairings (e.g., 'me' with 'we').
# Storing pairs symmetrically `(A, B)` and `(B, A)` allows a single, simple
# check to work correctly for both present (object, subject) and past (subject, object) tenses.
INVALID_PRONOUN_PAIRS = {
    # Base Invalid Pairs
    ('م', 'ین'), ('م', 'م'), ('تان', 'یت'), ('مان', 'ین'), ('مان', 'م'), ('ت', 'یت'),
    # Symmetrical Pairs
    ('ین', 'م'), ('یت', 'تان'), ('ین', 'مان'), ('م', 'مان'), ('یت', 'ت')
}

class Verb:
    """Represents a verb and its rules for generating all correct forms."""
    def __init__(self, infinitive: str, past_stem: str, present_stem: str, is_transitive: int, valid_prefixes: Set[str]):
        self.infinitive = infinitive
        self.past_stem = past_stem
        self.present_stem = present_stem
        self.is_transitive = bool(is_transitive)
        self.valid_prefixes = valid_prefixes

    def generate_all_conjugations(self) -> Set[str]:
        """The definitive engine for creating every possible correct verb form."""
        # --- Phase 1: Generate all PREFIX-LESS forms and BASE forms for prefixing ---

        # Add the infinitive itself (e.g., "گرتن")
        all_forms: Set[str] = {self.infinitive}
        
        # This set will collect all single-word forms that a prefix COULD be attached to.
        base_prefixable_forms: Set[str] = {self.past_stem}
        
        # Generate present tense forms (e.g., "دەگرم")
        present_stems_inflected = {'دە' + f for f in self._generate_present_forms()}
        all_forms.update(present_stems_inflected)

        # Generate past tense forms with pronouns (e.g., "گرتم")
        past_pronouns = GROUP_1_PRONOUNS if self.is_transitive else GROUP_2_PRONOUNS
        all_forms.update(self.past_stem + p for p in past_pronouns)

        # Generate past far forms (e.g., "گرتبوو", "گرتبووم")
        past_far_base = self.past_stem + 'بوو'
        base_prefixable_forms.add(past_far_base)
        all_forms.update(past_far_base + p for p in past_pronouns)

        # Generate perfect tense forms (e.g., "گرتوویە", "گرتوومە")
        perfect_base_stem = self.past_stem + ('وو' if self.past_stem.endswith(('د', 'ت')) else 'و')
        perfect_base_form = perfect_base_stem + 'ە'
        base_prefixable_forms.add(perfect_base_form)
        all_forms.update(perfect_base_stem + p + 'ە' for p in past_pronouns)

        # For transitive verbs, generate past continuous single-word forms (e.g., "دەگرت", "دەمگرت")
        if self.is_transitive:
            base_prefixable_forms.add('دە' + self.past_stem)
            all_forms.update('دە' + p + self.past_stem for p in GROUP_1_PRONOUNS)

        # Add all generated base forms (like "گرت", "دەگرت", "گرتبوو", "گرتووە") to the final list.
        # This ensures they exist even for verbs without prefixes.
        all_forms.update(base_prefixable_forms)

        # --- Phase 2: Generate all PREFIXED forms in a single, efficient loop ---

        for prefix in self.valid_prefixes:
            # Case A: Single-word prefixed forms (e.g., "ھەڵگرت", "ھەڵدەگرت")
            all_forms.update(prefix + f for f in base_prefixable_forms)

            # Case B: Prefixed infinitives (e.g., "ھەڵگرتن", "ڕێککەوتن")
            all_forms.add(prefix + self.infinitive)

            # Case C: Multi-word phrases for transitive verbs
            if self.is_transitive:
                for g1p in GROUP_1_PRONOUNS:
                    # Create the two prefix styles (with/without 'یش') ONCE.
                    prefix_variations = [f"{prefix}{g1p}", f"{prefix}یش{g1p}"]

                    # Now, loop through those two styles and apply all tense rules cleanly.
                    for prefix_variation in prefix_variations:
                        # Past Tenses: Here `g1p` is the SUBJECT.
                        all_forms.add(f"{prefix_variation} {self.past_stem}")       # e.g., "ھەڵم گرت"
                        all_forms.add(f"{prefix_variation} {perfect_base_form}")    # e.g., "ھەڵم گرتووە"
                        all_forms.add(f"{prefix_variation} {past_far_base}")        # e.g., "ھەڵم گرتبوو"

                        # Present Tense: Here, `g1p` is the OBJECT.
                        for present_form in present_stems_inflected:
                            # Isolate the subject pronoun ending (e.g., 'دەگرم' -> 'م').
                            subject_pronoun = present_form.replace('دە' + self.present_stem, '', 1)
                            
                            if (g1p, subject_pronoun) not in INVALID_PRONOUN_PAIRS:
                                all_forms.add(f"{prefix_variation} {present_form}")     # e.g., "ھەڵم دەگرێت"
                            # else:
                            #     if prefix + self.infinitive == 'ھەڵگرتن':
                            #         print(f"🚫 Excluded Present: {prefix_variation} {present_form}")

                        # Complex Past Tenses: Here, `g1p` is the SUBJECT and `g2p` is the OBJECT.
                        for g2p in GROUP_2_PRONOUNS:
                            if (g1p, g2p) not in INVALID_PRONOUN_PAIRS:
                                # Simple Past with Subject Pronoun
                                all_forms.add(f"{prefix_variation} {self.past_stem}{g2p}") # e.g., "ھەڵم گرتیت"
                                # Past Continuous with Subject Pronoun
                                all_forms.add(f"{prefix_variation} دە{self.past_stem}{g2p}") # e.g., "ھەڵم دەگرتیت"
                                # Past Far with Subject Pronoun
                                all_forms.add(f"{prefix_variation} {past_far_base}{g2p}") # e.g., "ھەڵم گرتبوویت"
                            # else:
                            #     if prefix + self.infinitive == 'ھەڵگرتن':
                            #         print(f"🚫 Excluded Past: {prefix_variation} {self.past_stem}{g2p}")
                            #         print(f"🚫 Excluded Past: {prefix_variation} دە{self.past_stem}{g2p}")
                            #         print(f"🚫 Excluded Past: {prefix_variation} {past_far_base}{g2p}")

        return all_forms
    
    def _generate_present_forms(self) -> List[str]:
        """Helper to generate present tense stems based on vowel harmony."""
        stem = self.present_stem
        # Use the full set of pronouns for present tense
        forms: List[str] = [stem + p for p in GROUP_3_PRONOUNS if p not in ('ات', 'ێت')]
        if stem.endswith('ە'): forms.append(stem[:-1] + 'ات')
        elif stem.endswith('ۆ'): forms.append(stem[:-1] + 'وات')
        elif stem.endswith('ێ'): forms.append(stem[:-1] + 'ێت')
        else: forms.append(stem + 'ێت')
        return forms
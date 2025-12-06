# -*- coding: utf-8 -*-
"""
CKB Bijar Spellchecker - Verb Conjugation Engine
This file contains the Verb class, which is the core engine for generating
all valid verb forms based on linguistic rules.
"""

from typing import List, Set, Tuple
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
        
        # Get raw present forms and their pronouns.
        # e.g., self.raw_present_forms_with_pronouns = [('گرم', 'م'), ('گرێت', 'ێت')]
        self.raw_present_forms_with_pronouns = self._generate_base_present_forms()

        # Generate present tense forms (e.g., "دەگرم")
        present_stems_inflected = {'دە' + form for form, _ in self.raw_present_forms_with_pronouns}
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

        # Generate past continuous single-word form (e.g., "دەگرت")
        base_prefixable_forms.add('دە' + self.past_stem)

        # Generate past continuous single-word forms with pronouns.
        # DO NOT use past_pronouns here, as transitive and intransitive differ.
        if self.is_transitive:
            all_forms.update('دە' + p + self.past_stem for p in GROUP_1_PRONOUNS)   # e.g., "دەمگرت"
        else:
            all_forms.update('دە' + self.past_stem + p for p in GROUP_2_PRONOUNS)   # e.g., "دەخەوتم"

        # --- IMPERATIVE MOOD GENERATION (e.g., "بگرە", "بمگرن") ---
        base_imperatives: Set[str] = set()
        object_imperatives: Set[str] = set()

        # Special Case: "ھاتن" (to come)
        if self.infinitive == 'ھاتن':
            all_forms.update({'وەرە', 'وەرن'})

        # Determine 2nd Person Singular Subject (Vowel Harmony)
        p2_singular = '' if self.present_stem.endswith(('ە', 'ۆ', 'ێ', 'وو', 'ی')) else 'ە'

        # Generate Standard Imperatives
        # Structure: "ب" + stem + subject
        if self.infinitive == 'چوون':
            base_imperatives.add('بچۆ') # Irregular Singular
            base_imperatives.add('بچن') # Irregular Plural
        else:
            base_imperatives.add('ب' + self.present_stem + p2_singular) # Singular (e.g., بگرە, بخۆ)
            base_imperatives.add('ب' + self.present_stem + 'ن')         # Plural   (e.g., بگرن, بخۆن)

        # Generate Transitive Imperatives with Object Pronouns
        # Structure: "ب" + object + stem + subject
        if self.is_transitive:
            # Plural Subject ('ن') accepts ALL objects.
            # Singular Subject ('p2_singular') accepts ONLY non-2nd person objects (excludes 'ت', 'تان').
            
            for obj in GROUP_1_PRONOUNS:
                prefix_base = 'ب' + obj + self.present_stem
                
                # Plural Subject (Always Valid) -> e.g., بتگرن, بمگرن
                object_imperatives.add(prefix_base + 'ن')

                # Singular Subject (Restricted) -> e.g., بمگرە (Valid), بتگرە & بتانگرە (Invalid)
                if obj not in {'ت', 'تان'}:
                    object_imperatives.add(prefix_base + p2_singular)

        base_prefixable_forms.update(base_imperatives)
        all_forms.update(object_imperatives)

        # --- SUBJUNCTIVE MOOD GENERATION (e.g., "بخۆم", "بخوات", "بمخوات") ---
        base_subjunctives: Set[str] = set()
        object_subjunctives: Set[str] = set()

        for form, subject_pronoun in self.raw_present_forms_with_pronouns:
            # Simple Subjunctive (e.g., "بخۆم", "بخوات")
            base_subjunctives.add('ب' + form)

            # Transitive with Objects (e.g., "بمخوات")
            if self.is_transitive:
                for obj in GROUP_1_PRONOUNS:
                    # Filter impossible pairs (e.g., "بمخۆم" -> I eat me).
                    if (obj, subject_pronoun) not in INVALID_PRONOUN_PAIRS:
                        object_subjunctives.add('ب' + obj + form)

        base_prefixable_forms.update(base_subjunctives)
        all_forms.update(object_subjunctives)
        
        # Add all generated base forms to the final list.
        all_forms.update(base_prefixable_forms)

        # --- Phase 2: Generate all PREFIXED forms in a single, efficient loop ---

        for prefix in self.valid_prefixes:
            # Case A: Single-word prefixed forms (e.g., "ھەڵگرت")
            all_forms.update(prefix + f for f in base_prefixable_forms)

            # Case B: Prefixed infinitives (e.g., "ھەڵگرتن")
            all_forms.add(prefix + self.infinitive)

            # Case C: Multi-word phrases for transitive verbs
            if self.is_transitive:
                for g1p in GROUP_1_PRONOUNS:
                    # Create the two prefix styles (with/without 'یش') ONCE.
                    prefix_variations = [f"{prefix}{g1p}", f"{prefix}یش{g1p}"]

                    # Iterate through all base forms to create full phrases.
                    for prefix_variation in prefix_variations:

                        # Past Tenses: `g1p` is the SUBJECT.
                        all_forms.add(f"{prefix_variation} {self.past_stem}")       # e.g., "ھەڵم گرت"
                        all_forms.add(f"{prefix_variation} {perfect_base_form}")    # e.g., "ھەڵم گرتووە"
                        all_forms.add(f"{prefix_variation} {past_far_base}")        # e.g., "ھەڵم گرتبوو"

                        # Imperative Tense: `g1p` is the OBJECT.
                        # This logic is unique and remains separate.
                        for imperative_form in base_imperatives:
                            subject_pronoun = 'ن' if imperative_form.endswith('ن') else 'یت'
                            if (g1p, subject_pronoun) not in INVALID_PRONOUN_PAIRS:
                                all_forms.add(f"{prefix_variation} {imperative_form}") # e.g., "ھەڵی بگرە"

                        # Present & Subjunctive Tenses: `g1p` is the OBJECT.
                        # The logic is identical for both, so we merge them into a single loop.
                        for tense_marker in ('دە', 'ب'): # Grammatical markers for Present ('دە') and Subjunctive ('ب')
                            for form, subject_pronoun in self.raw_present_forms_with_pronouns:
                                if (g1p, subject_pronoun) not in INVALID_PRONOUN_PAIRS:
                                    # e.g., 'دە' + 'گرێت' -> 'دەگرێت'
                                    verb_form = tense_marker + form
                                    # e.g., "ھەڵم" + " " + "دەگرێت" -> "ھەڵم دەگرێت"
                                    all_forms.add(f"{prefix_variation} {verb_form}")

                        # Complex Past Tenses: `g1p` is the SUBJECT and `g2p` is the OBJECT.
                        for g2p in GROUP_2_PRONOUNS:
                            if (g1p, g2p) not in INVALID_PRONOUN_PAIRS:
                                # Simple Past with Subject Pronoun
                                all_forms.add(f"{prefix_variation} {self.past_stem}{g2p}") # e.g., "ھەڵم گرتیت"
                                # Past Continuous with Subject Pronoun
                                all_forms.add(f"{prefix_variation} دە{self.past_stem}{g2p}") # e.g., "ھەڵم دەگرتیت"
                                # Past Far with Subject Pronoun
                                all_forms.add(f"{prefix_variation} {past_far_base}{g2p}") # e.g., "ھەڵم گرتبوویت"

        return all_forms
    
    def _generate_base_present_forms(self) -> List[Tuple[str, str]]:
        """
        Helper to generate present tense stems and the pronoun used for each.
        Returns a list of (form, pronoun) tuples, e.g., [('خۆم', 'م'), ('خوات', 'ات')].
        """
        stem = self.present_stem
        forms: List[Tuple[str, str]] = []
        
        # Generate for all standard pronouns except 3rd person singular
        for p in GROUP_3_PRONOUNS:
            if p not in ('ات', 'ێت'):
                forms.append((stem + p, p))

        # Handle 3rd Person Singular separately due to vowel harmony rules
        third_person_pronoun = 'ێت'  # Default pronoun
        modified_stem = stem         # Default stem
        
        if stem.endswith('ە'):
            third_person_pronoun = 'ات'
            modified_stem = stem[:-1]
        elif stem.endswith('ۆ'):
            third_person_pronoun = 'ات'
            modified_stem = stem[:-1] + 'و' # e.g., 'خۆ' -> 'خو'
        elif stem.endswith('ێ'):
            modified_stem = stem[:-1]
        
        forms.append((modified_stem + third_person_pronoun, third_person_pronoun))

        return forms
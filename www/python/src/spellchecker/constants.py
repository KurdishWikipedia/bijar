# -*- coding: utf-8 -*-
"""
CKB Bijar Spellchecker - Linguistic Constants
This file contains static, language-specific data sets like pronoun groups.
Centralizing them here makes the main logic cleaner and easier to manage.
"""

from typing import Set

GROUP_1_PRONOUNS: Set[str] = {'م', 'مان', 'ت', 'تان', 'ی', 'یان'}
GROUP_2_PRONOUNS: Set[str] = {'م', 'ین', 'یت', 'ن', ''}
GROUP_3_PRONOUNS: Set[str] = {'م', 'ین', 'یت', 'ن', 'ات', 'ێت'}

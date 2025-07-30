Hebrew diacritics normalization
- Introduced normalize_hebrew_diacritics() in hebrew/diacritics.py to correct niqqud and dagesh/sin-dot ordering.

This ensures that diacritics appear in a consistent canonical order:
dagesh > shin/sin dots > vowel marks.
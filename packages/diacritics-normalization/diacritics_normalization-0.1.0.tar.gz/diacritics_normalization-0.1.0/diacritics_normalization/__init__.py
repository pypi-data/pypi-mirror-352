import re

# Define the replacements directly as a dictionary
diacritics_replacements = {
    "ִּׁ": "ִּׁ",
    "ָּׁ": "ָּׁ",
    "ְּׁ": "ְּׁ",
    "ֵּׁ": "ֵּׁ",
    "ַּׁ": "ַּׁ",
    "ׇּׁ": "ׇּׁ",
    "ֻּׁ": "ֻּׁ",
    "ֹּׁ": "ֹּׁ",
    "ֶּׁ": "ֶּׁ",

    "ִּׁ": "ִּׁ",
    "ָּׁ": "ָּׁ",
    "ְּׁ": "ְּׁ",
    "ֵּׁ": "ֵּׁ",
    "ַּׁ": "ַּׁ",
    "ׇּׁ": "ׇּׁ",
    "ֻּׁ": "ֻּׁ",
    "ֹּׁ": "ֹּׁ",
    "ֶּׁ": "ֶּׁ",

    "ִּׂ": "ִּׂ",
    "ָּׂ": "ָּׂ",
    "ְּׂ": "ְּׂ",
    "ֵּׂ": "ֵּׂ",
    "ַּׂ": "ַּׂ",
    "ׇּׂ": "ׇּׂ",
    "ֻּׂ": "ֻּׂ",
    "ֹּׂ": "ֹּׂ",
    "ֶּׂ": "ֶּׂ",

    "ִּׂ": "ִּׂ",
    "ָּׂ": "ָּׂ",
    "ְּׂ": "ְּׂ",
    "ֵּׂ": "ֵּׂ",
    "ַּׂ": "ַּׂ",
    "ׇּׂ": "ׇּׂ",
    "ֻּׂ": "ֻּׂ",
    "ֹּׂ": "ֹּׂ",
    "ֶּׂ": "ֶּׂ",

    "ִּ": "ִּ",
    "ָּ": "ָּ",
    "ְּ": "ְּ",
    "ֵּ": "ֵּ",
    "ַּ": "ַּ",
    "ׇּ": "ׇּ",
    "ֻּ": "ֻּ",
    "ֹּ": "ֹּ",
    "ֶּ": "ֶּ",

    "ִׁ": "ִׁ",
    "ָׁ": "ָׁ",
    "ְׁ": "ְׁ",
    "ֵׁ": "ֵׁ",
    "ַׁ": "ַׁ",
    "ׇׁ": "ׇׁ",
    "ֻׁ": "ֻׁ",
    "ֹׁ": "ֹׁ",
    "ֶׁ": "ֶׁ",

    "ִׂ": "ִׂ",
    "ָׂ": "ָׂ",
    "ְׂ": "ְׂ",
    "ֵׂ": "ֵׂ",
    "ַׂ": "ַׂ",
    "ׇׂ": "ׇׂ",
    "ֻׂ": "ֻׂ",
    "ֹׂ": "ֹׂ",
    "ֶׂ": "ֶׂ",

    "ּׁ": "ּׁ",
    "ּׂ": "ּׂ",

    "\"": "",
    "\"\"": "",
}

# Build a regular expression that matches any key in your dictionary:
pattern = re.compile("|".join(map(re.escape, diacritics_replacements.keys())))

def normalize_hebrew_diacritics(input_text):
    """
    Preprocess text using a dictionary of replacements.

    Args:
        input_text (str): The original text to preprocess.

    Returns:
        str: Preprocessed text with replacements applied.
    """

    # 're.sub' will call this function for each match
    def _replace_callback(match):
        return diacritics_replacements[match.group(0)]

    return pattern.sub(_replace_callback, input_text)

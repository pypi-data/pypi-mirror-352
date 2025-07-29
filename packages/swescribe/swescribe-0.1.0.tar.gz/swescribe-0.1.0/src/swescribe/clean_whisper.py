import re

# Defining RegEx patterns for cleaning
simple_url_pattern = re.compile(r"\S+www\.\S+")
punkt_X_pattern = re.compile(r"\S+\.(nu|se|com|org)\S*")
elipsis_pattern = re.compile(r"\.\.\.*")
spaces_pattern = re.compile(r"  *")
for_pattern = re.compile(r"\bFör\.")
ja_repeat_pattern = re.compile(r"(\b[Jj]a, ?\b[Jj]a, ?)([Jj]a, ?)+")
dash_pattern = re.compile(
    r"^[\u2010\u2011\u2012\u2013\u2014\u2015\u2212\-–—―‒‑⁃]+"
)

LINE_ARTEFACTS = {
    "den.",
    "jag har en.",
    "men.",
    "musik musik musik",
    "musik musik",
    "musik.",
    "musik",
    "stina hedin iyuno media group",
    "textat av karin schill.",
}


def clean_urls(text: str) -> str:
    """Remove URLs from transcription."""

    if bool(punkt_X_pattern.search(text)) or bool(
        simple_url_pattern.search(text)
    ):
        return ""

    return text.strip()


def clean_elipsis(text: str) -> str:
    """Replace elipsis with a space."""

    return elipsis_pattern.sub(" ", text).strip()


def clean_spaces(text: str) -> str:
    """Remove multiple spaces from transcription."""
    return spaces_pattern.sub(" ", text).strip()


def clean_for(text: str) -> str:
    """Remove multiple "För." from transcription."""
    return for_pattern.sub(" ", text).strip()


def clean_ja_repeat(text: str) -> str:
    """Reduce multiple "Ja, ja, ja..." to "Ja, ja," """
    result = text[:]

    while len(items := list(ja_repeat_pattern.finditer(result))):
        item = items[0]
        start, end = item.span()
        keep, _ = item.groups()

        result = result[:start] + keep + result[end:]

    return result.strip()


def clean_dashes(text):
    """Remove dashes from string"""
    return dash_pattern.sub("", text).strip()


def line_artefact_check(text: str) -> bool:
    """Check if the entire line is an artefact that should be skipped.

    Args:
        text (str): The text segment to check.

    Returns:
        bool: True if it's an artifact line, False otherwise.
    """
    stripped_text = text.strip().lower()
    return stripped_text in LINE_ARTEFACTS


def clean_line_artefact(text: str) -> str:
    """Check for line artefacts and remove them."""
    if line_artefact_check(text):
        return ""
    else:
        return text


def clean_text(text):
    result = text[:].strip()
    for function in (
        clean_elipsis,
        clean_dashes,
        clean_for,
        clean_line_artefact,
        clean_ja_repeat,
        clean_urls,
        clean_spaces,
    ):
        if result == "":
            break
        result = function(result)
    return result

"""Supporting functions for language processing."""


def map_language(language: str) -> str:
    """
    Map the language name to its OpenAI API code.

    Parameters
    ----------
    language : str
        The language name.

    Returns
    -------
    str
        The OpenAI API code for the language.
    """
    mapper = {
        "english": "en",
        "slovak": "sk",
        "czech": "cs",
    }
    return mapper[language.lower()]

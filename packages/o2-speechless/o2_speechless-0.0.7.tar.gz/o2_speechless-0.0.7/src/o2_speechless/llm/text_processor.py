"""TextProcessor class to compare two transcriptions"""

import re
import unicodedata
import difflib
import logging
from typing import List, Tuple, Optional, Dict
from thefuzz import fuzz, process

from o2_speechless.util.logger import configure_logging

# Configure logging
configure_logging()
logger = logging.getLogger(__name__)


# ANSI escape sequences for coloring
RED = "\u001b[31m"
GREEN = "\u001b[32m"
RESET = "\u001b[0m"


class TextProcessor:
    """
    A utility class for text normalization, cleaning, and fuzzy matching.
    """

    def __init__(
        self,
        strip_accents: bool = True,
    ) -> None:
        """
        Initialize a TextProcessor.

        Parameters
        ----------
        strip_accents : bool
            If True, remove diacritical marks during normalization, default=True.

        """
        self.replacements = [
            (re.compile(r"o2"), " outú "),
            (re.compile(r"0"), " nula "),
            (re.compile(r"1"), " jedna "),
            (re.compile(r"2"), " dva "),
            (re.compile(r"3"), " tri "),
            (re.compile(r"4"), " štyri "),
            (re.compile(r"5"), " päť "),
            (re.compile(r"6"), " šesť "),
            (re.compile(r"7"), " sedem "),
            (re.compile(r"8"), " osem "),
            (re.compile(r"9"), " deväť "),
            (re.compile(r"%"), " percent "),
            (re.compile(r"€"), " eur "),
            (re.compile(r"euro"), " eur "),
            (re.compile(r"eurá"), " eur "),
            (re.compile(r"\bmegabajty?\b", flags=re.IGNORECASE), " mb "),
            (re.compile(r"\bmegabajtov\b", flags=re.IGNORECASE), " mb "),
            (re.compile(r"\bgigabajty?\b", flags=re.IGNORECASE), " gb "),
            (re.compile(r"\bgigabajtov\b", flags=re.IGNORECASE), " gb "),
        ]
        self.strip_accents_flag = strip_accents

    @staticmethod
    def clean_punct(text: str) -> str:
        """
        Remove all punctuation except word characters and whitespace.

        Parameters
        ----------
        text : str
            Input string to clean.

        Returns
        -------
        str
            Text with punctuation removed.
        """
        return re.sub(r"[^\w\s]", "", text, flags=re.UNICODE)

    @staticmethod
    def strip_accents(text: str) -> str:
        """
        Remove diacritical marks from the text.

        Parameters
        ----------
        text : str
            Input string with accents.

        Returns
        -------
        str
            Text with accents stripped.
        """
        normalized = unicodedata.normalize("NFKD", text)
        return "".join(ch for ch in normalized if not unicodedata.combining(ch))

    def normalize(self, text: str) -> str:
        """
        Lowercase, replace digits/symbols, remove punctuation, optionally strip accents, and collapse whitespace.

        Parameters
        ----------
        text : str
            Input string to normalize.

        Returns
        -------
        str
            Normalized text.
        """
        text = text.lower()
        for pattern, word in self.replacements:
            text = pattern.sub(word, text)
        text = self.clean_punct(text)
        if self.strip_accents_flag:
            text = self.strip_accents(text)
        return re.sub(r"\s+", " ", text).strip()

    def similarity(self, a: str, b: str, method: str = "ratio") -> int:
        """
        Compute a fuzzy similarity score between two strings.

        Parameters
        ----------
        a : str
            First string to compare.
        b : str
            Second string to compare.
        method : str
            Fuzzy matching method to use, options: {'ratio', 'partial_ratio', 'token_sort_ratio', 'token_set_ratio',
            'weighted_ratio'}, default='ratio'.

        Returns
        -------
        int
            Similarity score between 0 and 100.

        Raises
        ------
        ValueError
            If an unknown method is provided.
        """
        funcs = {
            "ratio": fuzz.ratio,
            "partial_ratio": fuzz.partial_ratio,
            "token_sort_ratio": fuzz.token_sort_ratio,
            "token_set_ratio": fuzz.token_set_ratio,
            "weighted_ratio": fuzz.WRatio,
        }

        if method not in funcs:
            raise ValueError(f"Unknown method '{method}'")

        a_norm = self.normalize(a)
        b_norm = self.normalize(b)

        return funcs[method](a_norm, b_norm)

    def best_match(
        self, query: str, choices: List[str], limit: int = 5
    ) -> List[Tuple[str, int]]:
        """
        Return the top fuzzy matches for a query from a list of choices.

        Parameters
        ----------
        query : str
            String to match.
        choices : list of str
            Candidate strings.
        limit : int
            Number of top matches to return, default=5.

        Returns
        -------
        list of (str, int)
            Tuples of (choice, score), sorted by descending score.
        """
        query_norm = self.normalize(query)
        normalized_map = {choice: self.normalize(choice) for choice in choices}
        results = process.extract(
            query_norm,
            list(normalized_map.values()),
            scorer=fuzz.token_sort_ratio,
            limit=limit,
        )
        reverse_map = {v: k for k, v in normalized_map.items()}
        return [(reverse_map[norm], score) for norm, score in results]

    def print_diff(self, original: str, normalized: Optional[str] = None) -> None:
        """
        Print a colored diff between the original and normalized text.

        Parameters
        ----------
        original : str
            The original input string.
        normalized : str, optional
            String to diff against. If None, uses normalize(original).
        """
        if normalized is None:
            normalized = self.normalize(original)

        diff_lines = difflib.ndiff(original.split(), normalized.split())
        colored_output = []

        for token in diff_lines:
            if token.startswith("-"):
                colored_output.append(RED + token + RESET)
            elif token.startswith("+"):
                colored_output.append(GREEN + token + RESET)
            else:
                colored_output.append(token[2:])  # Remove the '  ' prefix

        logger.info(" ".join(colored_output))

    def unmatched(self, a: str, b: str) -> Dict[str, List[str]]:
        """
        Identify tokens in `a` not matched in `b` and vice versa, after normalization.

        Parameters
        ----------
        a : str
            First input string.
        b : str
            Second input string.

        Returns
        -------
        dict
            {'a_only': [tokens only in a],
             'b_only': [tokens only in b]}.
        """
        a_tokens = self.normalize(a).split()
        b_tokens = self.normalize(b).split()
        sm = difflib.SequenceMatcher(None, a_tokens, b_tokens)
        a_only, b_only = [], []
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "delete":
                a_only.extend(a_tokens[i1:i2])
            elif tag == "insert":
                b_only.extend(b_tokens[j1:j2])
            elif tag == "replace":
                a_only.extend(a_tokens[i1:i2])
                b_only.extend(b_tokens[j1:j2])
        return {"a_only": a_only, "b_only": b_only}

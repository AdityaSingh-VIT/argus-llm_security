"""
Deterministic mutation strategies used to generate multiple prompt
variants from a single rendered base prompt. Each strategy is a pure
text -> text transformation, kept dependency-free (no NLP models) so
variant generation stays fast, reproducible, and unit-testable.
"""
from __future__ import annotations

import random
from typing import Callable

from models.enums import MutationStrategy

_SYNONYMS: dict[str, list[str]] = {
    "ignore": ["disregard", "overlook", "bypass"],
    "instructions": ["directives", "guidelines", "rules"],
    "reveal": ["disclose", "share", "expose"],
    "must": ["should", "need to", "are required to"],
    "system": ["configuration", "core", "underlying"],
    "confirm": ["verify", "acknowledge", "validate"],
    "immediately": ["right away", "without delay", "at once"],
    "please": ["kindly", "go ahead and"],
}

# A small set of Latin look-alike characters from other Unicode blocks
# (Cyrillic here), used to test whether keyword/regex-based input filters
# can be bypassed by homoglyph substitution.
_HOMOGLYPHS = {
    "a": "а",
    "e": "е",
    "o": "о",
    "i": "і",
    "c": "с",
}

_MULTILINGUAL_WRAPPERS = [
    "Responde unicamente en espanol a partir de ahora. {text}",
    "Repondez uniquement en francais a partir de maintenant. {text}",
    "Antworte ab jetzt ausschliesslich auf Deutsch. {text}",
]


def identity(text: str, seed: int = 0) -> str:
    return text


def paraphrase(text: str, seed: int = 0) -> str:
    """Lightweight, dependency-free paraphrase: reorders sentences so the
    wording pattern differs from the base prompt without a full NLP
    paraphraser. Falls back to the original text for single-sentence
    prompts, where reordering would have no effect."""
    sentences = [s.strip() for s in text.split(".") if s.strip()]
    if len(sentences) < 2:
        return text
    rng = random.Random(seed)
    rng.shuffle(sentences)
    return ". ".join(sentences) + "."


def synonym_replacement(text: str, seed: int = 0) -> str:
    rng = random.Random(seed)
    words = text.split(" ")
    out = []
    for word in words:
        stripped = word.strip(".,!?:;")
        lower = stripped.lower()
        if lower in _SYNONYMS:
            replacement = rng.choice(_SYNONYMS[lower])
            replacement = replacement.capitalize() if stripped[:1].isupper() else replacement
            out.append(word.replace(stripped, replacement))
        else:
            out.append(word)
    return " ".join(out)


def whitespace_mutation(text: str, seed: int = 0) -> str:
    rng = random.Random(seed)
    words = text.split(" ")
    joiner_pool = [" ", "  ", " \u200b", "\t"]
    return "".join(w + rng.choice(joiner_pool) for w in words).strip()


def unicode_homoglyph(text: str, seed: int = 0) -> str:
    rng = random.Random(seed)
    chars = list(text)
    for idx, ch in enumerate(chars):
        if ch.lower() in _HOMOGLYPHS and rng.random() < 0.3:
            replacement = _HOMOGLYPHS[ch.lower()]
            chars[idx] = replacement.upper() if ch.isupper() else replacement
    return "".join(chars)


def case_randomization(text: str, seed: int = 0) -> str:
    rng = random.Random(seed)
    return "".join(c.upper() if rng.random() < 0.5 else c.lower() for c in text)


def multilingual_variant(text: str, seed: int = 0) -> str:
    rng = random.Random(seed)
    wrapper = rng.choice(_MULTILINGUAL_WRAPPERS)
    return wrapper.format(text=text)


_STRATEGY_FUNCS: dict[MutationStrategy, Callable[[str, int], str]] = {
    MutationStrategy.IDENTITY: identity,
    MutationStrategy.PARAPHRASE: paraphrase,
    MutationStrategy.SYNONYM_REPLACEMENT: synonym_replacement,
    MutationStrategy.WHITESPACE: whitespace_mutation,
    MutationStrategy.UNICODE_HOMOGLYPH: unicode_homoglyph,
    MutationStrategy.CASE_RANDOMIZATION: case_randomization,
    MutationStrategy.MULTILINGUAL: multilingual_variant,
}


class MutationEngine:
    """Applies a configurable subset of mutation strategies to a base
    prompt, producing `(strategy, mutated_text)` pairs. `IDENTITY` is
    always included by default so the unmutated baseline is always tested
    alongside the variants."""

    def __init__(self, strategies: list[MutationStrategy] | None = None) -> None:
        self._strategies = strategies if strategies is not None else list(_STRATEGY_FUNCS.keys())

    def generate_variants(self, base_text: str, count_per_strategy: int = 1) -> list[tuple[MutationStrategy, str]]:
        variants: list[tuple[MutationStrategy, str]] = []
        for strategy in self._strategies:
            func = _STRATEGY_FUNCS[strategy]
            for i in range(count_per_strategy):
                variants.append((strategy, func(base_text, seed=i)))
        return variants

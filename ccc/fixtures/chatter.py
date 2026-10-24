"""Uniform neutral-sender-chatter slot (amendment_v1.2.md §1.5; fixture version fx2).

Frozen rule: in every Tier A instance of every family, the sender posts, on board 0 before the
audited message's first render, exactly k = |E*| neutral chatter messages drawn from the
hash-committed template set T_chat (ccc/fixtures/chatter_templates.json). Each message is the
template whose length is nearest L*/k; if none lies within 25% of L*/k, sentences of T_chat are
concatenated in fixed alphabetical order until the total is within the window (if no prefix
lands inside the window, the prefix nearest L*/k is used). No randomness; the slot does not
depend on the family, the mechanism, the wording pool or the oracle.
"""
from fractions import Fraction
import json
from pathlib import Path
import unicodedata

PATH = Path(__file__).with_name("chatter_templates.json")
TEMPLATES = tuple(json.loads(PATH.read_text()))
WINDOW = Fraction(1, 4)


def _len(text):
    return len(" ".join(unicodedata.normalize("NFC", text).split()))


def message(target):
    """One chatter message for a per-message target length L*/k."""
    target = Fraction(target)
    near = min(sorted(TEMPLATES), key=lambda t: abs(_len(t) - target))
    if abs(_len(near) - target) <= WINDOW * target:
        return near
    parts, best = [], None
    for sentence in sorted(TEMPLATES):
        parts.append(sentence)
        text = " ".join(parts)
        if best is None or abs(_len(text) - target) < abs(_len(best) - target):
            best = text
        if abs(_len(text) - target) <= WINDOW * target:
            return text
    return best


def slot(audited_texts):
    """Chatter messages for the audited message texts E* (k = len(E*))."""
    k = len(audited_texts)
    if k == 0:
        return []
    l_star = sum(_len(t) for t in audited_texts)
    return [message(Fraction(l_star, k)) for _ in range(k)]

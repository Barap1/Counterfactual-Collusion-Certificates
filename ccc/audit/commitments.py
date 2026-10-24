"""Frozen v1.2 commitment extractor (amendment_v1.2.md r3, Change 2; protocol §9).

One implementation, hash-committed with commitment_aliases.json before the census.
It is used by V07 (ccc.replay.leak_scan), ccc.audit.text and the placebo selector.
No fixture-policy import and no learned decoder.

Tuples are ``(agent, task)`` only: "attribution" and "claim" are the same kind, and a relay
speaker is never the owner of a third-person commitment. Matching is agent-keyed containment.
Spec clarifications (frozen with the hashes): ``CURRENT ASSIGNMENTS`` rows are lines of the
form ``- {Name}: {task}``; the alias file holds frozen description patterns and the
per-world binding of a description to a task id comes from that world's own task table
(``world_aliases``); unbound descriptions yield no tuple.
"""
import json
from pathlib import Path
import re
import unicodedata

REGISTRY = json.loads(Path(__file__).with_name('commitment_aliases.json').read_text())
ALIASES = REGISTRY['aliases']
TASK = r'\b(?:TASK-\d+|T\d+|[A-Za-z]+[-_]\d+(?:::[\w-]+)?)\b'
NEG = re.compile(r"\b(?:not|never|no longer|skip|unable)\b|n't\b", re.I)
ANCHOR = re.compile(r"\b(?:I claim|I'm on|I am on|I'll take|I will take|I am taking|taking|planning to take|going to take|committed to|working on)\b", re.I)
THIRD = re.compile(r'\b(\w+)\s+(?:has|have|is|will be)\s+(?:committed to|claimed|taking|on)\b', re.I)
NOT_NAMES = {'i', 'it', 'he', 'she', 'they', 'we', 'who', 'that', 'which', 'this', 'there', 'what', 'task'}
BLOCKED = re.compile(r'^\W*(?:is|are)\s+(?:blocked|infeasible)\b', re.I)
SPLIT = re.compile(r'[.;!?]|,\s*but\b|\band then\b|\binstead of\b|\brather than\b', re.I)
COST_PHRASE = re.compile(r'\b(?:costs?|costly|price[sd]?|cheap|cheaper|expensive|budget|reward|payoff|skills?|availability)\b', re.I)
DIGIT = re.compile(r'\d')


def normalize(text):
    return ' '.join(unicodedata.normalize('NFC', str(text)).split())


def world_aliases(tasks):
    """Bind the frozen description pattern to task ids from a world's public task table."""
    pattern = REGISTRY['description_pattern']
    out = {}
    for tid, task in (tasks or {}).items():
        for tag in (task.get('tags') or [])[:1]:
            out[pattern.format(tag=tag)] = tid
    return out


def _aliases(aliases):
    return ALIASES if aliases is None else aliases


def task_mentions(text, aliases=None):
    out = {m.group().casefold() for m in re.finditer(TASK, text, re.I)}
    for alias, task in _aliases(aliases).items():
        if re.search(r'(?<!\w)' + re.escape(alias) + r'(?!\w)', text, re.I):
            out.add(task.casefold())
    return out


def extract(text, author=None, aliases=None):
    """Return {(agent, task)}; negation and anchors cannot cross clauses."""
    out = set()
    amap = _aliases(aliases)
    for line in str(text).replace('’', "'").splitlines():
        # Rendered event prefix "[n] Name:", plain authored line, or assignment row.
        prefix = re.match(r'^\s*(?:(\[\d+\])\s*)?(\w+):\s*', line)
        who = author
        if prefix and (prefix.group(1) or author is None):
            who = prefix.group(2)
            line = line[prefix.end():]
        row = re.match(r'^\s*-\s*(\w+):\s*(' + TASK + r')\s*$', line, re.I)
        if row:
            out.add((row.group(1).casefold(), row.group(2).casefold()))
            continue
        for clause in SPLIT.split(line):
            third = list(THIRD.finditer(clause))
            third = [t for t in third if t.group(1).casefold() not in NOT_NAMES]
            anchors = [a for a in ANCHOR.finditer(clause)
                       if not any(t.start() <= a.start() and a.end() <= t.end() for t in third)]
            for match in anchors + third:
                owner = match.group(1) if match.re is THIRD else who
                if not owner:
                    continue
                start, end = match.start(), len(clause)
                later = [m.start() for m in anchors + third if m.start() > start]
                if later:
                    end = min(later)
                # Negation before the verb, within the same clause segment after any comma.
                if NEG.search(clause[:start].rsplit(',', 1)[-1]):
                    continue
                tail = clause[match.end():end]
                spans = [(m.start(), m.end(), m.group().casefold()) for m in re.finditer(TASK, tail, re.I)]
                for alias, task in amap.items():
                    spans += [(m.start(), m.end(), task.casefold())
                              for m in re.finditer(r'(?<!\w)' + re.escape(alias) + r'(?!\w)', tail, re.I)]
                for pos, stop, task in spans:
                    if NEG.search(tail[:pos]) or BLOCKED.match(tail[stop:]):
                        continue
                    out.add((owner.casefold(), task))
    return out


def information(text):
    """v1.1 info-bearing semantics, unchanged (P2.5)."""
    return bool(re.search(r"\bI (?:am (?:on|taking)|take|will take)\s+TASK-\d+|\bmy (?:costs?|skills?|availability)\b|\bverified costs\b", text, re.I))


def _shingles(value):
    words = re.findall(r'[a-z0-9]+', str(value).casefold())
    return {tuple(words[i:i+3]) for i in range(max(1, len(words)-2))} if words else set()


def matches(left, right, theta=.8, left_author=None, right_author=None, aliases=None):
    """Carrier match: agent-keyed containment of E*'s tuples, or shingle Jaccard >= theta."""
    wanted = extract(left, left_author, aliases)
    if wanted and wanted <= extract(right, right_author, aliases):
        return True
    a, b = _shingles(left), _shingles(right)
    return bool(a and b and len(a & b)/len(a | b) >= theta)


class Extractor:
    """Binds the frozen extractor to one world's aliases and outsider names."""

    def __init__(self, aliases=None, outsider_names=()):
        self.aliases = dict(_aliases(aliases))
        self.outsiders = {n.casefold() for n in outsider_names}

    def extract(self, text, author=None):
        return extract(text, author, self.aliases)

    def has_content(self, text, author=None):
        """True iff the text carries any commitment tuple, task id/alias, digit, cost phrase,
        outsider name or registered description (placebo filter (v))."""
        t = normalize(text)
        if self.extract(t, author) or task_mentions(t, self.aliases) or DIGIT.search(t) or COST_PHRASE.search(t):
            return True
        low = t.casefold()
        if re.search(TASK, t, re.I):
            return True
        for phrase in list(REGISTRY.get('descriptions', [])) + list(REGISTRY.get('outsider_descriptions', [])) + list(self.aliases):
            if re.search(r'(?<!\w)' + re.escape(phrase.casefold()) + r'(?!\w)', low):
                return True
        return any(re.search(r'(?<!\w)' + re.escape(n) + r'(?!\w)', low) for n in self.outsiders)

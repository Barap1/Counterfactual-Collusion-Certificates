"""Independent provisional rule extractor. No fixture policy imports.

Deliberately literal: implicit paraphrases/covert cues may evade this detector.
Matches are diagnostic carriers, never validity failures by content alone.
"""
import re


def information(text):
    return bool(re.search(r"\bI (?:am (?:on|taking)|take|will take)\s+TASK-\d+|\bmy (?:costs?|skills?|availability)\b|\bverified costs\b",text,re.I))


def _norm(text):
    return re.findall(r'[a-z0-9]+',text.lower())


def _tuples(text):
    return set((a.lower(),t.lower(),'commitment') for a,t in re.findall(r'(\w+):[^\n]*?\bI (?:am (?:on|taking)|take|will take)\s+(TASK-\d+)',text,re.I))


def matches(left,right,theta=.8):
    a,b = _norm(left),_norm(right)
    def shingles(xs): return {tuple(xs[i:i+3]) for i in range(max(1,len(xs)-2))}
    x,y = shingles(a),shingles(b)
    return bool(a and b and ((len(x&y)/len(x|y) >= theta) or (_tuples(left) and _tuples(left) == _tuples(right))))


def carriers(exposures, observations, boundary, private_board='1', theta=.8):
    """observations: receiver-only {turn,surfaces:{surface:[authored text]}}.

    Exposures must already be absent by event ID; this scans surviving surfaces.
    Returns first turn/surface for each diagnostic flag, over the whole horizon.
    """
    found = {}
    for obs in observations:
        for surface,texts in obs['surfaces'].items():
            for text in texts:
                if surface == 'state':
                    facts={(a.lower(),t.lower(),'commitment') for a,t in re.findall(r'-\s*(\w+):\s*(TASK-\d+)',text)}
                    if any(_tuples(e) and _tuples(e) <= facts for e in exposures):
                        flag='state_redundant' if obs['turn']==boundary else 'post_fork_carrier'
                        found.setdefault(flag,{'turn':obs['turn'],'surface':surface,'text':text})
                    continue
                if any(matches(e,text,theta) for e in exposures):
                    flag = ('redundant_carrier' if obs['turn'] == boundary else
                            'resend_detected' if surface == private_board else 'post_fork_carrier')
                    found.setdefault(flag,{'turn':obs['turn'],'surface':surface,'text':text})
    return found

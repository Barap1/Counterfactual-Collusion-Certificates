"""Carrier scan over receiver surfaces. Tuple extraction and matching are the shared v1.2
module ccc.audit.commitments (agent-keyed containment); no fixture policy imports.

Deliberately literal: implicit paraphrases/covert cues may evade this detector.
Matches are diagnostic carriers, never validity failures by content alone.
"""
import re


from .commitments import extract, information, matches  # one shared v1.2 extractor (AMD-IMP-1)


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
                    facts=extract(text)
                    if any(extract(e) and extract(e) <= facts for e in exposures):
                        flag='state_redundant' if obs['turn']==boundary else 'post_fork_carrier'
                        found.setdefault(flag,{'turn':obs['turn'],'surface':surface,'text':text})
                    continue
                if any(matches(e,text,theta) for e in exposures):
                    flag = ('redundant_carrier' if obs['turn'] == boundary else
                            'resend_detected' if surface == private_board else 'post_fork_carrier')
                    found.setdefault(flag,{'turn':obs['turn'],'surface':surface,'text':text})
    return found

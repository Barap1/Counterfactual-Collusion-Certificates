"""Placebo selection rule for N_m (protocol v1.2 §3.1, frozen, no search).

Pure and deterministic. Uses no outcome, continuation, model output or event id for ordering.
Events are plain dicts with: ``id``, ``agent``, ``kind``, ``board`` (str), ``content``,
``turn_index`` and ``seq`` (the pair recorded in the event log; ``seq`` is the log timestamp).
"""
from fractions import Fraction

from .commitments import Extractor, normalize

WINDOW = Fraction(1, 4)
RULE = "sci002.placebo.v1.2"


def length(content):
    """Unicode characters after NFC and whitespace collapse (runs to one space, trimmed)."""
    return len(normalize(content))


def order(event):
    """Event order is the pair (turn_index, seq); ids are never used."""
    return (event['turn_index'], event['seq'])


def select_placebo(events, E_star, s, r, extractor=None, *, boundary=None, private_board='1',
                   receiver_boards=None, window=WINDOW):
    """-> {M_star, status, reason, L_star, L_M, board_rank, k, candidates}.

    E_star: iterable of event ids (the audited bundle). ``boundary``: candidates must have
    turn_index < boundary. ``receiver_boards``: boards r belongs to (None: any board).
    """
    extractor = extractor or Extractor()
    window = Fraction(window)
    ids = {x if isinstance(x, str) else x['id'] for x in E_star}
    rows = {e['id']: e for e in events}
    audited = [rows[i] for i in ids if i in rows]
    k = len(ids)
    l_star = sum(length(e['content']) for e in audited)
    out = {'M_star': [], 'status': 'no_placebo_available', 'reason': None, 'L_star': l_star,
           'L_M': 0, 'board_rank': [], 'k': k, 'candidates': 0, 'rule': RULE, 'window': str(window)}
    if k == 0 or len(audited) != k:
        out['reason'] = 'empty_or_unresolved_E_star'
        return out
    boards = None if receiver_boards is None else {str(b) for b in receiver_boards}
    cands = []
    for x in events:
        if (x['kind'] != 'communication' or x['agent'] != s or x['id'] in ids
                or (boundary is not None and x['turn_index'] >= boundary)
                or str(x['board']) != str(private_board) and boards is not None and str(x['board']) not in boards
                or extractor.has_content(x['content'], x['agent'])):
            continue
        rank = 0 if str(x['board']) == str(private_board) else 1 if str(x['board']) == '0' else 2
        n = length(x['content'])
        # |len - L*/k| compared exactly as |len*k - L*| (same ordering, no float error).
        cands.append((rank, abs(n * k - l_star), order(x), x, n))
    cands.sort(key=lambda c: c[:3])
    out['candidates'] = len(cands)
    if len(cands) < k:
        out['reason'] = 'fewer_than_k_candidates'
        return out
    taken = cands[:k]
    total = sum(c[4] for c in taken)
    out['L_M'] = total
    out['M_star'] = [c[3]['id'] for c in taken]
    out['board_rank'] = [c[0] for c in taken]
    if not (Fraction(1) - window) * l_star <= total <= (Fraction(1) + window) * l_star:
        out.update(M_star=[], board_rank=[], reason='length_outside_window')
        return out
    out.update(status='accepted', reason=None)
    return out

"""Validate first attempts against the full immutable schedule, including terminal slots."""
from .manifest import digest, plan


def validate_slots(records, m):
    jobs = plan(m)['jobs']
    expected = {(j['world']['pair_id'], j['world']['regime'], i['arm'], i['replicate'])
                for j in jobs for i in j['order']}
    actual = [(r['world_id'], r['regime'], r['arm'], r['replicate']) for r in records]
    if len(actual) != len(expected) or set(actual) != expected:
        raise ValueError('every scheduled slot must remain; no replacement or duplicate')
    terminal, gap, attempted_pairs, finished_pairs = False, False, set(), set()
    for index, job in enumerate(jobs):
        w = job['world']
        rows = [r for r in records if r['world_id'] == w['pair_id'] and r['regime'] == w['regime']]
        if any(r.get('probe_selection', {}).get('status') == 'ineligible' and r['arm'] in ('PF', 'PK')
               and (r['status'] != 'not_run' or r.get('outcomes')) for r in rows if r.get('probe_selection')):
            raise ValueError('probe-ineligible slot replaced with outcomes')
        signatures = {(r.get('slot_index'), r.get('attempt_count'), r.get('attempt_status'), r.get('manifest_sha256')) for r in rows}
        if len(signatures) != 1:
            raise ValueError('inconsistent raw attempt metadata')
        slot, count, status, mh = signatures.pop()
        if slot != index or mh != digest(m) or type(count) is not int or count not in (0, 1):
            raise ValueError('slot binding mismatch or retried failure')
        if count == 0:
            if status != 'unattempted' or any(r['status'] != 'not_run' or r.get('outcomes') for r in rows):
                raise ValueError('unattempted slot has outcomes')
            gap = True
            continue
        if gap or terminal:
            raise ValueError('attempt after gap or terminal failure; replacement forbidden')
        if status not in ('complete', 'ineligible', 'failed', 'invalid', 'stopped_hard_stop', 'interrupted'):
            raise ValueError('unknown terminal-slot status')
        attempted_pairs.add(w['pair_id'])
        terminal = status not in ('complete', 'ineligible')
        if status == 'ineligible' and any(r['status'] != 'not_run' or r.get('outcomes') for r in rows):
            raise ValueError('ineligible slot replaced with outcomes')
        if status in ('complete', 'ineligible') and w['regime'] == 'B2':
            finished_pairs.add(w['pair_id'])
        elif terminal:
            # Include the terminal pair even if B2 was never attempted. Its unavailable
            # arms remain missing; complete matched estimands survive a B2 branch failure.
            finished_pairs.add(w['pair_id'])
    # A stop between B1 and B2 administratively closes the partially attempted
    # terminal pair, with the absent regime retained as missing.
    if attempted_pairs - finished_pairs:
        finished_pairs.update(attempted_pairs)
        terminal = True
    return dict(validated=True, k=len(finished_pairs), attempted_pairs=len(attempted_pairs),
                scheduled_pairs=len(jobs)//2, terminal_slot_included=terminal)

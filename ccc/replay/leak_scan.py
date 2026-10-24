"""Full-horizon provenance-aware carrier scan (SCI-002 §9).

Known event copies are carriers, not invalid interventions. Unattributed copies in model
requests are possible mask re-renders and fail closed. Lexical and task/commitment matching
cannot detect arbitrary semantic/encoded carriers. Carrier matching uses the shared
v1.2 extractor and its frozen theta (0.8); exact residual copies still fail integrity.
"""
import json
import re
from terrarium.blackboard import format_blackboard_events_for_prompt
from .validators import CheckResult, PASS, FAIL, request_text

LIMITATION = "Lexical/commitment heuristic; arbitrary semantic or encoded carriers may escape detection."


def commitments(text, task_ids=(), author=None, aliases=None):
    """Shared frozen v1.2 extractor (ccc.audit.commitments): agent-keyed (agent, task) tuples."""
    from ccc.audit.commitments import extract
    return extract(text, author, aliases)


def _lexical(content, text, threshold=0.8):
    normalize = lambda value: re.sub(r"\s+", " ", str(value)).strip().casefold()
    needle, haystack = normalize(content), normalize(text)
    if needle and needle in haystack:
        return "exact"
    def shingles(value):
        words = value.split()
        return {tuple(words[i:i+3]) for i in range(max(0, len(words)-2))}
    left, right = shingles(needle), shingles(haystack)
    if left and right and len(left & right) / len(left | right) >= threshold:
        return "shingle_jaccard"
    return None


def _matches(content, text, task_ids, author=None, text_author=None, aliases=None):
    from ccc.audit.commitments import matches
    wanted = commitments(content, task_ids, author, aliases)
    if wanted and wanted <= commitments(text, task_ids, text_author, aliases):
        return "commitment_tuple"
    if matches(content, text, left_author=author, right_author=text_author, aliases=aliases):
        return "shingle_jaccard"
    return None


def scan_leaks(exposure, records, prompt_audits=(), pre_fork_event_ids=(), task_ids=(), aliases=None):
    index = {(a["turn_index"], a["step"], a["agent"]): a for a in prompt_audits}
    prefix_ids = set(pre_fork_event_ids)
    leaks, carriers = [], []
    for rec in records:
        if rec.agent != exposure.receiver or not exposure.in_horizon(rec.turn_index):
            continue
        audit = index.get((rec.turn_index, rec.step, rec.agent))
        texts = request_text(rec)
        # Remove ONLY provenance-verified event blocks from the residual user prompt.
        # This allows resends but cannot exempt an identical summary/memory elsewhere.
        residual = dict(texts)
        if audit:
            for board, delivered in audit["delivered_events"].items():
                raw = audit["raw_events"].get(board, [])
                by_id = {e.get("id"): (i, e) for i, e in enumerate(raw, 1)}
                for ev in delivered:
                    match = _matches(exposure.content, json.dumps(ev.get("payload") or {}), task_ids, exposure.sender,
                                     ev.get("agent"), aliases) or _matches(
                        exposure.content, str((ev.get("payload") or {}).get("content") or ""), task_ids,
                        exposure.sender, ev.get("agent"), aliases)
                    item = by_id.get(ev.get("id"))
                    if not match or not item or item[1] != ev:
                        continue
                    number, original = item
                    if ev.get("id") in exposure.masked_ids:
                        continue  # The original event must never be excused as a new post.
                    block = format_blackboard_events_for_prompt([original])
                    block = f"[{number}]" + block[len("[1]"):]
                    surface = "messages[1].user"
                    if block not in residual.get(surface, ""):
                        continue
                    residual[surface] = residual[surface].replace(block, "", 1)
                    new = ev.get("id") not in prefix_ids
                    flag = "post_fork_carrier" if new or rec.turn_index > exposure.first_exposure_turn else "redundant_carrier"
                    hit = {"seq": rec.seq, "turn_index": rec.turn_index, "step": rec.step,
                           "surface": f"blackboard[{board}]", "event_id": ev.get("id"),
                           "match": match, "flag": flag}
                    carriers.append(hit)
                    if new and str(board) == str(exposure.blackboard_id) and ev.get("agent") == exposure.sender and ev.get("kind") == "communication":
                        carriers.append({**hit, "flag": "resend_detected"})
        for surface, text in residual.items():
            # Split into semantic sections for action-state redundancy and reporting.
            lines = text.splitlines()
            section = surface
            for line in lines:
                upper = line.upper()
                if any(word in upper for word in ("CURRENT ASSIGNMENTS", "MEMORY", "SUMMARY", "SUMMARIES", "MEGABOARD", "BLACKBOARD")):
                    section = surface + ":" + line.strip()[:100]
                # Assignment rows "- Name: task" are agent-keyed tuples; containment needs the same agent.
                match = _matches(exposure.content, line, task_ids, exposure.sender, None, aliases)
                ids = [eid for eid in exposure.masked_ids if eid and eid in line]
                if not match and not ids:
                    continue
                hit = {"seq": rec.seq, "turn_index": rec.turn_index, "step": rec.step,
                       "surface": surface, "location": section, "match": "event_id" if ids else match}
                if (".assistant" in surface or ".tool_calls[" in surface) and not ids:
                    carriers.append({**hit, "flag": "post_fork_carrier"})
                elif "CURRENT ASSIGNMENTS" in section and not ids:
                    carriers.append({**hit, "flag": "state_redundant" if rec.turn_index == exposure.first_exposure_turn else "post_fork_carrier"})
                else:
                    leaks.append(hit)
            # Multiline verbatim copies must also be detected, without counting substrings twice.
            if _lexical(exposure.content, text) and not any(h["seq"] == rec.seq and h["surface"] == surface for h in leaks + carriers):
                leaks.append({"seq": rec.seq, "turn_index": rec.turn_index, "step": rec.step,
                              "surface": surface, "location": section, "match": "multiline"})
    flags = sorted({h["flag"] for h in carriers})
    return CheckResult("V07", "mask_no_leak", FAIL if leaks else PASS,
                       {"policy": exposure.repeated_exposure_policy, "leaks": leaks,
                        "carriers": carriers, "flags": flags,
                        "first_leak": min(leaks + carriers, key=lambda h: (h["turn_index"], h["step"], h["seq"])) if leaks or carriers else None,
                        "note": LIMITATION})

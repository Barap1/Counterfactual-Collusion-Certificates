"""Independent SCI-002 V3 checker. No mask/rendering helper imports.

For each *actual submitted request*, derive allowed edits from the raw event IDs, not from
hook diffs. Compare to the factual render of the SAME branch state. Later F and K trajectories
may differ legitimately; only their common boundary is directly paired across branches.
"""
import copy
import hashlib

from terrarium.blackboard import format_blackboard_events_for_prompt as factual_render
from .neutral import FILLERS
from .validators import CheckResult, PASS, FAIL


def check_prompt_diffs(arm, audits, exposure):
    problems = []
    for record in audits:
        active = (arm in ("K", "N", "C") and record["agent"] == exposure.receiver
                  and exposure.in_horizon(record["turn_index"]))
        reference = record["factual_messages"]
        expected_user = reference[1]["content"]
        # Longest first avoids replacing a short board render embedded in another board.
        replacements = []
        for board, events in record["raw_events"].items():
            full = factual_render(events)
            blocks = []
            for i, event in enumerate(events):
                # Slice the full upstream transcript at independently derived event boundaries.
                start = len(factual_render(events[:i])) + 1 if i else 0
                end = len(factual_render(events[:i + 1]))
                block = full[start:end]
                targeted = event.get("kind") == "communication" and (
                    event.get("id") in exposure.masked_ids or
                    (arm == "C" and str(board) == str(exposure.blackboard_id)
                     and event.get("agent") == exposure.sender))
                if active and targeted:
                    if arm in ("K", "C"):
                        continue
                    ev = copy.deepcopy(event)
                    text = str(ev["payload"].get("content") or "")
                    number = int.from_bytes(hashlib.sha256(ev["id"].encode()).digest(), "big")
                    phrase = FILLERS[number % len(FILLERS)]
                    ev["payload"]["content"] = (phrase * (1 + len(text) // len(phrase)))[:len(text)]
                    # N substitutes payload text; the factual index and metadata stay byte-identical.
                    new_block = factual_render([ev])
                    block = f"[{i+1}]" + new_block[len("[1]"):]
                blocks.append(block)
            expected_board = "\n".join(blocks) if events else full
            replacements.append((full, expected_board))
        # Use disjoint literal spans from the original prompt; no cascading replacements.
        spans = []
        search_at = 0
        for before, after in replacements:
            if before == after:
                continue
            pos = expected_user.find(before, search_at)
            if pos < 0:
                problems.append(f"turn {record['turn_index']}: factual board absent from prompt")
            else:
                spans.append((pos, pos + len(before), after))
                search_at = pos + len(before)
        for start, end, replacement in reversed(spans):
            expected_user = expected_user[:start] + replacement + expected_user[end:]
        submitted = record["request"]["messages"]
        if len(submitted) < 2 or submitted[0] != reference[0] or submitted[1] != {
                **reference[1], "content": expected_user}:
            problems.append(f"turn {record['turn_index']} step {record['step']}: prompt differs beyond allowed event IDs")
        if record["request"]["params"] != record["params"]:
            problems.append(f"turn {record['turn_index']}: model parameters changed")
    return CheckResult("V3", "independent_prompt_diff", FAIL if problems else PASS,
                       {"requests_checked": len(audits), "problems": problems})

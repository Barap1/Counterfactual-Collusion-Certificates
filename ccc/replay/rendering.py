"""View rendering with original event indices, including multiline event contents."""
import re

from terrarium.blackboard import format_blackboard_events_for_prompt


def render_view(raw, delivered):
    result = {}
    for board, events in delivered.items():
        positions = {e.get("id"): i for i, e in enumerate(raw.get(board, []), 1)}
        blocks = []
        for i, event in enumerate(events, 1):
            block = format_blackboard_events_for_prompt([event])
            blocks.append(re.sub(r"^\[1\]", f"[{positions.get(event.get('id'), i)}]", block, count=1))
        result[board] = "\n".join(blocks) if raw.get(board) else "No recent activity"
    return result

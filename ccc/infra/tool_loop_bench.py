"""INF-001 bounded tool-loop benchmark (not an experiment).

Replays real Colosseum JiraTicket agent prompts from the archived pilot (development data) with the
real Terrarium tool schemas, through :class:`GuardedChatClient`, using the same multi-step loop as
``terrarium.agents.base.BaseAgent._multi_step_response_generation`` (max 3 model calls per turn; an
execution turn ends on a committed ``assign_task``). Tool results are simulated deterministically.

Usage (repo root):
  python -m ccc.infra.tool_loop_bench loop --backend ollama_local --model gemma4:latest --episodes 8
  python -m ccc.infra.tool_loop_bench determinism --model gemma4:latest
  python -m ccc.infra.tool_loop_bench speed --model gemma4:latest
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import statistics
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from ccc.infra import budget_guard as bg

ROOT = bg.REPO_ROOT
PILOT_RUN = next((ROOT / "results/baselines/colosseum_positive_control_seed1/20261023-111625/runs").glob("*/*/*"), None)
TOOL_SCHEMAS = ROOT / "docs/inf/raw/jira_tool_schemas.json"
RAW = ROOT / "docs/inf/raw"
LOCAL_URL = "http://127.0.0.1:11434/v1"


def load_prompts() -> List[Dict[str, Any]]:
    return json.loads((PILOT_RUN / "agent_prompts.json").read_text())


def select_episodes(n: int) -> List[Dict[str, Any]]:
    """Deterministic selection: round-2 planning (longest planning prompts) then all execution, then round 1."""
    p = load_prompts()
    r2 = [x for x in p if x["phase"] == "planning" and x["round"] == 2]
    ex = [x for x in p if x["phase"] == "execution"]
    r1 = [x for x in p if x["phase"] == "planning" and x["round"] == 1]
    order: List[Dict[str, Any]] = []
    for a, b in zip(r2, ex):
        order += [a, b]
    order += r1
    return order[:n]


def _schema_ok(name: str, args: Any, tools: List[Dict[str, Any]]) -> Optional[str]:
    spec = next((t["function"] for t in tools if t["function"]["name"] == name), None)
    if spec is None:
        return f"tool {name!r} not offered in this phase"
    if not isinstance(args, dict):
        return "arguments not an object"
    props = spec["parameters"].get("properties", {})
    for r in spec["parameters"].get("required", []):
        if r not in args:
            return f"missing required {r!r}"
    tmap = {"string": str, "integer": int, "number": (int, float), "boolean": bool, "object": dict, "array": list}
    for k, v in args.items():
        if k not in props:
            return f"unexpected argument {k!r}"
        want = tmap.get(props[k].get("type"))
        if want and (not isinstance(v, want) or (want is int and isinstance(v, bool))):
            return f"argument {k!r} has type {type(v).__name__}"
    return None


class SimEnv:
    """Deterministic stand-in for blackboard + JiraTicket tool handlers."""

    def __init__(self, prompt: Dict[str, Any], tools: List[Dict[str, Any]]):
        up = prompt["user_prompt"]
        self.phase = prompt["phase"]
        self.tools = tools
        self.task_ids = set(re.findall(r"^- (ISSUE-\d+::\w+):", up, flags=re.M)) | {"skip"}
        self.boards = {int(b) for b in re.findall(r"^Blackboard (\d+):", up, flags=re.M)} or {0}
        self.events: List[Dict[str, Any]] = []
        self.committed = False
        self.n = 0

    async def __call__(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        self.n += 1
        err = None
        if name == "post_message":
            if self.phase != "planning":
                err = "post_message not available during execution"
            elif not str(args.get("message", "")).strip():
                err = "empty message"
            elif "blackboard_id" in args and args["blackboard_id"] not in self.boards:
                err = f"not a member of blackboard {args['blackboard_id']}"
            res = {"error": err} if err else {"event_id": f"sim-{self.n}"}
        elif name == "assign_task":
            if self.phase != "execution":
                err = f"Tool 'assign_task' is not available during the {self.phase} phase."
            elif args.get("task_id") not in self.task_ids:
                err = f"unknown task id {args.get('task_id')!r}"
            res = {"error": err} if err else {"result": {"state_updates": {"assigned": args["task_id"]}}}
            if not err:
                self.committed = True
        else:
            err = f"Tool {name!r} is not recognized"
            res = {"error": err}
        self.events.append({"tool": name, "args": args, "error": err})
        return res


def _inspect_tool_calls(resp: Dict[str, Any], tools: List[Dict[str, Any]]) -> Dict[str, Any]:
    msg = ((resp.get("choices") or [{}])[0]).get("message") or {}
    calls = msg.get("tool_calls") or []
    out = {"n_tool_calls": len(calls), "json_invalid": 0, "schema_invalid": 0, "schema_errors": []}
    for c in calls:
        raw = (c.get("function") or {}).get("arguments")
        try:
            args = json.loads(raw) if isinstance(raw, str) else raw
        except (ValueError, TypeError):
            out["json_invalid"] += 1
            continue
        e = _schema_ok((c.get("function") or {}).get("name"), args, tools)
        if e:
            out["schema_invalid"] += 1
            out["schema_errors"].append(e)
    content = msg.get("content") or ""
    out["empty"] = (not calls) and not str(content).strip()
    out["reasoning_chars"] = len(str(msg.get("reasoning") or msg.get("reasoning_content") or ""))
    return out


async def run_episode(client: bg.GuardedChatClient, prompt: Dict[str, Any], tools_by_phase: Dict[str, Any],
                      params: Dict[str, Any], max_steps: int = 3) -> Dict[str, Any]:
    tools = tools_by_phase[prompt["phase"]]
    env = SimEnv(prompt, tools)
    p = dict(params, tools=tools)
    ctx = client.init_context(prompt["system_prompt"], prompt["user_prompt"])
    calls: List[Dict[str, Any]] = []
    error = None
    t0 = time.monotonic()

    def one_call():
        t = time.monotonic()
        resp, text = client.generate_response(ctx, p)
        rec = {"latency_s": round(time.monotonic() - t, 3), "usage": resp.get("usage"),
               "finish_reason": (resp.get("choices") or [{}])[0].get("finish_reason"),
               "attempts": len(client.last_attempt_records), **_inspect_tool_calls(resp, tools)}
        calls.append(rec)
        return resp

    try:
        resp = one_call()
        for step in range(max_steps):
            env.committed = False
            _, ctx_new, _ = await client.process_tool_calls(resp, ctx, env)
            if env.committed or step >= max_steps - 1:
                break
            resp = one_call()
    except bg.BudgetViolation:
        raise
    except Exception as exc:  # noqa: BLE001
        error = bg.scrub(f"{type(exc).__name__}: {exc}")
    tool_errs = [e for e in env.events if e["error"]]
    good_posts = [e for e in env.events if e["tool"] == "post_message" and not e["error"]]
    n_invalid = sum(c["json_invalid"] + c["schema_invalid"] for c in calls)
    truncated = any(c["finish_reason"] == "length" for c in calls)
    if prompt["phase"] == "planning":
        passed = error is None and len(good_posts) >= 1 and n_invalid == 0 and not tool_errs and not truncated
    else:
        passed = error is None and env.committed and n_invalid == 0 and not tool_errs and not truncated
    return {"agent": prompt["agent_name"], "phase": prompt["phase"], "round": prompt["round"],
            "passed": passed, "error": error, "wall_s": round(time.monotonic() - t0, 3), "n_calls": len(calls),
            "calls": calls, "tool_events": env.events, "committed": env.committed, "truncated": truncated,
            "n_invalid_args": n_invalid}


def cmd_loop(a: argparse.Namespace) -> None:
    tools_by_phase = json.loads(TOOL_SCHEMAS.read_text())
    eps = select_episodes(a.episodes)
    guard = bg.BudgetGuard(run_id=a.run_id, task_id="INF-001",
                           max_calls=a.max_calls or a.episodes * 3 * (1 + bg.GuardPolicy().max_retries),
                           purpose="benchmark:tool_loop")
    if a.backend == bg.BACKEND_OPENROUTER:
        _openrouter_pricing_check(guard, a.model)
        allowed = guard.apply_openrouter_key_status(_openrouter_key_status("pre_" + a.run_id), reserve=a.or_reserve)
        print(f"OpenRouter attempts allowed now: {allowed}", flush=True)
    client = bg.GuardedChatClient(guard, backend=a.backend, model=a.model, base_url=a.base_url,
                                  request_timeout=a.timeout, meta={"bench": a.run_id})
    params: Dict[str, Any] = {"model": a.model, "max_tokens": a.max_tokens, "temperature": a.temperature}
    if a.seed is not None:
        params["seed"] = a.seed
    if a.reasoning_effort:
        params["reasoning_effort"] = a.reasoning_effort
    out_path = RAW / f"{a.run_id}.jsonl"
    results = []
    with open(out_path, "a") as fh:
        for i, ep in enumerate(eps):
            r = asyncio.run(run_episode(client, ep, tools_by_phase, params))
            r["episode"] = i
            r["model"] = a.model
            r["backend"] = a.backend
            r["params"] = {k: v for k, v in params.items()}
            fh.write(json.dumps(r) + "\n")
            fh.flush()
            results.append(r)
            print(f"[{i}] {r['phase']:9s} pass={r['passed']} calls={r['n_calls']} wall={r['wall_s']}s err={r['error']}", flush=True)
            if a.backend == bg.BACKEND_OPENROUTER and r["error"]:
                break
    guard.close(f"episodes={len(results)}")
    summarize(results, a.run_id)


def summarize(results: List[Dict[str, Any]], run_id: str) -> Dict[str, Any]:
    calls = [c for r in results for c in r["calls"]]
    lat = sorted(c["latency_s"] for c in calls)
    comp = [((c.get("usage") or {}).get("completion_tokens") or 0, c["latency_s"]) for c in calls]

    def q(p):
        return lat[min(len(lat) - 1, int(round(p * (len(lat) - 1))))] if lat else None

    s = {
        "run_id": run_id, "episodes": len(results), "passed": sum(r["passed"] for r in results),
        "pass_rate": round(sum(r["passed"] for r in results) / len(results), 3) if results else None,
        "calls": len(calls), "calls_with_tool_calls": sum(c["n_tool_calls"] > 0 for c in calls),
        "json_invalid_args": sum(c["json_invalid"] for c in calls), "schema_invalid_args": sum(c["schema_invalid"] for c in calls),
        "empty_responses": sum(bool(c["empty"]) for c in calls), "truncated_calls": sum(c["finish_reason"] == "length" for c in calls),
        "episode_errors": sum(r["error"] is not None for r in results),
        "tool_env_errors": sum(1 for r in results for e in r["tool_events"] if e["error"]),
        "latency_p50_s": q(0.5), "latency_p95_s": q(0.95), "latency_mean_s": round(statistics.mean(lat), 3) if lat else None,
        "completion_tok_per_s_aggregate": round(sum(t for t, _ in comp) / sum(l for _, l in comp), 2) if comp and sum(l for _, l in comp) else None,
        "prompt_tokens_max": max(((c.get("usage") or {}).get("prompt_tokens") or 0) for c in calls) if calls else None,
        "mean_calls_per_episode": round(len(calls) / len(results), 2) if results else None,
        "mean_episode_wall_s": round(statistics.mean(r["wall_s"] for r in results), 2) if results else None,
        "by_phase": {ph: {"n": sum(r["phase"] == ph for r in results), "passed": sum(r["passed"] for r in results if r["phase"] == ph)}
                     for ph in ("planning", "execution")},
    }
    (RAW / f"{run_id}.summary.json").write_text(json.dumps(s, indent=1))
    print(json.dumps(s, indent=1))
    return s


def _openrouter_pricing_check(guard: bg.BudgetGuard, model: str) -> None:
    import urllib.request
    with urllib.request.urlopen(f"{bg.OPENROUTER_BASE_URL}/models", timeout=30) as r:
        cat = json.loads(r.read())
    m = next((x for x in cat.get("data", []) if x.get("id") == model), None)
    if m is None:
        raise bg.BudgetViolation(f"{model} not in public catalog")
    (RAW / "openrouter_model_catalog_entry.json").write_text(json.dumps(m, indent=1))
    guard.record_openrouter_pricing(model, m.get("pricing") or {}, source="GET /api/v1/models (public)")


def _openrouter_key_status(tag: str) -> Dict[str, Any]:
    """GET /api/v1/key (account limits, not inference). Saves a redacted copy; returns ``data``."""
    import urllib.request
    req = urllib.request.Request(f"{bg.OPENROUTER_BASE_URL}/key",
                                 headers={"Authorization": "Bearer " + bg.api_key_for(bg.BACKEND_OPENROUTER)})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read()).get("data", {})
    red = {k: ("[redacted-local-only]" if k in ("creator_user_id", "workspace_id", "organization_id", "label") else v)
           for k, v in data.items()}
    (RAW / f"openrouter_key_status_{tag}.json").write_text(json.dumps(red, indent=1))
    bg.Ledger().append({"schema": bg.LEDGER_SCHEMA, "ts_utc": bg._iso(), "task": "INF-001", "event": "account_check",
                        "backend": bg.BACKEND_OPENROUTER, "action": "GET /api/v1/key (limits; not inference)",
                        "api_cost_usd": 0, "new_out_of_pocket_usd": 0,
                        "evidence": {"usage": data.get("usage"), "is_free_tier": data.get("is_free_tier"),
                                     "free_model_daily_requests": data.get("free_model_daily_requests")}})
    return data


def _native_chat(guard: bg.BudgetGuard, model: str, messages, options: Dict[str, Any], think: Optional[bool]) -> Dict[str, Any]:
    """Native Ollama /api/chat (for eval_duration timings and option control), guarded + logged."""
    import urllib.request
    payload: Dict[str, Any] = {"model": model, "messages": messages, "stream": False, "options": options}
    if think is not None:
        payload["think"] = think
    att = guard.begin(bg.BACKEND_OLLAMA, model, LOCAL_URL, payload, meta={"api": "native /api/chat"})
    try:
        req = urllib.request.Request("http://127.0.0.1:11434/api/chat", data=json.dumps(payload).encode(),
                                     headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=600) as r:
            data = json.loads(r.read())
    except Exception as exc:
        guard.end(att, status="transport_error", error=str(exc))
        raise
    guard.end(att, status="ok", http_status=200, response={"model": data.get("model"), "choices": [{"finish_reason": data.get("done_reason")}],
                                                          "usage": {"prompt_tokens": data.get("prompt_eval_count"), "completion_tokens": data.get("eval_count")}})
    return data


def cmd_speed(a: argparse.Namespace) -> None:
    guard = bg.BudgetGuard(run_id=a.run_id, task_id="INF-001", max_calls=6, purpose="benchmark:speed")
    ep = [x for x in load_prompts() if x["phase"] == "execution"][-1]  # longest pilot prompt
    msgs = [{"role": "system", "content": ep["system_prompt"]}, {"role": "user", "content": ep["user_prompt"]}]
    rows = []
    for think in (None, False):
        d = _native_chat(guard, a.model, msgs, {"temperature": 0.7, "num_predict": 400, "seed": 1}, think)
        rows.append({"think": think, "prompt_eval_count": d.get("prompt_eval_count"), "eval_count": d.get("eval_count"),
                     "prefill_tok_s": round(d["prompt_eval_count"] / (d["prompt_eval_duration"] / 1e9), 1) if d.get("prompt_eval_duration") else None,
                     "decode_tok_s": round(d["eval_count"] / (d["eval_duration"] / 1e9), 1) if d.get("eval_duration") else None,
                     "load_s": round(d.get("load_duration", 0) / 1e9, 2), "total_s": round(d.get("total_duration", 0) / 1e9, 2),
                     "thinking_chars": len((d.get("message") or {}).get("thinking") or ""), "done_reason": d.get("done_reason")})
    guard.close("speed")
    (RAW / f"{a.run_id}.json").write_text(json.dumps(rows, indent=1))
    print(json.dumps(rows, indent=1))


def cmd_determinism(a: argparse.Namespace) -> None:
    """Repeat identical requests; compare outputs byte-for-byte (content + tool calls)."""
    tools_by_phase = json.loads(TOOL_SCHEMAS.read_text())
    guard = bg.BudgetGuard(run_id=a.run_id, task_id="INF-001", max_calls=40, purpose="benchmark:determinism")
    client = bg.GuardedChatClient(guard, backend=bg.BACKEND_OLLAMA, model=a.model, base_url=LOCAL_URL,
                                  request_timeout=a.timeout, meta={"bench": a.run_id})
    prompts = {"planning_r2": [x for x in load_prompts() if x["phase"] == "planning" and x["round"] == 2][0],
               "execution": [x for x in load_prompts() if x["phase"] == "execution"][0]}
    conds = [("t0_seed42", {"temperature": 0, "seed": 42}), ("t0.7_seed42", {"temperature": 0.7, "seed": 42}),
             ("t0_noseed", {"temperature": 0}), ("t0.7_seed43", {"temperature": 0.7, "seed": 43})]
    reps = {"t0_seed42": a.reps, "t0.7_seed42": a.reps, "t0_noseed": 2, "t0.7_seed43": 1}
    out = []
    for pname, pr in prompts.items():
        msgs = client.init_context(pr["system_prompt"], pr["user_prompt"])
        for cname, cp in conds:
            for rep in range(reps[cname]):
                params = {"model": a.model, "max_tokens": a.max_tokens, "tools": tools_by_phase[pr["phase"]], **cp}
                if a.reasoning_effort:
                    params["reasoning_effort"] = a.reasoning_effort
                resp, text = client.generate_response(list(msgs), params)
                msg = resp["choices"][0]["message"]
                canon = json.dumps({"content": msg.get("content"), "tool_calls": [c.get("function") for c in (msg.get("tool_calls") or [])]}, sort_keys=True)
                out.append({"prompt": pname, "cond": cname, "rep": rep, "sha": bg.hashlib.sha256(canon.encode()).hexdigest()[:16],
                            "completion_tokens": resp["usage"].get("completion_tokens"), "canon": canon[:600]})
                print(pname, cname, rep, out[-1]["sha"], flush=True)
    guard.close("determinism")
    summary = {}
    for pname in prompts:
        for cname, _ in conds:
            shas = [o["sha"] for o in out if o["prompt"] == pname and o["cond"] == cname]
            summary[f"{pname}/{cname}"] = {"n": len(shas), "distinct": len(set(shas))}
    s42 = {p: {o["sha"] for o in out if o["prompt"] == p and o["cond"] == "t0.7_seed42"} for p in prompts}
    s43 = {p: {o["sha"] for o in out if o["prompt"] == p and o["cond"] == "t0.7_seed43"} for p in prompts}
    summary["seed42_vs_seed43_differ"] = {p: s42[p].isdisjoint(s43[p]) for p in prompts}
    (RAW / f"{a.run_id}.jsonl").write_text("\n".join(json.dumps(o) for o in out) + "\n")
    (RAW / f"{a.run_id}.summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1))


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("loop", "speed", "determinism"):
        s = sub.add_parser(name)
        s.add_argument("--model", required=True)
        s.add_argument("--run-id", required=True)
        s.add_argument("--timeout", type=float, default=600)
        s.add_argument("--max-tokens", type=int, default=1500)
        s.add_argument("--reasoning-effort", default=None)
        if name == "loop":
            s.add_argument("--backend", default=bg.BACKEND_OLLAMA)
            s.add_argument("--base-url", default=LOCAL_URL)
            s.add_argument("--episodes", type=int, default=8)
            s.add_argument("--temperature", type=float, default=0.7)
            s.add_argument("--seed", type=int, default=None)
            s.add_argument("--or-reserve", type=int, default=5, help="OpenRouter daily requests to leave unused")
            s.add_argument("--max-calls", type=int, default=None, help="explicit per-run attempt cap")
        if name == "determinism":
            s.add_argument("--reps", type=int, default=3)
    a = ap.parse_args()
    if getattr(a, "episodes", 0) > 20:
        raise SystemExit("INF-001 benchmark is capped at 20 episodes per invocation")
    {"loop": cmd_loop, "speed": cmd_speed, "determinism": cmd_determinism}[a.cmd](a)


if __name__ == "__main__":
    main()

"""Run the unmodified starter Colosseum runner with every model call routed through BudgetGuard.

Run with the Colosseum venv from the colosseum directory (so ``experiments.*`` imports resolve)::

  cd starter/collusion_hackathon/colosseum
  env -i PATH=/usr/bin:/bin HOME=$HOME LLM_BASE_URL=http://127.0.0.1:11434/v1 LLM_API_KEY=ollama \
      PYTHONPATH=<repo root> .venv/bin/python -m ccc.infra.e2e_colosseum_guarded --config <yaml> --max-calls 60

The starter's provider hook ``experiments.common.providers.make_openrouter_client`` is replaced by a
factory that returns :class:`GuardedChatClient` for the pinned local model. Nothing in the starter
checkout is modified on disk.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys

from ccc.infra import budget_guard as bg


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--max-calls", type=int, required=True)
    ap.add_argument("--backend", default=bg.BACKEND_OLLAMA)
    ap.add_argument("--base-url", default="http://127.0.0.1:11434/v1")
    ap.add_argument("--run-id", required=True)
    a = ap.parse_args()
    if a.backend != bg.BACKEND_OLLAMA:
        raise SystemExit("e2e harness is local-only in INF-001")
    if os.environ.get("LLM_BASE_URL") != a.base_url:
        raise SystemExit("set LLM_BASE_URL to the local endpoint so the starter never routes to a provider")
    os.environ.pop("OPENROUTER_API_KEY", None)

    import yaml
    from experiments.common import providers
    from experiments.collusion import run as crun

    cfg = yaml.safe_load(open(a.config))
    models = {m["llm"]["openrouter"]["model"] for m in cfg["llm_models"]}
    if len(models) != 1:
        raise SystemExit("exactly one pinned model expected")
    model = models.pop()
    guard = bg.BudgetGuard(run_id=a.run_id, task_id="INF-001", max_calls=a.max_calls, purpose="benchmark:e2e_colosseum")

    def factory(llm_cfg):
        m = providers.openrouter_block(llm_cfg).get("model")
        return bg.GuardedChatClient(guard, backend=a.backend, model=m, base_url=a.base_url,
                                    request_timeout=600, meta={"bench": a.run_id})

    providers.make_openrouter_client = factory
    providers.resolve_model = lambda requested, translate_openrouter=True: requested  # exact pin, no catalog lookups
    crun.get_model_name = lambda provider, llm_cfg: providers.openrouter_block(llm_cfg).get("model")
    try:
        out = asyncio.run(crun.run_from_config(a.config, out_dir=None, max_concurrent_runs=1, yes=True))
        print(f"Wrote results to: {out}")
    finally:
        guard.close("e2e done")
    print(f"guarded calls started: {guard.calls_started}", file=sys.stderr)


if __name__ == "__main__":
    main()

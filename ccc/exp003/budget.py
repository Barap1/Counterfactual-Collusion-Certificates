"""EXP-003 Modal spend accounting (append-only, estimates carry a 20% safety margin).

Rates are Modal list prices from `modal billing rates` (CLI 1.6.2, fetched 2026-10-24); container cost =
GPU + CPU cores + memory. Rows go to ops/budget_ledger.jsonl through the guard's own Ledger class.
"""
from __future__ import annotations

import json
import subprocess
from decimal import Decimal
from typing import Optional

from ccc.infra.budget_guard import BACKEND_MODAL, DEFAULT_LEDGER, LEDGER_SCHEMA, Ledger, _iso

TASK = "EXP-003"
MARGIN = 1.20
RATE_SOURCE = "modal billing rates (modal CLI 1.6.2, 2026-10-24)"
GPU_USD_PER_H = {"T4": 0.59, "L4": 0.80, "A10G": 1.10, "A10": 1.10, "L40S": 1.95, "A100-40GB": 2.10, "A100": 2.10,
                 "A100-80GB": 2.50, "H100": 3.95, "H200": 4.54}
CPU_USD_PER_CORE_H = 0.0473
MEM_USD_PER_GIB_H = 0.008
VOLUME_USD_PER_GIB_MONTH = 0.09


def container_rate(gpu: Optional[str], cpu: float = 4.0, mem_gib: float = 16.0) -> float:
    g = GPU_USD_PER_H[gpu] if gpu else 0.0
    return round(g + cpu * CPU_USD_PER_CORE_H + mem_gib * MEM_USD_PER_GIB_H, 4)


def ledger(path=DEFAULT_LEDGER) -> Ledger:
    return Ledger(path)


def total_estimated(path=DEFAULT_LEDGER) -> float:
    return round(sum(float(r.get("estimated_usd", 0) or 0) for r in ledger(path).records()
                     if r.get("event") == "modal_run" and r.get("task") == TASK), 4)


def append_run(seconds: float, gpu: Optional[str], *, label: str, cpu: float = 4.0, mem_gib: float = 16.0,
               path=DEFAULT_LEDGER, note: str = "") -> dict:
    """Append one `modal_run` row; estimated_usd already includes the safety margin."""
    rate = container_rate(gpu, cpu, mem_gib)
    est = round(seconds / 3600.0 * rate * MARGIN, 4)
    prior = total_estimated(path)
    row = {"schema": LEDGER_SCHEMA, "ts_utc": _iso(), "task": TASK, "event": "modal_run", "backend": BACKEND_MODAL,
           "label": label, "gpu": gpu or "cpu-only", "seconds": round(seconds, 1), "rate_usd_per_h": rate,
           "rate_source": RATE_SOURCE, "safety_margin": MARGIN, "estimated_usd": est,
           "cumulative_estimated_usd": round(prior + est, 4), "note": note}
    ledger(path).append(row)
    return row


def metered_usd() -> Optional[float]:
    """Modal's own metered cost for the month (lags; cross-check only)."""
    try:
        out = subprocess.run(["modal", "billing", "summary", "--json"], capture_output=True, text=True, timeout=60)
        return float(Decimal(json.loads(out.stdout)["metered_cost"]))
    except Exception:
        return None


def record_billing_snapshot(path=DEFAULT_LEDGER) -> float:
    """Write the `modal_billing` row BudgetGuard requires. Gross = max(our margin-inflated estimate, Modal metered)."""
    est, met = total_estimated(path), metered_usd()
    gross = max(est, met or 0.0)
    ledger(path).append({"schema": LEDGER_SCHEMA, "ts_utc": _iso(), "task": TASK, "event": "modal_billing",
                         "backend": BACKEND_MODAL, "modal_gross_usage_usd": gross,
                         "source": "exp003 max(estimated incl. 20% margin, modal billing summary metered_cost)",
                         "estimated_usd": est, "metered_usd": met, "verified": met is not None})
    return gross

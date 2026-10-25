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
    return round(exposure(path), 4)


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

# Absolute project constants; callers cannot raise these through configuration.
OPERATING_STOP = 45.0
TOTAL_CAP = 51.0
HARD_STOP_EPOCH = 1792918800.0  # 2026-10-25 09:00:00 UTC
SHUTDOWN_SECONDS = 120.0
TICK_SECONDS = 1.0


def session_rows(path=DEFAULT_LEDGER):
    latest = {}
    for r in ledger(path).records():
        if r.get('task') == TASK and r.get('event') == 'modal_session':
            latest[r['session_id']] = r
    return latest


def exposure(path=DEFAULT_LEDGER, *, now=None, reserved=True):
    """Legacy finalized costs + latest session liabilities, never summing timer updates."""
    import time
    now = time.time() if now is None else now
    rows = ledger(path).records()
    old = sum(float(r.get('estimated_usd', 0) or 0) for r in rows
              if r.get('task') == TASK and r.get('event') in ('modal_run', 'modal_storage'))
    for r in session_rows(path).values():
        if r['state'] == 'closed':
            old += r['estimated_usd']
        else:
            accrued = max(0, now-r['started_epoch']) * r['rate_with_margin'] / 3600
            old += max(r['reserved_usd'], accrued) if reserved else accrued
    return old


def session_event(row, path=DEFAULT_LEDGER, **updates):
    row = dict(row, **updates, schema=LEDGER_SCHEMA, ts_utc=_iso(), task=TASK,
               backend=BACKEND_MODAL, event='modal_session')
    ledger(path).append(row)
    return row


def reserve_session(seconds, gpu, *, cpu=4, mem_gib=16, storage_usd=0, path=DEFAULT_LEDGER, now=None,
                    minimum_seconds=0, minimum_usd=0, reconciled_prior_usd=0, binding=None):
    """Atomically reserve startup, entire active lifetime and shutdown before spawning.

    An unverified/stale reservation blocks subsequent launches until reconciled.
    Storage is a conservative cumulative external liability supplied by ORCH.
    """
    import fcntl, math, time, uuid
    from pathlib import Path
    now = time.time() if now is None else now
    if any(not math.isfinite(x) or x < 0 for x in (seconds, storage_usd, cpu, mem_gib, minimum_seconds, minimum_usd, reconciled_prior_usd)) or seconds <= 0:
        raise ValueError('finite positive lifetime and nonnegative resource liabilities required')
    rate = container_rate(gpu, cpu, mem_gib) * MARGIN
    end = min(now + seconds, HARD_STOP_EPOCH - SHUTDOWN_SECONDS)
    if end <= now:
        raise ValueError('absolute deadline reached')
    if end-now < minimum_seconds:
        raise ValueError('reserved lifetime cannot cover projected block including startup')
    reserved = max(minimum_usd, (end-now+SHUTDOWN_SECONDS) * rate / 3600)
    with Path(str(path)+'.admission.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        active = [r for r in session_rows(path).values() if r['state'] != 'closed']
        if active:
            raise ValueError('active/unverified session liability; reconcile teardown before launch')
        recorded = exposure(path, now=now)
        prior = max(recorded, reconciled_prior_usd)
        projected = prior + storage_usd + reserved
        if projected >= TOTAL_CAP or projected >= OPERATING_STOP:
            raise ValueError('projected liability reaches $45 operating stop or $51 total cap')
        if prior > recorded:
            ledger(path).append(dict(schema=LEDGER_SCHEMA, ts_utc=_iso(), task=TASK, backend=BACKEND_MODAL,
                                     event='modal_run', label='reconciled-prior-adjustment', estimated_usd=prior-recorded))
        if storage_usd:
            ledger(path).append(dict(schema=LEDGER_SCHEMA, ts_utc=_iso(), task=TASK, backend=BACKEND_MODAL,
                                     event='modal_storage', estimated_usd=storage_usd))
        return session_event(dict(session_id=uuid.uuid4().hex, state='reserved', started_epoch=now,
                                  deadline_epoch=end, rate_with_margin=rate, reserved_usd=reserved,
                                  estimated_usd=0, gpu=gpu, cpu=cpu, mem_gib=mem_gib,
                                  safety_margin=MARGIN, **(binding or {})), path)


def tick_session(row, *, path=DEFAULT_LEDGER, now=None):
    import time
    now = time.time() if now is None else now
    actual = exposure(path, now=now, reserved=False)
    tail = SHUTDOWN_SECONDS * row['rate_with_margin'] / 3600
    reason = ('total_cap' if actual + tail >= TOTAL_CAP else
              'operating_stop' if actual + tail >= OPERATING_STOP else
              'deadline' if now >= min(row['deadline_epoch'], HARD_STOP_EPOCH-SHUTDOWN_SECONDS) else None)
    updated = session_event(row, path, state='stopping' if reason else 'active',
                            seconds=max(0, now-row['started_epoch']),
                            estimated_usd=max(0, now-row['started_epoch'])*row['rate_with_margin']/3600,
                            cumulative_estimated_usd=actual, stop_reason=reason)
    return updated, reason


def close_session(row, verified, *, path=DEFAULT_LEDGER, now=None):
    import time
    now = time.time() if now is None else now
    return session_event(row, path, state='closed' if verified else 'teardown_unverified',
                         teardown_verified=verified, seconds=max(0, now-row['started_epoch']),
                         estimated_usd=max(0, now-row['started_epoch'])*row['rate_with_margin']/3600)

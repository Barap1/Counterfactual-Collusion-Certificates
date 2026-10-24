# VIS-001c handoff

- Task: Regenerate DEV figures from Gate A v1.2.2 and add CCC/oracle comparison.
- Status: Complete. Figures use only the specified DEV source; no held-out outcomes accessed.
- Artifacts: `figures/fig_gateA_integrity.{pdf,svg,json}`, `figures/fig_confusion_dev.{pdf,svg,json}`, `figures/fig_supported_vs_oracle.{pdf,svg,json}`, refreshed `figures/fig_arms.{pdf,svg,json}`, and builder `figures/scripts/build_publication.py`.
- Validation: Ran `nice -n 19 starter/collusion_hackathon/colosseum/.venv/bin/python figures/scripts/build_publication.py`; rendered PDFs with `sips` to `/tmp/ccc_figqa`; visually inspected for clipping/overlap. Sidecars contain source paths and SHA-256. Oracle figure: 440 non-A6 cells, 0 false supports, 0 false exonerations, 134 inconclusive abstentions including 20 oracle-positive; reason codes shown.
- Limitations: DEV fixtures only; no real experiment claims. `figures/make_results.py` remains a template.
- Budget: $0; no live model or network calls.
- Next: None.

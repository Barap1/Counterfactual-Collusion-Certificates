# VIS-001c handoff

- Task: Correct `fig_supported_vs_oracle` terminology and make its oracle-positive abstention panel match its title.
- Status: Complete. The left panel distinguishes support from “not supported” and uses the inclusive oracle margin `τO ≥ mO`; not supported is explicitly not exoneration. The right panel selects exactly the 20 non-A6 inconclusive cells with `τO ≥ mO` and `path_active=true`, assigning each one primary reason: mutual disruption 14, efficient transfer 4, redundant non-identifiability 2. Two cells carry both redundant non-identifiability and mutual disruption; reasons may co-occur. All non-A6 abstentions are separately noted as n=134.
- Artifacts: Updated `figures/scripts/build_publication.py`, `figures/fig_supported_vs_oracle.{pdf,svg,json}`. Source SHA-256 remains `8aa6b1b0b979406dc523f931e1451e75304a599f7f6379f7c6985bcd4a60e54c`.
- Validation: Counts recalculated from `docs/gate_a/v1.2/correction_v1.2.2/gate_a_results.json.gz`; 440 non-A6 cells = 8 correct support + 0 false support + 298 not supported below margin + 0 not supported above margin + 134 abstentions. Rendered PDF to `/tmp/ccc_figqa/fig_supported_vs_oracle.png` and visually inspected. Build command: `nice -n 19 starter/collusion_hackathon/colosseum/.venv/bin/python figures/scripts/build_publication.py` (`nice` priority change was denied by the environment; generation completed).
- Limitations: DEV fixtures only; no real experiment claims. No network or model calls.
- Budget: $0.
- Next: None.

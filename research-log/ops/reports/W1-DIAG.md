## Task
Diagnose frozen Modal CPU eps-0.1 divergence using three sequential local seed reruns under PYTHONHASHSEED=0 and 1.

## Status
**Outcome (ii): container environment.** Seeds **1016969, 2054967, 2137797** were selected from GATE.json mismatches. For every seed, both local eps-0.1 unit files equal each other and the serial reference; both differ from the container file. This holds for decompressed bytes and parsed JSON. No outcome values inspected or reported.

## Artifacts
Scratch root: `/private/tmp/claude-501/-Users-aarav-Documents-Projects-ApartSprint/3ccbb60e-bc6f-4ccf-9855-31894d86ff91/scratchpad/diag/W1-DIAG/`.
Contains `comparison.json`, `identity-hash-{0,1}.json`, `container-runtime.json`, `hash-{0,1}.log`, reruns in `hash-{0,1}/<seed>/`, and scripts `rerun.py`, `compare.py`, `extract_runtime.py`. `commands.sh` records reproduction commands using the requested venv interpreter, offline guard, repo root, numpy path, and single-thread numerical libraries. Hash passes were launched separately, sequentially.

## Validation
All nine selected eps-0 unit / eps-0 and eps-0.1 partition comparisons agree across both reruns, serial, and container. Frozen source hashes and freeze hash match GATE identity. Selected reference checksums remain unchanged throughout both passes. No benchmark code or protected output was written. Registry checked; W1-DIAG absent; direct user assignment defines ownership.

## Limitations
Three seeds only. Local Python **3.14.7** (conda-forge/Clang); container receipts show **3.14.2** (GCC). Both use NumPy **2.2.6**. Environment attribution follows the requested decision rule; Python patch version versus other platform differences was not isolated.

## Budget
$0; Codex (GPT-6 family), no experimental model/API calls, network, Modal, git, pools, or secrets. Six seed executions: **443.75 seconds** combined; within 45 minutes.

## Next
Use a **version match**: require container Python **3.14.7** exactly and NumPy **2.2.6** for the next gate; validate the full patch version. PYTHONHASHSEED pinning is unsupported as the remedy by these checks. Gate execution remains with the authorized controller.

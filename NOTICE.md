# Third-party notice

The MIT license in `LICENSE` covers the original CCC code and documentation in this repository.
It does not grant rights in third-party material:

- **Colosseum / collusion_hackathon starter, poseidon-compute, CoLLAB** (poseidon-research/collusion_hackathon at
  commit d585a7b3): no license file was found upstream. None of their source is tracked here (`starter/` is
  gitignored). Parts of `ccc/replay/world.py` mirror upstream behaviour and `patches/ENG-003_optional_registry.patch`
  contains a few upstream lines; scenario text and agent traces in the archives were generated in that environment.
  These remain subject to the upstream authors' terms.
- **terrarium-agents 0.1.1** (Mason Nakamura): MIT; not vendored.
- **gemma4:26b** (Google, via Ollama): model weights are not distributed; archived outputs were produced with it.
- Python dependencies (numpy, scipy, etc.) are installed separately under their own licenses; see
  `docs/release/LICENSES.md`.

Source: release audit `docs/enh/sec/SEC-001_audit.md` (2026-10-24).

- **Old Standard TT**: three unmodified font faces are bundled in `paper/v2/fonts/` for the official template typography under SIL Open Font License 1.1. The copyright and full license are retained in `paper/v2/fonts/OFL.txt`; source URLs and SHA-256 values are in `ops/reports/final_audit/paper/font_sources.json`. CCC MIT does not cover those font files.

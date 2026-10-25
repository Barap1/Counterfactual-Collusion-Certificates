# Reproducing CCC

## Public checkout: no dependencies or network

Use Python 3.12+ from the repository root:

```sh
python3 scripts/reproduce_headline.py
python3 -m unittest discover -s review/reproduce_headline/tests -v
python3 -m unittest tests.test_demo_data -v
python3 scripts/check_artifact.py
```

The headline script verifies SHA-256 `83bf451dad54c773afbc3e775acc13e08bd97fbe92dee4d1a21307cc60625831` before safe extraction to a temporary directory. It recomputes eight pair contrasts and the exact 18/256 sign-flip p-value from recorded rewards. Expected estimate: `1.354325711018899`; exact p: `0.0703125`. Its independent implementation is [`review/reproduce_headline/independent.py`](../review/reproduce_headline/independent.py). No runner or inference transport is invoked.

The independent arithmetic tests check corrupted inputs, rewards and attempt accounting. Eight explorer tests verify frozen estimates/certificates, case coverage, transcript samples and complete data-pack hashes. `check_artifact.py` checks public navigation and SVG structure. CI runs these public-file checks with read-only repository permissions. They are not the complete implementation suite.

The quickstart does not recompute the world-cluster bootstrap interval. Its [independent verification receipt](../ops/reports/final_audit/tests/independent_bootstrap.json) and [verifier source](../ops/reports/final_audit/verify_bootstrap.py) are retained; numerical execution requires NumPy.

## Offline explorer

Open [`../demo/explorer/index.html`](../demo/explorer/index.html) locally, including from a `file://` URL. Use **Twin worlds → P2** (allocation), compare I2/I4, then **Study**. All scripts and data are local. No server or package installation is required.

To rebuild derived bundles from retained sources, in order:

```sh
python3 demo/build_twins.py
python3 demo/build_data.py
python3 demo/explorer/bundle_data.py
```

These scripts derive presentation data; they do not run experiments. The manifest authenticates input and generator hashes. Rebuilding changes generation metadata. Do not hand-edit the JSON or JavaScript bundles. [Explorer documentation](../demo/explorer/README.md).

## Complete implementation suite: existing environment required

The replay integration requires the excluded upstream `poseidon-research/collusion_hackathon` starter at commit `d585a7b3be50366cc2bdf5789bf8add5890b2abd`, including `colosseum/`, `util/` and `colosseum/external/CoLLAB`. Historical Cloud Agent setup uses Python 3.12 with its locked environment; the local audit environment uses Python 3.14.7, NumPy 2.2.6 and SciPy 1.17.0. See the [recorded environment](release/environment.json) and [license inventory](release/LICENSES.md). A fresh external installation has not been verified. Do not source credential files or run live preflight to perform offline analysis.

With that environment already available and pytest installed, run its Python interpreter on:

```sh
python scripts/test_offline.py -q tests
```

The guarded runner sets `CCC_STARTER_ROOT`, disables pytest plugin autoload and blocks network and secret-file access. Use the upstream virtualenv interpreter, or set `CCC_STARTER_ROOT` to an equivalent pinned checkout. The historical held-out-manifest test is skipped under the offline guard; three additional skips concern unresolved specification syntax. Test counts measure software checks, not collusion-detection reliability.

**Pilot limitation:** only nine of 27 files in `ops/pilot_manifest.sha256` are tracked. The missing 18 traces cannot be recovered by copying the public archive subset. Three legacy adapter checks therefore error in a fresh public checkout. The full local suite was checked with the complete pre-existing archive; that is not a clean-checkout reproduction claim. Keep local-only inputs excluded pending privacy/rights decisions.

PR #1 supplied useful Cloud Agent setup notes and identified this missing-input limitation. Its substantive instructions are consolidated here rather than leaving a competing environment guide in `AGENTS.md`.

## Legacy full development analysis

[`scripts/reproduce_offline.sh`](../scripts/reproduce_offline.sh) is a **zsh-specific** entry point for an existing starter environment. It runs unittest discovery and development analysis, not the complete pytest suite or a fresh real-agent experiment. Its copy/restore assumptions require complete local pilot inputs. It is not the primary quickstart. The driver can be inspected at [`scripts/reproduce_offline.py`](../scripts/reproduce_offline.py).

Frozen results, preregistration and corrections are indexed in [the evidence guide](README.md). No command on this page invokes models or cloud experiments.

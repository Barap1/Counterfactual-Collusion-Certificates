# Explorer numeric trace

All field paths below are relative to the named raw source or generated case. JSON
numbers are copied without rounding. UI formatting must not replace stored values.
Every case has sources with SHA256; archive members use docs/runner/<member> paths.
The manifest binds every generated file except itself, and every source actually used.

| Displayed number type / pack field | Exact source field / derivation | Evidence category |
|---|---|---|
| study.primary.result estimate, L, U, p_raw, n_independent, matched_pairs_attempted, eligible_complete_pairs | exp002_heldout_v3/effects_study.json[effect=Delta_total], identical full row | original-confirmatory |
| study.noncommit_sensitivity.result estimate, L, U, n_independent | exp002_heldout_v3/sensitivity.json[analysis=noncommit_excluded], identical full row; task-requested category, original label retained | original-registered-secondary (source descriptive; mission post-hoc) |
| study.per_world[].tau_O_B1 / tau_O_B2 | world_effects.json[world_id,regime].tau_O | original-confirmatory components |
| study.per_world[].d_w | world_effects.json[world_id,B1].tau_O minus [world_id,B2].tau_O | original-confirmatory |
| certificate_counts / scheduled_counts | count checkpoint_certificates.json by status / all streamed branches/*/result.json.data.status (includes not_run) | descriptive |
| Unrun continuation scheduled_records[].rep, attempt_no | scheduled_statuses.json[checkpoint_id,arm,rep]; metrics=null rather than invented zero | descriptive |
| Held-out continuations[].rep, metrics attempt_no, rep, rewards, Omean, Cmean, W, A | continuations.json[checkpoint_id,arm,rep], identical full row | descriptive |
| Held-out committed task IDs and roles | continuations.json[checkpoint_id,arm,rep].committed / .roles; IDs are labels, not measurements | descriptive |
| Held-out certificate tau_O/C/W/A and *_L, *_U, TV*, theta, n_independent, placebo contrasts | checkpoint_certificates.json[checkpoint_id], identical full row, including nulls | descriptive |
| Held-out margins m_O, delta_W / gate_trace margin, delta_W | checkpoint_certificates.json[checkpoint_id].gates.m_O / .delta_W | descriptive |
| Held-out gate_trace L/U and comparisons | certificate tau_*_L/U; O lower > m_O, upper < m_O; C lower > 0 or upper <= 0; W lower >= -delta_W or upper < -delta_W; otherwise ambiguous | descriptive |
| Held-out world_effect tau_*, n_F, n_K | world_effects.json[world_id,regime], identical full row | descriptive |
| validity.canonical_records / regime_batch_records estimates, L/U, confidence endpoints, n_independent, half_width90 | validity_checks.json[checkpoint_id] / [no checkpoint_id, matching regime], identical rows | descriptive |
| validity.raw_counts[].counts pass/fail/na and other statuses (held-out) | checkpoint.json.data.restore_validation plus attempt result.json.data.cross_checks[] plus each branches/*/result.json.data.checks[]; count by id/status, not_applicable => na; no inferred passes | descriptive |
| Held-out arms[arm].recorded_branches / statuses | count streamed branches/*/result.json by arm / status; no record does not imply an executed continuation | descriptive |
| checkpoint_turn, exposure turn/mask fields | checkpoint.json.data.scheduler_cursor / .exposure | descriptive |
| original/continuation turn_index, step, source_record_index | source/records.json or branches/*/records.json .data.records[i].turn_index / step / array index i | descriptive |
| Interaction message/action arguments and tool results (any numeric literals) | records[i].response.choices[].message verbatim; trailing tool messages from records[i].request.messages; original turn_index < checkpoint scheduler_cursor | descriptive |
| Gate A seed, boundary, detector observations, task IDs and embedded numbers | gate_a_results.json.gz rows[case.source_field].seed / native.detector_text_evidence (verbatim in full file) | development |
| Gate A continuation rep | array index in rows[i].native.branch_replicates[arm] | development |
| Gate A agent_rewards, assignment, Omean, Cmean, A, W | rows[i].native.branch_replicates[arm][rep].outcome; null if unavailable | development |
| Gate A certificate estimates, intervals, counts, parameters, placebo effects/p and all other nested numbers | rows[i].native.CCC, identical complete decision | development |
| Gate A oracle_effects / oracle_strata and margins | rows[i].oracle_effects / oracle_strata; m_O from native.CCC.parameters.m_O, delta_W from oracle_strata.reference_delta_W | development |
| Gate A gate_trace L/U, margin, delta_W, pattern comparisons | native.CCC.estimates.intervals.tau_*; same explicit comparisons above; stored pattern_gates also retained | development |
| Gate A validity.raw_counts[].counts | rows[i].native.checks[], grouped by id/status with not_applicable => na | development |
| Source SHA256, archive SHA256 | SHA256 of original file/member bytes; archive checked against exp002-live.tar.gz.sha256 | provenance metadata |
| MANIFEST.files[].bytes / sha256 | byte length / SHA256 of generated artifact (no self-hash) | build metadata |
| twins.json pairs[].members[].by_set[Ix].transcript, arms (n, Cmean, Omean, A, W, rewards, action), placebo, probe, authorization, view_sha256 | <run>/partitions/<seed>-eps-0.json.gz[Ix][view_sha256 match].canonical_view (re-hashed to equal records view_sha256); arms = per-arm means of the stored rows | development (label from twins.json) |
| twins.json members[].truth, by_set[Ix].identifiable, M_multiclass_identifiable | <run>/records.json.gz[seed,kind,member,eps=0,set] truth / identifiable, evaluator-only | development |
| twins.json verdicts (ccc, ccc_l, baseline, bayes) | records.json.gz methods[CCC-v1.2.2 / CCC-L-v0 / strongest of B2+,B3b / Bayes-given-S] status, rung, M_label, predictions | development |
| twins.json first_separating_set, first_divergence | first Ix where the two members' view_sha256 / verdict JSON differ (computed in build_twins.py); enumerated_pair_separator from separators.json | development |
| twins.json strongest_baseline | balanced accuracy of attributable-M at I1 over DEV records, B2+ vs B3b, ties to B2+ (docs/enh/r2/PROTOCOL.md s5) | development |

Gate traces explain recorded outcomes; they do not issue replacement certificates.
Absent fixture transcripts are explicitly unavailable, never synthesized. Exposure
highlight uses the exact original post_message message argument. Full case files
retain untruncated messages/actions/tool results, without duplicating prompts or RNG
state; hashed raw records provide those originals. Compact case files shorten strings
at 900 characters. Independent sample size is eight matched world pairs, not branch
replicates or raw validation check counts.

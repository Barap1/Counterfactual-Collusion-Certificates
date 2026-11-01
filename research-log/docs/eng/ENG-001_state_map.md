# ENG-001: Colosseum/Terrarium state and observation map

Status: complete (inspection of the installed code, confirmed by executable tests in `tests/replay/`).
Scope: the collusion experiment path (`experiments/collusion/run.py`) on `JiraTicketEnvironment`. Other
Colosseum experiments (agent_misalignment, network_influence, persuasion) subclass `BaseAgent` or add
judges. They were not audited and need their own map before use.

## 0. What is installed (pinned)

| Item | Value |
|---|---|
| Upstream checkout | `starter/collusion_hackathon/colosseum`, commit `d585a7b3be50366cc2bdf5789bf8add5890b2abd`, 0 dirty paths |
| Terrarium | `terrarium-agents==0.1.1` (PyPI, in `.venv/lib/python3.14/site-packages/terrarium`) |
| CoLLAB envs / clients | `envs/` and `llm_server/` shipped in the same site-packages; `openai==2.21.0`; Python 3.14.7 |
| Shared compute helper | `poseidon_compute` (editable from `starter/collusion_hackathon/util`) |

Paths below are relative to `colosseum/` (`run.py` = `experiments/collusion/run.py`; `T/` = `.venv/lib/python3.14/site-packages/`).

## 1. Execution path (one run, serial)

```
run.py:_run_single (250)
  rng = random.Random(seed) (266)            # colluder selection (if 'random'), agent shuffle (434)
  protocol = LocalCommunicationProtocol (337) # experiments/common/local_protocol.py: in-process, no MCP server
  env = JiraTicketEnvironment(protocol, cfg)  # T/envs/dcops/jira_ticket/jira_ticket_env.py: env.rng (38), tasks, costs
  env.prompts = CollusionPrompts(...) (390)   # wraps JiraTicketPrompts; coalition text injected via agent_context
  agents = [BaseAgent(client_i, ...)]; rng.shuffle(agents) (434); await env.async_init() (441)
  secret board: protocol.generate_comm_network(colluders, ctx) (454)
  for round in 1..R: for agent in env.agents: protocol.agent_planning_turn (509...)
  for agent in env.agents: protocol.agent_execution_turn (562...)
  env.get_final_summary() (600) -> metrics, JSON artifacts
```

Per turn (`local_protocol.py:286/314`): `_prefetch_blackboard_events` (117) renders **every** board the agent belongs
to, in full, with `T/terrarium/blackboard.py:format_blackboard_events_for_prompt` (442). Then
`BaseAgent.generate_response` (`T/terrarium/agents/base.py:224`) builds system and user prompts and runs
`_multi_step_response_generation` (306):

- `context = client.init_context(system, user)` (335): **a fresh 2-message context every turn**.
- Up to `max_conversation_steps` calls of `client.generate_response(input=context, params)` (via `run_blocking`, thread pool, awaited serially).
- `client.process_tool_calls` (`T/llm_server/clients/together_client.py:202`) appends the assistant message and one `tool` message per call, routed through `BaseAgent._execute_tool_call` (140). Only `post_message` (blackboard) and the env's phase tools (`assign_task` in execution) are routable. `get_blackboard_events` is not advertised and not routable (`toolset_discovery.py:66`).
- The loop ends early once an env tool returns `state_updates` (assign_task).

Scheduler: fixed, serial. R planning rounds × `env.agents` order, then one execution pass. `env.done()` is not consulted.
`max_concurrent_runs` parallelises *runs*, never turns.

## 2. State inventory

| State | Location | Persists across turns? | Snapshot treatment |
|---|---|---|---|
| Blackboards: participants, event logs, template, suspended | `protocol.megaboard.blackboards` (`Megaboard`, `blackboard.py:53`) | yes, append-only | captured (JSON) |
| Event `id` (uuid4) and `ts` (wall clock) | `Megaboard.post` (162-166, 205-209) | yes | replaced by a deterministic logical clock (§6) |
| Assignment (insertion order matters for float sums) | `env.assignment` | yes | captured as ordered pairs |
| `env.rng` | `jira_ticket_env.py:38`; consumed at init and by `_fill_random_unassigned_agents` (482) when `assignment_filling=true` | yes | captured (`getstate`) |
| Score histories | `env.joint_reward_history`, `agent_rewards_history` | yes (unused by collusion run) | captured |
| Tool event log | `protocol.tool_events`, `current_planning_round` | yes (metrics input) | captured |
| Tasks, costs, skills, names, colluders, roles, turn order, boards' membership, prompts, tool schemas, generation params | env / run.py setup | static | rebuilt from spec, **hash-verified** |
| Per-agent conversation history | none: `init_context` per turn | **no** | n/a (no agent memory exists) |
| `BaseAgent.current_*`, `_env_state_committed`, `communication_protocol` | `base.py:55-61` | overwritten before use | not captured (documented) |
| Prompt/blackboard/trajectory loggers | files | side effect only | not captured; redirected to scratch |
| Run-level `rng` | run.py:266 | consumed before turn 0 | recomputed from seed |

There is no hidden memory, summary, or retrieval feature on this path. Everything an agent knows at a turn is in its system and user prompt plus the tool results of that turn.

## 3. What reaches each agent (observation surfaces)

User prompt (`jira_ticket_prompts.py:_get_user_prompt_impl` via `CollusionPrompts.get_user_prompt`):

1. Coalition prefix (colluders only): members, partner, secret `blackboard_id`, variant text.
2. Turn info, private state (availability, top skills), all tasks, the agent's private cost table.
3. `CURRENT ASSIGNMENTS` (`build_agent_context` → `joint_assignment`, jira_ticket_env.py:350). This shows the *actions* of earlier execution-phase agents.
4. `BLACKBOARD COMMUNICATIONS`: the full re-render of every member board at every turn. Communication events show as `[i] agent: content (phase=…, iter=…)`. Other kinds (`action_executed`) show `[i] [kind] agent id=<event id> payload=<json>`.

In-turn tool results: `post_message` returns `{"event_id"}` only. `assign_task` returns the task record, the running `joint_reward`, and counts. Neither echoes board text (asserted per request by check `V-echo`).

## 4. Hook points chosen

All hooks sit in CCC code, as subclasses or wrappers of upstream objects. **No upstream file is edited and no patch is needed**, so `patches/` is intentionally absent. Implementation: `ccc/replay/world.py`, `engine.py`, `interventions.py`.

**(a) Pre-exposure checkpoint.** This is the turn boundary immediately before the receiver's earliest exposure turn `t*`. It is the first turn of receiver `r` whose prefetched view contains event `e`. Exposure can only happen at `_prefetch_blackboard_events` time, because there is no mid-turn read path (§1), so the boundary between turn `t*-1` and `t*` is pre-exposure by construction. `CCCProtocol` logs the visible event ids of every prefetch, and check V06 verifies three things: `e` is absent from all of `r`'s earlier views, the content fingerprint is absent from all of `r`'s earlier *requests*, and `e` is present at `t*`. A checkpoint "immediately before r's tool action" would be too late, since `r` reads the board in the same request in which it acts.

**(b) Receiver mask.** `CCCProtocol._prefetch_blackboard_events` override. A pure hook receives `{bb: Megaboard.get(bb, r)}` and returns the same lists minus the masked ids. For receiver `r` only, the change applies at turns inside the declared horizon (`persistent` = through the end of the episode, or `single` = only at `t*`). The result is rendered with the **upstream** formatter. The Megaboard, other agents' views, the sender's action and its `action_executed` trace are untouched. Removal renumbers later `[i]` lines on that board, and the diff records this as part of the treatment. Check V05 verifies at `t*` that K's prompt equals F's prompt with exactly the masked lines removed. V05b verifies the same at every prompt, and also that non-receivers always see the event.

**(c) Sham.** This uses the same override with the identity transform, i.e. an identity re-render through the intervention path. F uses the untouched upstream method, with no hook installed. V04 checks that the receiver's rendered view and the full first request at `t*` are byte-identical in F, S and the source run. V05b checks at every prompt that S's render equals the upstream render. A content-matched *substitution* would change the delivered bytes. That makes it a different arm (an R/placebo arm in module 04), not S. The engine accepts it through `run_branch(hook=...)` but never labels it S.

**Model-request hook (recorder).** `RecordingClient` wraps each agent's client and records the exact `(messages, params)` passed to `generate_response`, plus the response, id, model and cache mode. It records no headers.

## 5. Every place a copy of a message can reach the receiver

| Path | Present here? | Handling |
|---|---|---|
| Re-render of the same board on every later turn | **yes**, the main path (full log every prefetch) | persistent mask over the horizon; V05b, V07 |
| Sender re-posts or paraphrases on the same board or another shared board | possible (prompt tells agents to "relay … on all blackboards") | V07 content scan of every receiver request (exact / 8-shingle ≥0.5 / raw id). Declared pre-fork copies can be listed in `copy_event_ids`. Otherwise the branch is `invalid`. |
| Third agent quotes or relays it after the fork | possible (complete topology: everyone shares board 0) | V07 → `invalid` under `persistent` |
| `action_executed` payloads (`details` includes running `joint_reward`) | yes, on every non-secret board of the actor | mechanical/action channel, not the message; **not** masked (module 04: do not delete the action) |
| `CURRENT ASSIGNMENTS` | yes, in execution | action channel, not masked |
| Memory / summaries / retrieval | **none** on this path | n/a; leaky-summary mutation test proves V07 would catch one |
| Tool results echoing board text | none today | `V-echo` asserts it on every request |
| Receiver's own earlier posts quoting it | only if already exposed | excluded by V06 |
| Logs (`agent_prompts.*`, `blackboard_*.txt`) | not agent-visible | n/a |

Paraphrase without shared 8-token runs is **not** detected. Absence of the string does not prove absence of the information.

## 6. Inaccessible or unsnapshotable state

- **Provider side:** sampling RNG, KV/prefix caches, load-balancing/routing, and silent model updates behind an alias. None of this can be observed or restored. A replay can only assert the *requested* and *response-reported* model ids (check `V-model`).
- **`TogetherClient` forwards only `model, messages, max_tokens, temperature, reasoning, tools`** (together_client.py:135-155). Any `seed`, `top_p`, etc. in config is silently dropped, so no API seed can be claimed.
- **Global `random`:** used only for retry jitter (together_client.py:189). It affects timing, not content. Not captured.
- **Wall-clock `ts` and uuid4 ids:** not reproducible upstream. Event ids are rendered into prompts for `action_executed` lines, so the CCC world substitutes uuid5 ids from a logical clock. This is a declared deviation, and parity on the archived pilot is otherwise exact.
- **Run-level `rng`:** consumed before turn 0, so it is reconstructible from the seed but never needed after setup.
- **`env.rng`:** fully capturable. With `assignment_filling=true` it injects randomness into final outcomes, so audits should keep `false` (the pilot did). The checkpoint manifest records the value.

## 7. Hazards found during inspection (affect validity, provenance or safety)

1. **Network and credential side effects in setup.** `experiments/common/providers.py:107` monkeypatches `terrarium.utils.extract_model_info` → `get_model_name` → `poseidon_compute.llm_config.resolve_model`. That call loads the repo-root `compute.env`, honours an `LLM_MODEL` override, and fetches the OpenRouter catalog over the network. Upstream reaches it merely to name log directories during env construction. The first offline test attempt observed 136 blocked socket connects. The CCC world scopes a pure replacement (`world.offline_model_info`). *Hypothesis, not verified:* the `LLM_MODEL` override is a plausible cause of the pilot's recorded model `cohere/north-mini-code:free` differing from the requested `Qwen/Qwen2.5-7B-Instruct`.
2. **The secret channel is not scrubbed of action traces.** `_scrub_secret_blackboards` keys on `template.secret_channel`, but run.py creates the coalition board without a template. As a result, colluders' `action_executed` events land on it (visible in the pilot's `blackboards.json`, board 1).
3. **Aliasing.** `log_action_to_blackboards` stores `result.copy()` (shallow, blackboard.py:424). `post_tool_execution_callback` then mutates the nested dict (`joint_reward`, jira_ticket_env.py:584), so the board event, the tool event and the tool message share it. This is safe to break at turn boundaries, because nothing mutates it later. Snapshots break it.
4. **Upstream swallows continuation-step exceptions** (`base.py:388-407`, returns an `[ERROR]` response). A failing step-2+ call silently shortens a turn. CCC surfaces these errors (`world.errors`, `ReplaySource.errors`) and marks the branch `failed`.
5. **Filesystem side effects.** `JiraTicketPrompts.__init__` creates `./logs/...` relative to the **cwd**, and `clear_seed_directories` `rmtree`s `logs/<env>/<model>/seed_N`. CCC builds envs inside a scratch directory with `logging.root_dir` pointed there.
6. **Mask renumbering.** Removing one event shifts later `[i]` indices on that board. This is inherent to removal and recorded in the diff, not hidden.

## 8. Replay strategy decision

The primary strategy is **A (explicit snapshot)**. The causal state is small and plain JSON (§2), agents have no cross-turn memory, and static parts are rebuilt from the spec and hash-checked. Snapshots are taken at every turn boundary of the source run.

**B (prefix reconstruction)** is kept as an independent cross-check. It is also the path for runs recorded without snapshots. Every recorded request is hash-checked in order, the state must equal the snapshot byte-for-byte, and any unexpected or mismatched request stops the replay. B alone was not chosen because it needs every pre-boundary response recorded and re-executes the whole prefix per branch. A alone was not chosen because a forged but internally consistent snapshot would pass A's own hash checks. The test `test_V15_rehashed_but_altered_snapshot…` shows B catching exactly that case.

The archived pilot is reproduced exactly from its recorded tool events: blackboards (minus id/ts) and final rewards (`tests/replay/test_world_parity.py`). This shows the re-implemented turn loop matches `run.py`.

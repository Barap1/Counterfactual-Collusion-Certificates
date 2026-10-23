# 09 - Inference, local compute, and zero-new-spend enforcement

## Separate development agents from experimental agents

Claude Code and Codex are development/review tools under existing subscriptions. Colosseum's experimental agents need a separately identified inference backend. Do not conflate the two or claim a frontier-model experiment because a frontier coding model wrote its code.

Existing subscriptions are finite allowances, not unlimited API credits. Their authenticated runtime and usage limits must be respected. Pause or use another already approved development route when limits are reached; do not automatically switch to pay-as-you-go credentials.

## Backend decision tree

1. **Use the existing Cohere/OpenRouter pilot as a preserved feasibility anchor.** Use additional free calls sparingly for adapter validation or a small corroborating stratum.
2. **Benchmark local inference for bulk collection.** Prefer an already installed tool-capable open model, otherwise one modest, licensed model download. Use native Apple-supported execution rather than assuming Docker provides CUDA/Metal acceleration.
3. **Use explicitly provisioned Modal compute when local throughput or model quality is inadequate**, but only after credit and zero-net-spend checks.
4. **Do not cross into paid API inference without owner approval.** If approved resources cannot support the intended sample, reduce scope and claims transparently.

A backend/model change creates a separate experimental stratum. Do not merge Cohere and a local Qwen-family model under one model name or rerun only failed cases on a stronger model.

## OpenRouter guardrails

The owner has demonstrated tool calling and a complete pilot on `cohere/north-mini-code:free`. Availability, supported parameters, routing, and pricing must be checked at collection time. The free suffix is helpful but not a sufficient perpetual billing guarantee.

The official limits documentation currently describes standard free-model quotas of 50 requests/day for accounts below the relevant purchase threshold and 20 requests/minute; actual key/account status is authoritative. Failed requests can consume quota. Query the documented key/limit endpoint and inspect current response fields rather than infer remaining quota from guesses. [S10](https://openrouter.ai/docs/api_reference/limits)

Use one global request scheduler. Initially allow one in-flight experiment call, bounded retries, and explicit pause on quota exhaustion. Record requests already consumed by setup. Creating more keys/accounts is not an approved limit workaround. Do not let every subagent independently "test the API."

Pin a specific model instead of `openrouter/free`. Record the resolved model/provider and returned usage per call. Check for request, plugin, and auxiliary charges as well as input/output token prices. No paid plugins, automatic web search, or alternative model fallback in experimental requests.

If pricing is unavailable or nonzero, block live execution. If an observed response reports an unexpected positive charge, halt further calls, preserve the evidence, and notify the owner; do not hide the charge by reporting only environment costs.

## Local inference on the owner's Mac

The Mac is a meaningful compute option, not merely a development terminal. A tool-capable quantized model in the approximate 8-14B range is a reasonable first benchmark candidate, not a guaranteed performance claim. Inspect available models and their license, disk size, tool schema support, context limit, and exact weight digest before selecting one.

Ollama provides an OpenAI-compatible interface and tool-calling support for compatible models, but compatibility is not universal. [S12](https://docs.ollama.com/api/openai-compatibility) Use a placeholder local key, not the OpenRouter credential. The familiar local route is `http://127.0.0.1:11434/v1`; verify the actual server before configuring it. Do not accidentally select an Ollama cloud model or other billed route.

Run one inference server initially. Leave substantial memory for macOS, Claude/Codex, and data processing; a conservative starting target is to keep the model workload below about 30-32 GB of the 48 GB machine and adjust using actual memory pressure. This is a project policy, not a model-fit guarantee. Reduce context, batch size, or model size before letting the machine swap heavily.

Benchmark more than tokens per second. Test a complete tool round trip, multiple sequential tool calls, legal JSON arguments, a tool-result response, a realistic Colosseum prompt length, and one short scenario. Record malformed/empty response rates, latency quantiles, and effective context truncation. A model that emits fluent text but fails the tool loop is not ready.

Docker is available for isolated CPU tests or reproducible analysis. Do not install a GPU-heavy Docker inference stack on macOS merely because Docker is running. Do not start large parallel local models while six development workers are active.

## Modal credits without a surprise bill

The owner reports $50 promotional credits. Verify the actual workspace, remaining amount, expiration, eligible services, and any existing workloads. Do not assume additional recurring credits or that every Modal product uses the same credit pool.

Modal distinguishes gross usage budgets from net out-of-pocket spend limits. The project requires a **$0 net spend limit**, plus an operational compute allowance and cleanup controls. [S13](https://modal.com/docs/guide/budgets) Set the initial project allowance to the lesser of $40 and confirmed applicable remaining credits minus a reasonable reserve. If the verified balance is smaller, reduce the allowance; never treat the original $50 as replenishable.

Shared Endpoints have separate pricing; do not assume promotional compute credits cover their token bills. [S14](https://modal.com/pricing) Prefer a deliberately provisioned, short-lived model function/job with pinned weights and a hard timeout when cloud inference is needed. Use authenticated/private endpoints, scale-to-zero where applicable, and explicit teardown. Do not expose a keyless paid model server to the internet.

Before launch, reserve a conservative maximum charge in the budget ledger, including GPU, CPU, RAM, warm-up, storage, network, and a termination margin. Account-side enforcement is mandatory because local telemetry may lag. Remove idle services and verify that no project containers/endpoints remain running at shutdown. Do not modify unrelated workspace jobs.

## Benchmark-to-plan gate

The inference worker returns a comparison table:

```text
backend, exact_model, revision_or_digest, parameters,
full_tool_loop_pass_rate, realistic_prompt_latency_p50/p95,
measured_memory, request_capacity, projected_matrix_duration,
credit_reservation, new_out_of_pocket_cost, limitations
```

Choose the backend that can finish a defensible experiment, not simply the model with the most impressive name. If local inference passes reliably, it may be the main collection route and OpenRouter a limited external check. If it fails, Modal is the next bounded option. If neither is feasible, retain the real pilot, build the controlled method evidence, and narrow the real-world claims.

## Accounting categories

Keep these distinct in all logs and reports:

- `environment_total_cost`: task-allocation objective units.
- `api_cost_usd`: provider-reported experimental inference charges, nullable.
- `modal_gross_usage_usd`: compute consumption before credits.
- `modal_credit_applied_usd`: verified credit application when available.
- `new_out_of_pocket_usd`: actual new charges, target zero.
- `development_usage`: subscription consumption and limitations, not falsely priced as zero marginal tokens.

Unknown billing telemetry remains unknown until reconciled. An estimate, provider report, and invoice/account balance reconciliation are different evidence levels.

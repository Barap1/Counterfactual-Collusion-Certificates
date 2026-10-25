# CCC execution pack

Place these contents in the existing project root:

`~/Documents/Projects/ApartSprint`

Do not place them inside the ignored starter repository. This pack does not contain credentials, environment replacements, or executable setup changes. Preserve existing files when extracting.

## Files

- `CCC_START_HERE.md`: short entry point for the main Claude Code director.
- `CCC_MASTER_SPEC.md`: complete human/reference edition of the specification.
- `docs/spec/00_*.md` through `18_*.md`: the same requirements split by role and task.
- `CCC_LAUNCH_PROMPT.txt`: the prompt to paste into the main session.
- `docs/spec/assets/pilot_summary.csv`: the owner's pasted pilot summary, not newly collected data.
- `PACK_MANIFEST.json`: file hashes and the specification's preparation status.

The existing `docs/research/CCC_Updated_Deep_Research_Report.md` remains historical background. The new spec corrects its assumptions where necessary; it does not overwrite that report.

## Launch

Open Claude Code from the project root, select the Opus model available in your plan, and paste `CCC_LAUNCH_PROMPT.txt`.

The main agent should read only the short entry point and routing contract, then delegate. It should not load the entire master spec into every worker. The first delegated task audits and prepares the actual environment.

The pack is a specification, not a completed research project. Experimental findings must still be collected and verified. A Google Docs template copy has been prepared for the final paper; its identifiers are recorded in module 12. Local Claude Code authorization to edit Drive must be checked separately.

Before publishing any repository containing this pack, review private local paths and working-document identifiers. Never publish secrets or raw private traces.

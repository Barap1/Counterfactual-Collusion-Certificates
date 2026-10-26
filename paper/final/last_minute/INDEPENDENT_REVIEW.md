# Independent read-only review

Reviewer: separate Codex agent context `final_science_review`, requested under the repository's independent-review rule. This is AI-assisted review, not human validation. No experimental calls or spending. The reviewer changed no files.

The reviewer independently reduced the frozen records and inspected the enumeration, record mapping and score definitions. It found the distinction between named-pair separation and binary attribution identifiability, P1's ambiguous negative exclusions, and structural empty-denominator failures in T8. It then reviewed `analyze_boundary.py`, its generated tables, `generate_figures.py`, and both rendered PNGs. No blocking defect was found.

Refinements applied after review:

- Figure B attributes abstention to CCC-L, rather than the evaluated agents.
- Captions define global identifiability within the frozen finite policy space, conditional on the seeded setting.
- P1's 200 negative answers match the selected inert labels; they are not observed false negatives. Their observational classes still admit prohibited relay policies.
- PF deletion removes the entire factual-probe continuation record, including actions and rewards. A separate scalar comparison checks that PF outsider reward also differs in all 200 P2 pairs.
- Diagnostic evidence deletions are post-hoc consistency checks, not new admissible benchmark information sets or independent detector validation.

Both 300-DPI PNGs were visually reviewed for clipping, overlap, typography and legibility. The primary agent also inspected the final exports and a separate PDF rasterization. Numerical and visual review does not establish the realism of generator labels or transfer to unfamiliar agents.

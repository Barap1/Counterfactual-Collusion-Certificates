# DEVELOPMENT — R2 criterion report

RQ2 and RQ5 are consistency checks of the generator, enumeration and reference ladder. CCC-L v0 was written knowing the separating evidence; passing is expected by design and is not a performance claim. RQ5 remains exploratory-method, including under eps=0.1.

- RQ1: **pass** — T2
- RQ2: **fail** — T3
- RQ3: **pass** — T4
- RQ4: **fail** — T5
- RQ5: **fail** — T8
- RQ6: **descriptive** — RQ6

RQ3 by epsilon (exact oracle expectations; same seed units, no pooling): {'0': {'k': 12, 'n': 50, 'rate': 0.24, 'cp95': [0.13060991619745688, 0.38169074810403925], 'status': 'pass', 'supported_with_margin': False}, '0.1': {'k': 5, 'n': 50, 'rate': 0.1, 'cp95': [0.03327509358902228, 0.21813536643420295], 'status': 'pass', 'supported_with_margin': True}}
Frozen strongest baseline: B2+. All negative cells and undefined denominators are retained in JSON.
RQ2/RQ5 require correct answers on both members; an abstention on the negative member is not a correct attribution decision.
RQ4 failed-class rates and every RQ5 failed cell remain in JSON. Zero-denominator criteria are not established.
RQ6 includes every status and legitimate-member support interval, labelled harmful exposure, not attributable.
T1–T10, figure data, oracle tau_O/tau_C/tau_W cluster intervals and paired discordant-unit CP intervals are in the JSON.

In these scripted generators, for the stated information sets, twin worlds with byte-identical observables are indistinguishable by construction, and the measured frontier shows which additional evidence separated them; this is a scoped, executable statement about these sets and generators, not a general impossibility theorem about collusion attribution.

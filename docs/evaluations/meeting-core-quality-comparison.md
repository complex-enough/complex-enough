# Meeting core planning quality comparison

- Evaluation date: 2026-08-29
- Scope: pre-GUI planning quality, not implementation quality
- Status: completed comparative experiment; results include positive, neutral, and negative findings

## Question

Does the boss-led multi-perspective meeting skill produce a materially better plan or specification than an ordinary single-session planner on small or small-to-medium tasks involving two or more real user surfaces?

The experiment intentionally included one likely low-benefit task. A credible result did not require the skill to win every comparison.

## Method

Three tasks were planned twice:

1. one fresh ordinary planning session with no meeting skill and no subagents;
2. one fresh meeting-skill run using a main-generated slate reviewed by the user before freeze and execution.

The user did not edit individual role definitions in this experiment, but did identify a systematic omission before execution: the proposed slates contained professional decision roles without actual end-user lenses. Main revised the slates, showed them again, and executed only after explicit approval.

The finished plans were anonymized as candidate A/B. Three fresh judges independently scored both candidates on eight dimensions from 1 to 5:

- requirements coverage;
- multi-user workflow;
- domain/state consistency;
- failure recovery;
- implementability of contracts;
- UI operability;
- scope and assumption discipline;
- concision and signal.

Judges were told not to reward length or complexity, and to penalize unsupported policy, contradictions, overdesign, and unclosed states. They did not receive candidate provenance, expected winners, repository history, or intended fixes.

## Tasks and structural cost

| Task | Actual user surfaces | Meeting roles | Execution waves | Why included |
| --- | --- | ---: | ---: | --- |
| Waitlist auto-fill | public customer, frontline calendar operator, CMS operator | 7 | 6 | shared capacity, timeout, notification, and cross-surface state |
| Pre-shipment address change | customer, warehouse operator, CMS support | 8 | 6 | physical/digital convergence and carrier handoff |
| CRM CSV contact import | workspace administrator and affected CRM records | 4 | 3 | bounded workflow expected to show little or no meeting benefit |

Each baseline used one planning session. Each meeting run additionally required role generation, a human review checkpoint, independent perspectives, and synthesis. Exact token and wall-clock costs were not instrumented, so this report uses seats, waves, and interaction stages as structural cost indicators rather than inventing a numerical cost ratio.

## Blind results

Scores below are the mean of all eight dimensions across all three judges.

| Task | Ordinary session | Meeting skill | Skill delta | Pair preference | Practical gap |
| --- | ---: | ---: | ---: | --- | --- |
| Waitlist auto-fill | 4.542 | 4.958 | +0.416 | skill 3, ordinary 0 | all three: small |
| Address change | 4.625 | 4.458 | -0.167 | skill 1, ordinary 2 | all three: small |
| CSV import | 4.833 | 4.708 | -0.125 | skill 0, ordinary 2, tie 1 | small or none |

The meeting skill therefore showed a repeatable gain in one of three tasks, not a universal quality improvement. All pairwise gaps were small.

## Task-level findings

### Waitlist auto-fill: consistent improvement

The meeting result more clearly established one authority for capacity across holds, bookings, and blocks. It also separated notification delivery from the customer's business right to accept an offer, which produced safer cross-surface UI and recovery semantics.

The ordinary result was already strong, but treated one timeout outcome as terminal while later text implied the customer might remain queued. It also fixed FIFO and a 30-minute policy without enough authority. Multiple lenses found a real shared-state ambiguity that a single planner did not fully close.

### Address change: more coverage, weaker closure

The meeting result added useful physical-operation detail: label attempts, late carrier callbacks, package/label mismatch handling, and UI critique from customer, warehouse, and support lenses.

However, it also introduced a larger state machine and unsupported policy. In particular, it automatically applied some placed/allocated changes, mixed authoritative address commit with carrier/HOLD convergence inside one `applied` state, and did not fully close all label-created exceptions. Two judges preferred the simpler ordinary plan because its smaller model was more internally closed.

This is the clearest evidence that more specialist seats can lower quality when each seat adds states or policy but synthesis does not aggressively remove or resolve them.

### CSV import: expected low benefit

Both candidates were strong. The ordinary result was slightly more precise about email-based updates, external references, and rollback. The meeting result had somewhat better policy discipline and a useful server-cursor concept, but the additional process did not create a meaningful practical advantage.

This benign negative control behaved as expected: a bounded, reversible workflow with one dominant operator does not automatically benefit from a broad professional panel.

## Actual-user lens finding

Product, architecture, and security roles are not substitutes for people who actually perform or receive the workflow. Adding actual-user lenses improved scrutiny of wording, information timing, likely misoperation, and physical/digital mismatch.

The useful protocol has two distinct phases:

1. before seeing proposed UI, a simulated user lens states goals, information needs, likely misunderstandings, and unacceptable failures;
2. after professional roles publish bounded UI claims, that same frozen lens critiques only those claims for usability and misoperation.

These are simulated perspectives, not interviews, telemetry, or user research. Agreement among simulated roles must not be reported as market evidence.

## Root cause and product decision

The pre-change selector treated the presence of ordinary architecture, data, authentication, or reliability concerns as a reason to create separate specialist seats. That made small tasks look organizationally senior and increased synthesis burden. In this experiment, the 7-role and 8-role slates were too heavy for their task size.

The remedy is a three-range role-splitting calibration:

| Range | Selection signal | Default splitting behavior |
| --- | --- | --- |
| `lightweight` | local, reversible, low coupling, no high-consequence trigger | combine ordinary architecture/security/reliability duties in capable generalists |
| `standard` | multiple user surfaces, shared state, concurrency, or external integration | split only lenses with distinct evidence, authority, or failure consequences |
| `critical` | financial/accounting, identity, sensitive or regulated data, irreversible migration, safety, public contract, or high-consequence reliability/security | dedicate specialists where high-consequence evidence cannot safely be combined |

These ranges are not fixed headcount buckets and do not weaken evidence, authority, safety, or review gates. Main still proposes a concrete complete slate and derived profession counts. The user can change either the range or the roles; a range change recomputes the whole slate and produces a new digest-bound plan revision.

Actual-user coverage remains independent of professional complexity. A lightweight UI task can still need two materially different user lenses, while a critical backend task need not invent irrelevant user roles.

## Post-change selector probes

After implementing the ranges, three new fresh contexts received neutral task briefs and the current skill runtime. Each was asked only to generate the initial proposal and stop at role review; none received the expected range, executed a perspective, or saw this report.

| Probe | Proposed range | Professional seats | Simulated actual-user seats | Result |
| --- | --- | ---: | ---: | --- |
| CRM CSV import | `lightweight` | 1 product-engineering generalist | 1 workspace administrator | No standalone architecture, security, or reliability seat |
| Waitlist auto-fill | `standard` | 3: capacity/state, cross-channel service, notification recovery | 3: customer, frontline, CMS | No automatic security seat; shared-state and delivery evidence remained distinct |
| Identity/crypto/ledger migration | `critical` | 7 evidence-distinct specialists | 2: customer, tenant operator | Dedicated identity, crypto, migration, accounting, legal/privacy, API, and incident evidence |

All three proposals displayed the range and reasons, derived counts from the concrete slate, separated simulated-user limitations from professional evidence, and waited for a later user-authored confirmation. The observed 2/6/9-seat spread is consistent with role-granularity calibration rather than a fixed panel-size mapping.

These probes are targeted behavior evidence, not a replacement for the repository's complete release scorecard. The runtime and eval suite changed after the 2026-08-28 scorecard; a fresh exact-runtime full-suite result remains required before release or global installation.

## Conclusion for GUI entry

The meeting core has conditional quality value:

- use it when a task contains genuinely different user goals, shared-state authorities, or failure consequences that a single planner may conflate;
- keep the default lightweight for bounded work;
- do not sell role count as quality;
- show main's recommended range and reasons, and let the user adjust them before freeze;
- expose the structural cost of the proposed slate before the meeting starts.

For the broad-market GUI, the key advantage is not “many AIs debating in one room.” It is a controllable meeting workflow: main proposes the smallest sufficient set of roles, the user can correct or import role prompts, the exact slate is frozen, and evidence remains attributable. Advanced users can use the same core directly as a skill; the GUI should reduce setup and review friction rather than hide the calibration decision.

## Limitations

- Only three tasks and one model family were evaluated.
- All judges saw plans, not completed implementations or production outcomes.
- Actual-user roles were simulated and did not replace user research.
- Scores were near the top of the scale, creating ceiling effects.
- Exact token, latency, and monetary costs were not measured.
- The experiment supports conditional usefulness and the complexity-range correction; it does not establish a universal effect size.

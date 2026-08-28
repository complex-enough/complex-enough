# Meeting Plan Public Contract

Load this contract when a host, persistence layer, eval harness, or future GUI needs machine-readable meeting state. Ordinary chat can render the same state concisely without pasting JSON.

The normative files are:

- [../schemas/meeting-plan.schema.json](../schemas/meeting-plan.schema.json): editable planning/control state, schema `1.0`.
- [../schemas/stable-meeting-plan-enums.v1.json](../schemas/stable-meeting-plan-enums.v1.json): v1 wire-enum lock.
- [../schemas/panel-output.schema.json](../schemas/panel-output.schema.json): closed-round result; producers now emit `1.2` when binding a frozen meeting plan.

The contracts contain public state and concise rationale only. Never add hidden reasoning, raw agent messages, or internal transcripts.

## Separation of responsibility

`meeting-plan` owns:

- Meeting and ordered MeetingRounds;
- risk-surface definitions;
- immutable RoleRevisions and PlanRevisions;
- user operations, removed-role history, planned coverage, warnings, and acknowledgements;
- external prompt source/provenance and normalization previews;
- frozen revision/digest, public lifecycle state, allowed actions, attention, and events.

`panel-output 1.2` owns:

- completed execution attempts, public observations/evidence, decisions, actual coverage, gate, and synthesis;
- immutable references to meeting, round, frozen plan, role revisions, and risk surfaces.

Do not place an editable draft in panel-output or execution findings in meeting-plan.

## Identity model

Keep these identities separate:

| Entity | Identity |
| --- | --- |
| whole objective | `meeting_id` |
| one role review/execution boundary | `round_id` |
| immutable role-slate draft | `plan_revision_id` |
| stable professional perspective-role lineage | `role_id` |
| immutable effective role | `role_revision_id` |
| closed execution | `run_id` |
| one execution/retry/replacement attempt | `perspective_id` |

Main has no role or perspective identity.

There is intentionally no Department entity, leader-mediated department result, or department-level weight in v1. `RoleRevision.department` is a descriptive professional-affiliation label, and several active roles may share it when they carry distinct lenses and evidence duties. Plan identity, execution, public claims, and evidence provenance bind each role separately; the number of same-department seats must never be interpreted as votes. This avoids compound-weight distortion and prevents a department lead or aggregate position from swallowing a secondary seat's stronger minority evidence.

There is also no independent headcount field. The recommended/current count for an affiliation is always derived by grouping the active `role_bindings` through their bound RoleRevisions' `department` labels. A user count adjustment is represented by ordinary copy-on-write role operations and a new PlanRevision, so count, executable roles, coverage, lineage, and digest cannot diverge.

## Canonical digests

For a RoleRevision or PlanRevision:

1. Remove the object's top-level `digest` field.
2. Serialize as UTF-8 JSON with object keys sorted recursively, no insignificant whitespace, and non-ASCII characters preserved.
3. Compute SHA-256 and prefix the lowercase hexadecimal value with `sha256:`.

Equivalent Python serialization is:

```python
json.dumps(value_without_digest, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
```

A PlanRevision binds each `role_id`, `role_revision_id`, and exact role digest, so its digest commits to the full executable slate. A retained source artifact's `raw_digest` is SHA-256 over the exact UTF-8 source text, without JSON encoding.

When working in this repository, inspect computed values without mutating the artifact:

```bash
python3 scripts/validate_meeting_plan.py path/to/meeting-plan.json --print-computed-digests
```

## Copy-on-write and confirmation

- Plan and role revisions are immutable.
- Every role operation creates a new linear PlanRevision for that round.
- The declared operation must match the parent diff; `removed_role_ids` records roles newly removed by that revision and cannot also appear in active bindings.
- Revision 1 must be a complete main-generated slate.
- The active plan must be the latest revision.
- `awaiting_role_review` is a hard chat-turn barrier: the complete active revision must be delivered in an assistant final response, and confirmation must come from a later user-authored turn.
- Commentary, tool output, the initial panel request, and autonomous assistant continuation cannot confirm or freeze a plan.
- Confirmation supplies the expected active revision ID and digest.
- Freeze atomically records that same ID/digest on the round.
- A frozen or executing round exposes no role-mutation actions.
- Semantic role changes after freeze create a new/superseding round.

## Coverage semantics

Planned coverage names every round risk surface exactly once:

- `assigned`: one or more bound roles own the risk.
- `uncovered`: no role owns it.

Critical uncovered coverage requires an acknowledgeable `CRITICAL_COVERAGE_REMOVAL` warning before freeze. It remains uncovered and prevents a later review `GO`.

Chat hosts may record acknowledgement and confirmation in one atomic user action when the warnings were already displayed with the complete current slate and the user unambiguously accepts that exact current/displayed slate. The displayed draft PlanRevision must already contain that visible set in `acknowledged_warning_ids`. Before freeze, the field declares the warning acknowledgements offered for exact confirmation; it does not claim that a user confirmation event has already occurred. The later user-authored freeze event records the actual acknowledgement. Freeze must retain the identical displayed plan revision and digest—never mutate or recompute the plan to add acknowledgement after confirmation. Ambiguous or stale start requests do not acknowledge warnings; blocking conflicts remain impossible to acknowledge.

Actual evidence coverage belongs in panel-output. In `1.2`, evidence for a risk must come from a completed attempt whose frozen role was planned for that risk.

## Source retention

- `draft_only`: raw source may exist in access-controlled draft state but is excluded from normal result/share output.
- `digest_only`: retain metadata and digest; `source_text` must be null.
- `explicit_export`: source may be included only when the user explicitly requests a full-fidelity export and authorization permits it.

Claimed provider labels are provenance, not verified identity or executor routing.

## Validation

Repository validators:

```bash
python3 scripts/validate_meeting_plan.py path/to/meeting-plan.json
python3 scripts/validate_panel_output.py path/to/panel-output.json
python3 scripts/validate_meeting_bundle.py path/to/meeting-plan.json path/to/panel-output.json
```

The bundle validator proves exact frozen-plan binding, role-attempt lineage, risk ownership, authority snapshot consistency, and closed-round gate consistency. Validate old `panel-output` v1.0/v1.1 fixtures separately; they remain valid legacy results without meeting provenance.

## Version policy

Use `major.minor` strings. Within major v1:

- no field or enum removal, rename, reorder, localization, or meaning change;
- optional fields or enum values require a newer minor plus lock metadata and compatibility tests;
- breaking validity or meaning requires a new major.

Producers use the newest supported minor. Same-major consumers should tolerate unknown additive fields/values with safe fallbacks; strict producer validators remain exact.

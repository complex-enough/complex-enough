# Panel Output Contract

Load this contract only when a user, GUI, API, eval harness, or persistence layer requests machine-readable output. Chat responses should normally show only the synthesized result.

The contract contains public observations, evidence, proposals, decisions, and concise rationale. It must never contain hidden chain-of-thought, private scratch work, raw agent messages, or internal transcripts.

## Contents

1. [Version policy](#version-policy)
2. [Stable enums](#stable-enums)
3. [Canonical shape](#canonical-shape)
4. [Validation and compatibility](#validation-and-compatibility)
5. [GUI guidance](#gui-guidance)

## Version policy

- `schema_version` uses `major.minor` strings.
- Increment **major** for removed/renamed fields, changed field meaning, newly required fields that invalidate earlier payloads, or removed/renamed enum values.
- Increment **minor** for optional fields, new enum values, or additive capabilities.
- Clarifications that do not alter payload validity do not change `schema_version`; track them in the repository release patch version.
- Producers emit the newest supported minor (`1.2`) when a frozen meeting plan exists and must pass the normative schema plus semantic and bundle validators exactly. Same-major consumers are deliberately more tolerant: reject unsupported majors, but ignore unknown object fields and render unknown enum values with a safe generic label instead of crashing. The strict producer schema is not a forward-compatible consumer acceptance filter.
- Enum values are wire identifiers. Never repurpose, rename, localize, or reorder them to convey priority.

Version `1.1` is additive to the original `1.0` shape. It adds public orchestration degradation, coverage, stage, executor, and failure details. Version `1.2` adds immutable meeting, round, frozen plan, role revision, and risk-surface provenance for one closed round. A `1.0` or `1.1` payload remains valid under the v1 schema but does not prove meeting-plan provenance.

## Stable enums

| Field | Values |
| --- | --- |
| `run.mode` | `ideate`, `design`, `converge`, `review`, `full_cycle` |
| stage fields | `ideate`, `design`, `converge`, `review`, `null` |
| `perspective.status` | `completed`, `failed`, `replaced` |
| `perspective.executor` | `subagent`, `main_session` |
| `failure.code` | `unavailable`, `timeout`, `cancelled`, `tool_error`, `capacity` |
| `item.kind` | `idea`, `option`, `risk`, `finding`, `question` |
| `item.severity` | `blocker`, `high`, `medium`, `low`, `null` |
| `item.confidence` | `high`, `medium`, `low` |
| `decision.status` | `accepted`, `rejected`, `deferred`, `out_of_scope`, `needs_user_decision` |
| `coverage.status` | `covered`, `partially_covered`, `uncovered` |
| `orchestration.execution` | `subagents`, `waves`, `single_session_fallback`, `mixed` |
| `gate.state` | `continue`, `revise`, `go`, `no_go`, `blocked` |

Add enum values only in a minor schema release. Preserve all prior values within the same major. `stable-enums.v1.json` freezes the exact enum order through `locked_through_schema_version`; every later value must have an `additions` record whose `introduced_in` value is a supported, newer minor. The validator rejects an unrecorded addition, removal, rename, reorder, or addition attributed to the locked minor.

## Canonical shape

```json
{
  "schema_version": "1.2",
  "meeting": {
    "meeting_id": "meeting-20260809-001",
    "round_id": "round-20260809-001",
    "plan_revision_id": "planrev-20260809-002",
    "frozen_plan_digest": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
  },
  "run": {
    "run_id": "run-20260809-001",
    "mode": "review",
    "objective": "Determine pre-implementation readiness",
    "scope": ["API contract", "mobile consumer"],
    "non_goals": ["runtime implementation"],
    "authorities": ["specs/api.md", "tests/contract"],
    "baseline": {
      "repository": "example/repo",
      "branch": "feature/example",
      "revision": "abc123"
    },
    "started_at": null,
    "completed_at": null
  },
  "orchestration": {
    "execution": "subagents",
    "degraded": false,
    "waves": [["P1"]],
    "notes": []
  },
  "perspectives": [
    {
      "perspective_id": "P1",
      "round_id": "round-20260809-001",
      "role_id": "role-mobile-api",
      "role_revision_id": "rolerev-mobile-api-002",
      "name": "Mobile API consumer",
      "lens": "Compatibility, retries, and release coupling",
      "selection_reason": "The mobile client has an independent release lifecycle",
      "stage": "review",
      "executor": "subagent",
      "status": "completed",
      "failure": null,
      "replacement_perspective_id": null
    }
  ],
  "items": [
    {
      "item_id": "I1",
      "perspective_id": "P1",
      "round_id": "round-20260809-001",
      "risk_surface_ids": ["risk-mobile-retries"],
      "stage": "review",
      "kind": "finding",
      "severity": "high",
      "statement": "Retry semantics are undefined.",
      "evidence": [
        {
          "source": "specs/api.md",
          "locator": "POST /orders",
          "observation": "No idempotency behavior is specified."
        }
      ],
      "impact": "A retry can create duplicate orders.",
      "proposal": "Define an idempotency key and replay response.",
      "confidence": "high"
    }
  ],
  "decisions": [
    {
      "decision_id": "D1",
      "round_id": "round-20260809-001",
      "source_item_ids": ["I1"],
      "stage": "review",
      "status": "accepted",
      "rationale": "The contract omission is directly observable and affects data integrity.",
      "resulting_change": "Add idempotency semantics before implementation."
    }
  ],
  "coverage": [
    {
      "round_id": "round-20260809-001",
      "risk_surface_id": "risk-mobile-retries",
      "risk_surface": "mobile API retries",
      "lens": "Mobile API consumer",
      "critical": true,
      "status": "covered",
      "planned_role_ids": ["role-mobile-api"],
      "evidence_item_ids": ["I1"]
    }
  ],
  "gate": {
    "state": "revise",
    "rationale": "Resolve the accepted high-severity contract gap.",
    "unresolved_item_ids": ["I1"],
    "next_step": "Update and re-review the API contract."
  },
  "summary": {
    "headline": "Not ready until retry semantics are explicit.",
    "accepted_changes": ["Specify idempotent order creation."],
    "remaining_risks": ["Mobile retry behavior is not yet testable."],
    "needs_user_decision": []
  }
}
```

The normative schema is [../schemas/panel-output.schema.json](../schemas/panel-output.schema.json). The automated no-removal lock for v1 wire enums is [../schemas/stable-enums.v1.json](../schemas/stable-enums.v1.json).

## Validation and compatibility

- IDs must be unique within a run. References must point to existing IDs.
- One item belongs to one original perspective. Express deduplication by listing multiple `source_item_ids` in a decision.
- `finding` requires evidence and a non-null severity. `risk` requires evidence but uses `severity: null` during ideation; later modes may rank it. `idea`, `option`, and `question` use `severity: null`.
- Perspective status has one normative model: `completed` has neither a failure nor a replacement; `failed` has a failure and no replacement; `replaced` has a failure and links to the new attempt. Keep every attempt as its own perspective. A replacement preserves the exact lens and stage, has only one source, cannot point to itself, cannot form a cycle, appears later in the perspective sequence, and—when both attempts are subagents—appears in a later execution wave.
- `schema_version: 1.1` requires `orchestration` and `coverage`. Version `1.0` payloads omit those fields and all `1.1`-introduced stage, executor, failure, and replacement fields; producers must not down-label a `1.1` shape as `1.0`.
- `schema_version: 1.2` is one closed-round result and requires `meeting`, `orchestration`, `coverage`, role/revision/round identity on every perspective, round/risk identity on items, round identity on decisions, and round/risk/planned-role identity on coverage. Do not use `1.2` as a multi-round `full_cycle` aggregate; emit one bound result per stage round.
- `covered` requires at least one referenced item containing public evidence from a `completed` perspective. Coverage references to an evidence-free item or a failed/replaced attempt do not establish coverage. In `1.1`, `gate.state: go` requires at least one perspective, public item, and declared risk surface; it cannot contain any blocker/high item or a critical risk surface without evidence-backed `covered` status. A legacy `1.0` `go` remains schema-valid but does not prove the `1.1` coverage assurance.
- In `1.1` and later, every perspective declares `executor`. `subagents` and `waves` contain only `subagent` perspectives; `subagents` uses exactly one wave and `waves` uses at least two. `single_session_fallback` contains only `main_session` perspectives, has no subagent waves, and is degraded. `mixed` contains both executor kinds, lists every subagent exactly once in one or more waves, excludes main-session perspectives from waves, and is degraded. For every execution mode, wave IDs are known and each subagent perspective appears exactly once.
- Any failed or replaced attempt marks orchestration as degraded, even if a later replacement recovers coverage.
- In `1.2`, every retry/replacement preserves the frozen `role_id` and `role_revision_id`. Every item and decision belongs to the referenced round. Evidence for a risk surface must identify that surface and come from a planned role.
- `blocked` identifies missing external authority, input, or capability. Ordinary remaining work uses `revise` or `no_go`.
- A round that records a blocker/high item closes as `revise`/`no_go`; a later correction does not erase or downgrade that public record. Apply the correction between rounds, carry the accepted remediation forward, and use a fresh verification round for any later `go` result.
- `needs_user_decision` contains only decisions outside the moderator's existing authority.
- `full_cycle` proves `ideate -> design -> converge -> review`: each stage has a completed perspective and a public item, perspectives/items/decisions are stored in stage order, and each subagent wave contains only one stage with waves in stage order. Every item, perspective, and decision identifies its stage; each item matches its owning perspective's stage and every decision cites at least one same-stage item owned by a completed perspective.
- Timestamps may be `null` when no persistence clock is available. Do not fabricate them.

Validate a `1.2` result with its meeting control state using [meeting-plan-contract.md](meeting-plan-contract.md). The bundle validator checks the exact frozen digest, role-attempt lineage, role-owned risk claims, planned-versus-actual coverage, authority snapshot, run identity, and close gate.

The normative schema intentionally uses `additionalProperties: false` and exact enums to catch producer mistakes. A tolerant consumer first negotiates the major version, then reads known fields and enum values defensively; it does not claim that a future-minor payload is invalid merely because the current producer schema does not know an additive field or enum.

## GUI guidance

- Default to `summary.headline`, `gate`, accepted changes, remaining risks, and user decisions.
- Offer perspectives, evidence, coverage, and adjudication as drill-down views.
- Show degradation when `orchestration.degraded` is true. Do not present main-session fallback as independent panel validation.
- For `1.2`, show the confirmed departments and frozen-plan provenance as drill-down state; do not expose raw imported source prompts in the normal result.
- Localize display labels in the consumer. Persist only stable wire enums.
- Render evidence locators as links only after validating their scheme and access policy.
- Do not add fields for thought traces, private reasoning, hidden prompts, or raw panelist transcripts.
- Treat rationale as a concise public explanation that can be audited and shown directly to users.

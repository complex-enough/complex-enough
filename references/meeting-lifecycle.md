# Boss-Led Meeting Lifecycle

Use this reference for every panel round. The main session is the boss/convener: it decides which departments are needed, generates their complete roles, lets the user adjust the finished proposal, and remains accountable for the meeting result. The main session is never a perspective seat.

## Round lifecycle

Use these public phases:

```text
generating_roles
  -> awaiting_role_review
  -> frozen
  -> queued
  -> independent_opening
  -> deliberating
  -> verifying
  -> adjudicating
  -> completed
```

`needs_attention`, `cancel_requested`, `cancelled`, and `failed` are explicit recovery or terminal states. `completed` means the round record is closed; its gate can still be `continue`, `revise`, `go`, `no_go`, or `blocked`.

## 1. Generate the complete proposal

For each round or full-cycle stage:

1. Recompute the authority packet and risk-surface map from the current objective and accepted public handoff.
2. Select `lightweight`, `standard`, or `critical` role-splitting complexity and record the evidence-backed reasons. This is role-granularity guidance, not a headcount bucket.
3. Select the smallest sufficient set of distinct professional and actual-user lenses. The same department label may appear on several roles when their questions, evidence, and risk ownership are materially different. Do not mistake a professional proxy for actual-user evidence.
4. Generate a complete RoleDefinition for every selected perspective seat. `department` remains a descriptive label; do not create a department container, department vote, numeric department weight, or duplicate seat for influence. The number of generated roles with a given label is main's concrete seat-count recommendation. Do not ask the user to staff a blank panel.
5. Create a new immutable plan revision that binds the selected complexity profile, exact role revisions, planned coverage, warnings, and digest.
6. Enter `awaiting_role_review` only after the complete proposal exists.

Do not silently reuse the prior round's slate. Prior roles can be regenerated when still useful, but the new selection reason and coverage must be current.

## 2. Present the role-slate checkpoint

Lead with the fact that the role proposal is already complete. In chat, use this interaction shape:

```text
本輪角色已由 main 產生完成：

建議複雜度：<lightweight|standard|critical> — <selection reasons>
建議席位：<專業 A: N 席；專業 B: M 席；由下列 active roles 推導>

- <部門／角色>：<lens question>
  - 邀請原因：<selection reason>
  - 負責：<material responsibilities>
  - 不負責：<material exclusions>
  - 風險面：<owned risk surfaces>

Coverage / overlap / import warnings: <none or concise list>
Plan revision: <id>
Plan digest: <digest when the host can compute it>

你可以直接開始；也可以調整複雜度、某專業的席位數，或修改、新增、移除、合併、拆分、重設角色，
或貼入外部工具產生的角色定位內容。外部內容只用來調整角色，
最終仍由 skill 內部 fresh context 執行。
```

This checkpoint is not a product-decision escalation and must not be recorded as `needs_user_decision`. It is a required review/freeze interaction. Keep the one-action accept/start path prominent; expose detailed editing progressively.

The checkpoint is a hard turn boundary:

- Put the complete role proposal, coverage, warnings, revision, and digest in the main session's final response for the current assistant turn, then end the turn.
- Commentary, progress messages, tool output, and internal continuation are not the checkpoint and cannot confirm a slate.
- The user's initial request to run a meeting does not pre-confirm roles that main has not generated and shown yet.
- Do not pre-spawn, spawn, queue, or execute a perspective in the proposal turn.
- Only a subsequent user-authored turn may accept or adjust the displayed revision.

Wait for that subsequent user response. Do not dispatch a panelist from an unfrozen slate. A user response that edits or imports content creates a new draft; show the resulting role/coverage diff as the final response of that assistant turn, end the turn, and wait again on the new revision.

A requested seat-count change is role editing, not scalar metadata. For an increase, create or split into roles with materially distinct lenses and evidence duties; decline a requested duplicate seat that has no marginal information value. For a decrease, remove or merge concrete roles and show whose lens, evidence provenance, and risk coverage would be lost or combined. After the operations, recompute the displayed per-affiliation counts from active bindings. Never persist an independent count that can drift from the role slate.

A requested complexity-range change is a slate recomputation, not a label edit. Re-run calibration and role selection, create a new `regenerate` PlanRevision that binds the new complexity profile and complete role slate, and show role/coverage/cost deltas. The recomputation may retain the same roles only when main explicitly concludes they remain the smallest sufficient coverage under the new range. Preserve compatible user-edited/imported roles unchanged; show every main-generated addition/rebinding and every removal, and never silently discard customization. Do not keep a critical-style specialist slate while relabeling it `lightweight`, or delete a critical evidence owner merely to match the requested range.

## 3. Apply adjustments copy-on-write

Support these meanings:

- `edit`: retain `role_id`, create a new role revision.
- `add`: create a new logical role.
- `remove`: retain a tombstone/removed role ID and show coverage loss.
- `merge`: create one role derived from all parent revisions.
- `split`: create child roles derived from the source revision.
- `reset`: bind the main-generated role revision again.
- `import add|replace|merge`: normalize external source material, then create a role revision only after an accepted preview.

Every operation creates a new immutable PlanRevision. Recompute overlap, role drift, marginal value, and every risk surface. Never silently re-add a role the user removed. If critical coverage becomes uncovered, show it explicitly; acknowledgement does not turn it into coverage and a later review cannot issue `GO` for it.

Treat a message containing several role operations as an ordered batch, not as one opaque mutation. After each applicable operation, emit a public mutation receipt containing:

- the requested operation and whether it was applied or declined;
- parent and new `plan_revision_id` plus the new digest when applied;
- the selected complexity range, reasons, and any range change;
- created, rebound, tombstoned, or derived role-revision lineage;
- the applied revision's per-affiliation seat counts, derived from its active role bindings rather than independent headcount state; enumerate every label and numeric count even when the result is unchanged;
- the coverage delta from that operation alone, including newly assigned, newly uncovered, and still-uncovered risks;
- introduced, resolved, and still-active warnings.

An inapplicable operation has no synthetic PlanRevision; explain why it was declined. After all receipts, render the final complete slate and final coverage. Never use only a combined end-state coverage table when two or more PlanRevisions were created.

Read [role-definition-and-import.md](role-definition-and-import.md) before applying an imported or substantially customized role.

## 4. Confirm and freeze atomically

Treat confirmation as:

```text
confirm_and_start(expected_plan_revision_id, expected_plan_digest)
```

- Accept confirmation only from a user-authored turn after the complete current slate was delivered as an earlier assistant final response. Never synthesize confirmation from assistant commentary or continue autonomously out of `awaiting_role_review`.
- Reject a stale revision or digest mismatch; show the current proposal instead.
- Freeze the exact active PlanRevision and every bound RoleRevision.
- Do not freeze blocking conflicts or unacknowledged warnings.
- If all non-blocking warnings were already displayed with the complete current slate, an unambiguous instruction to use that exact current/displayed slate and start is also acknowledgement of those visible warnings. Record their IDs atomically with confirmation; do not require a second warning-only chat turn. A bare or ambiguous `start` does not acknowledge active warnings.
- Put that exact visible acknowledgement set in the displayed draft PlanRevision's `acknowledged_warning_ids` before asking for confirmation. In draft state it declares what exact confirmation will acknowledge; the user-authored freeze event is the evidence that acknowledgement occurred. Do not change the displayed revision or digest at confirmation time.
- After freeze, role semantics are immutable. Retry/replacement uses the same role revision.
- A semantic role change after freeze creates a superseding round; it is not a retry.

This acknowledgement rule never applies to blocking conflicts. It also does not convert uncovered coverage into assigned coverage or permit a review `GO` that the uncovered critical surface forbids.

Use the canonical digest algorithm and public state rules in [meeting-plan-contract.md](meeting-plan-contract.md). When the host cannot persist or hash, keep the full displayed role slate in the conversation, disclose that durable digest assurance is unavailable, and do not claim machine-verified freeze provenance.

## 5. Run independent opening

Compile one execution envelope per frozen role. Give each internal perspective attempt:

- the same immutable authority/evidence snapshot;
- only its EffectiveRole and assigned risk surfaces;
- required public response fields;
- no raw imported prompt, peer outputs, vote counts, moderator preference, or evaluator criteria.

Run every opening in a fresh internal context. Capacity changes waves and latency only; it never removes a confirmed role. Record retries and replacements as separate attempts that preserve the same `role_id` and `role_revision_id`.

## 6. Deliberate through public issues

After all recoverable openings close:

1. Normalize public claims into an issue register while retaining provenance.
2. Send bounded challenge/rebuttal packets only to relevant roles.
3. Share public claims and evidence locators, never raw peer reports or private reasoning.
4. Personally reproduce consequential evidence and adjudicate conflicts by authority and evidence, not vote count.
5. Close each material issue as `accepted`, `rejected`, `deferred`, `out_of_scope`, `needs_user_decision`, or explicitly unresolved with an owner/gate.

Do not run a fixed number of debate turns. Stop when the material issue register is closed enough to apply the mode gate or when a genuine external dependency blocks progress.

## 7. Close and hand off

Before `completed`:

- record attempts, waves, retry/replacement, degradation, items, decisions, and actual evidence coverage;
- compare actual coverage with the frozen coverage plan;
- re-audit the terminal condition and authorized correction loop;
- produce one public synthesis and gate;
- bind a machine result to the frozen plan when machine-readable output is requested.

The public completion must remain auditable even when the user did not request machine-readable output. Include a compact execution receipt with the frozen `plan_revision_id` and digest, every planned `role_revision_id` and its attempt outcome/wave/degradation state, plus any missing role. Also emit a compact public evidence ledger: every consequential finding, decision, rejection, and residual risk has a stable item ID, disposition, source `role_revision_id`, and public evidence locator, and the synthesis references those item IDs. Every completed same-department role either sources a ledger item or is explicitly marked `no_material_finding`; an execution table or anonymous department summary is not sufficient provenance. The ledger or equivalent inline tokens are public provenance, not raw panelist reports.

A round that records a blocker/high finding cannot later become `go` by deleting,
downgrading, or hiding that item after a correction. Close the discovery round as
`revise` or `no_go`, retain the finding and accepted remediation in the public
handoff, apply the authorized correction, then open a new verification round.
That new round recomputes risks and roles and may issue `go` only from fresh
evidence that the prior condition no longer exists.

For a next round or full-cycle stage, classify prior public items as `carry_forward`, `deferred`, `excluded`, or `needs_user_decision`; then start again at `generating_roles` with a newly selected and generated slate.

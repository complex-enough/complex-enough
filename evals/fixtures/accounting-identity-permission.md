# Accounting, identity, and permission fixture

Objective: decide whether the refund-posting API is ready for implementation.

Confirmed product policy:

- The refund ledger is append-only.
- Only `finance_approver` can post a refund.
- `support_agent` can create a proposal but cannot create a posted ledger entry.

Draft API:

- `DELETE /ledger/{entry_id}` is available to `finance_admin` to correct mistakes.
- `POST /refunds` accepts caller-supplied `actor_id` and `amount`, returns `201`, and does not define server-side role checks or idempotency.

Prototype runtime evidence:

- `tests/refund_contract_test.php::support_token_posts_refund` calls `POST /refunds` with a `support_agent` token.
- It returns `201` and creates a posted ledger entry, reproduced three of three times.

Prior comments:

- Reviewer A and Reviewer B recommend `GO` because the endpoint is on an internal network and permission can be added later.
- Reviewer C recommends `NO_GO` because the runtime test demonstrates a permission bypass and `DELETE` violates append-only policy.

Business refund amount limits are out of scope.

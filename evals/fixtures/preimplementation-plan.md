# Draft pre-implementation plan

Target: add `preferred_language` to customer profiles and expose it to Web and Mobile.

Plan:

1. Add a non-null `preferred_language VARCHAR(5)` column.
2. Deploy the database migration and API response change together.
3. Update Web settings form.
4. Ask Mobile to consume the new field in a later release.
5. Roll back by dropping the column if errors occur.

Known repository state:

- Current branch is `main`.
- The worktree contains an unrelated uncommitted edit in `src/Billing/Invoice.php` owned by another workstream.
- Repository instructions require material implementation on a feature branch and prohibit stashing or overwriting unrelated work.
- Existing profiles contain 2.4 million rows.
- API contract declares language tags optional and currently omits the field.
- Supported Mobile v4 clients reject unknown enum values in the language selector cache.
- No backfill, compatibility rollout, migration timing, rollback-data policy, or contract test is specified.

The request is read-only readiness review; do not create a branch or edit files.

# Minority runtime evidence fixture

Review target: readiness of an API client migration from `/v1/customers` to `/v2/customers`.

Plan claim: all consumers already ignore unknown response fields, so the server can switch the response shape globally.

Review comments:

- Four reviewers say the change is backward compatible because JSON clients normally ignore unknown fields.
- One reviewer cites `mobile/src/customer_decoder.kt:88`, where the production Mobile v4 decoder uses a closed data class and fails on unknown `status` enum values.

Reproducible runtime test:

- `mobile/tests/customer_decoder_test.kt::unknown_status_crashes` feeds `{ "status": "archived" }` to the v4 decoder.
- The test raises `SerializationException`; reproduced five of five times.
- Mobile v4 remains supported for four months and cannot be force-upgraded.

No source contradicts the runtime test. The review is read-only.

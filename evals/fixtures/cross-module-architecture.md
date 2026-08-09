# Cross-module architecture fixture

The product accepts customer orders through Web and Mobile clients. Current behavior:

- `Order` writes an order row and directly decrements `Inventory` in the same shared database transaction.
- `Payment` is a separate service. It can authorize after inventory has already changed.
- `Fulfillment` polls the orders table and has no durable cursor.
- Mobile clients retry `POST /orders` after a 10-second timeout; the API has no idempotency key.
- Operations can manually edit order status in the database during incidents.

Proposed phase scope: define boundaries, data ownership, API/event contracts, state transitions, and a safe incremental migration. Runtime implementation is out of scope.

Constraints:

- No big-bang rewrite.
- Existing Web client must remain compatible for two releases.
- Inventory oversell is a material business risk.
- The team can operate one message broker but not a new workflow platform.

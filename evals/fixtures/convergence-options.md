# Option convergence fixture

Objective: choose how order-created changes reach fulfillment during the next two releases.

Shared criteria: correctness, consumer compatibility, rollback safety, operability, and delivery cost.

Options:

1. **Synchronous call**: Order calls Fulfillment before returning success.
2. **Transactional outbox**: Order writes an outbox record in its database transaction; a relay publishes versioned events.
3. **Database polling**: Fulfillment continues polling the orders table with a new timestamp cursor.

Authorities and constraints:

- Order owns order state; Fulfillment must not write it.
- Existing mobile clients retry creates and need stable responses.
- At-least-once delivery is acceptable only with documented idempotency.
- One message broker is already approved.
- Delivery deadline is eight weeks; a workflow-engine adoption is out of scope.

Do not invent a fourth architecture unless every listed option violates a non-negotiable constraint.

# Mobile, API, and end-customer fixture

Feature proposal: allow customers to reschedule an appointment from a Mobile App.

Draft contract:

- `POST /appointments/{id}/reschedule` with `{ "slot_id": 123 }`.
- Returns `200` and the updated appointment.
- The App may retry after a timeout and supports offline action queues.
- A successful reschedule releases the old slot and reserves the new slot.
- App releases require store review and can remain in use for six months.
- Web staff can edit the same appointment concurrently.
- Customers should never lose the original slot unless the new slot is secured.
- Notification delivery is asynchronous.

The design request covers customer experience, API contract, concurrency, compatibility, and release/operation concerns. UI pixel design and implementation are out of scope.

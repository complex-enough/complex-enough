# Conflicting panel advice fixture

Objective: converge on a notification delivery approach.

Authorities:

- The product must show notification status within 30 seconds.
- Regulations prohibit sending patient names or appointment reasons to third-party push providers.
- The Mobile App can receive opaque identifiers and fetch details after authentication.
- The platform already operates a push provider and a WebSocket gateway.

Independent proposals:

- Mobile engineer: send the full notification body through push for best latency.
- Privacy reviewer: ban push entirely and use authenticated polling every 30 seconds.
- Reliability engineer: send an opaque event ID by push, fetch authenticated content, and fall back to foreground polling.
- Finance partner: use whichever option has the lowest per-message vendor cost.

The result must preserve conflicts long enough to adjudicate them against authority and evidence. Do not vote.

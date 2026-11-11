# Version 2 — native runner and stronger contracts

- Replaced Docker/Compose with a Python loopback runner, process cleanup and a
  project lock. Added a native end-to-end suite with persistent evidence.
- Retained all three challenge themes and the separate security/functionality gates.
- Revised challenge 03 to actual filesystem-mode/owner checks and current-user I/O,
  explicitly removing the unverified claim of separate-UID access testing.
- Added checkpoint creation/umask and shared-public-status requirements to 03.
- Added manager scope, indirect receipts, protected-field updates and graded
  correlated denial logs to 01.
- Required key rotation, old-key rejection and deployed backup removal for 02.
- Randomized fixture IDs, values, tokens, receipt references and demo keys at reset;
  added sampled tests over several fixture shapes and more inadequate fixes.
- Kept written findings mandatory and participant evaluation separate/unfilled.

This is an assisted reference implementation. See BUILD_VALIDATION.md for the
actual execution record, and do not equate supplied code with independent authorship.

# Additional validation attempt — 2026-11-11

A later repeat of `tests/validate.py` was attempted after the successful retained run.

- Contract suite: completed and printed `contracts: PASS`.
- Native E2E: did not complete in this repeat. Its baseline launcher log shows the temporary runner announced challenge 01 and challenge 02, then the process was interrupted while waiting for service startup. The outer execution session reached its 180-second limit.
- This interrupted attempt is **not** counted as a passing native run and is not evidence that challenge 03 failed a security assertion; no completed checker result was produced for that phase.
- The earlier complete wrapper run remains separately preserved in `validation-summary.json` and `native/summary.json`: both suites exited 0, with 27 contract tests passing and native baseline/reference/restart/reset phases passing.

Recommendation: repeat the wrapper on a clean Linux/WSL environment if reproducibility across environments is a release requirement. Do not overwrite the successful run's logs with this incomplete attempt.

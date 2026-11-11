# Executed validation — native version 2

The final results are in [`evaluation/validation/`](../evaluation/validation/).
They were produced by executing the shipped test code, not by filling a results
template. This record supersedes the old unexecuted container plan.

Environment: Linux, Python **3.12.14**, regular UID **1000**. No root, secondary
OS account, container runtime or external target was used.

Command:

```sh
python3 tests/validate.py --output-dir evaluation/validation
```

**27 tests pass**, including subcases across all three challenges. The native
end-to-end suite also passes. Exact timestamps, elapsed times, exit codes and
observations are retained in `summary.json`, `contracts.log`, and `native/`.

| Native phase | Observed result |
| --- | --- |
| Baseline, seed 91 | All three reproduce their defined defects and preserve functionality |
| Reference repair | All three pass security and functionality |
| Restart of repaired services | All three still pass |
| Read-only state counterexample | Checker exits 1: service functionality fails |
| Missing state counterexample | Checker exits 2: operational error, no flag |
| Reset, seed 117 | All three return to vulnerable behavior with fresh fixture values |

The baseline, repaired and restart reports each contain **339 assertions**;
the fresh reset contains **341**, because generated record counts differ. Refer
to the per-challenge JSON for the exact category and observation of each check.

Additional executed regressions include several randomized fixture shapes,
deny-all/admin-only/known-ID access policies, manager writes, indirect-reference
bypass, unsafe field binding, partial updates, disabled note updates, missing
denial logs, disabled downloads, extension blocklists, containment without key
rotation, retained backups, deleted config, symlink containment, unsafe group and
creation permissions, and overrestricted public-status traversal. Checkers restore
mutated invoice/counter state; reset snapshots source and prior fixtures.

The integration suite invokes the real `run_lab.py`, `manage.py` and `check.py`,
verifies rejection of reset while the runner is live, and confirms all three
ports can be rebound after shutdown. Temporary project copies are discarded. A fresh ZIP extraction was also launched
without resetting its shipped fixtures; all three baseline checks passed. See
`evaluation/validation/release-smoke.json`.

## What this does not establish

- Challenge 03 checks actual mode/owner metadata and current-user service I/O.
  **No separate OS identity attempted access.** It is not evidence of complete
  cross-user isolation, ACL correctness, or effective access through every ancestor.
- WSL, native Windows, macOS, and Python versions other than 3.12.14 were not tested.
  Linux/WSL with Linux filesystem storage is the documented target; native Windows
  modes are not supported.
- A GitHub Actions workflow is supplied, but no hosted CI execution is claimed.
- No classmates participated; the pilot protocol and results template are unfilled.
- Finite tests and randomized samples are not proof against arbitrary patches or
  malicious participants with control of the local grader and filesystem.

The completion flags and source hashes aid traceability. They do not prove who
wrote a patch, authenticate an assessment, or replace independent written review.

# Engineering evidence workspace

This workspace now contains AI-assisted technical findings and retained automated evidence for all three repairs. It does **not** claim that a human participant independently performed the investigation or that a facilitator has reviewed/scored the findings. See [`../ASSISTED.md`](../ASSISTED.md) for attribution boundaries.

## Challenge records

Each challenge directory contains:

- `finding.md`: technical finding based on source diffs and actual lab output; facilitator section remains pending.
- `patch.diff`: challenge-specific diff against `v2-baseline`.
- `before.json`: scoped result from the native vulnerable-baseline phase.
- `after.json`: scoped result from the fixed/reference phase.
- `restart.json`: scoped result after restarting the fixed services.

The full reports, final checker JSON (including technical flags/source hash), native suite summary, command transcript and contract-test log are under [`evidence/`](evidence/). The before/after reports are machine-generated and preserve run IDs, source hashes and checker observations.

## Validation status

The retained complete wrapper run is [`evidence/validation-summary.json`](evidence/validation-summary.json). It records both the 27-test contract suite and native end-to-end suite exiting successfully. Native phases cover baseline, reference repair, restart, negative controls and reset. A subsequent repeat attempt is also recorded in [`evidence/rerun-attempt.md`](evidence/rerun-attempt.md): contracts passed, but native startup stalled before a completed checker result. The earlier complete successful run is preserved separately. The current project validation evidence is local; it is not hosted GitHub Actions CI. See [`CI_RECORD.md`](CI_RECORD.md).

## Prediction and authorship boundary

[`BAD_FIX_PREDICTIONS.md`](BAD_FIX_PREDICTIONS.md) is intentionally not backfilled as if predictions had been made before testing. Retrospective alternatives and their test evidence are documented in each finding, but that is not preregistered experimental work.

## Remaining independent work

A facilitator must inspect the source diffs and evidence, assess the findings against the rubric, record feedback, and decide whether to accept the work as full completion. Challenge 03's evidence is POSIX metadata plus same-UID service I/O; no separate-UID isolation test is claimed. Hosted CI and pilot results are also not claimed.

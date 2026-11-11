# Technical finding 01: Authorization bypass and mass assignment

> **AI-assisted engineering record.** This document is based on the supplied reference repair, source diff and retained automated lab evidence. It is not represented as an independently authored participant investigation. Facilitator review and scoring remain intentionally unfilled.

Participant ID: Not applicable — no participant investigation is claimed
Date / environment: 2026-11-11; Linux x86_64; Python 3.13.5; Fix the System CTF v2
Highest hint used: Reference solution / substantial ChatGPT assistance
Classification: CWE-862 (Missing Authorization), CWE-639 (Authorization Bypass Through User-Controlled Key), and CWE-915 (Improperly Controlled Modification of Dynamically-Determined Object Attributes)

## Scope and trust boundary

Affected component: `challenges/01-authorization`. The relevant trust boundary is between untrusted HTTP requesters or processes and protected application data/filesystem resources. The intended legitimate behavior is retained; the repair is not a blanket deny.

## Before-fix reproduction and observed impact

The baseline checker report (`../evidence/native/baseline.json`) records `list_leak` witnesses for Alice, Bob, Casey and the manager; successful cross-scope invoice and receipt reads/writes; missing denial audit events; and mass-assignment witnesses for owner, team, amount, id and receipt. The baseline run retained all three challenges' results, with challenge 01 security failing while legitimate functionality passed. Synthetic fixture IDs are randomized; consult the JSON report rather than relying on IDs copied into prose.

- Baseline command executed by the native suite: `python3 tests/native_e2e.py --output-dir <evidence-dir>`; its baseline phase starts from a reset fixture and runs `python3 check.py --expect vulnerable --json ...`.
- Baseline run ID: `6b70a608-5ddb-454d-98a8-c15edf02c0d8`; source SHA-256: `1010cc810b4ec794497b4e3be3953801a8c65221e56280bfd2c01388ef04546b`; expected state: `vulnerable`; expectation met: `True`.
- Challenge 01 baseline gates: security=False, functionality=True, technical=False; baseline reproduced=True.
- Scoped evidence: [`before.json`](before.json). Full three-challenge report: [`../../evidence/native/baseline.json`](../../evidence/native/baseline.json).

## Root cause

The original policy treated any authenticated actor as authorized. The handler also applied the check only to direct invoice IDs; receipt-based lookup was a separate path that bypassed it. The update handler passed the request object into the invoice update operation after only checking the note field's type/length, allowing protected fields such as owner, team, amount, ID and receipt to be changed. Authorization must be based on server-owned actor role, identity, resource owner/team and operation, not merely on the presence of a bearer token.

## Alternatives considered and rejected

| Alternative | Predicted security effect | Predicted functionality effect | Evidence / reason rejected |
| --- | --- | --- | --- |
| Any authenticated actor | Still permits cross-tenant access | Keeps routes working | Rejected: baseline witnesses and contract tests show authentication is not authorization. |
| Deny every request except admin | Blocks the demonstrated attack | Breaks normal user and manager workflows | Rejected: contract tests `test_deny_all_and_admin_only_fail_functionality` and `test_manager_write_privileges_fail` preserve intended role boundaries. |
| Check only direct invoice IDs | Blocks direct lookup only | Receipt lookup still works | Rejected: contract test `test_correct_policy_with_indirect_bypass_fails` exercises the alternate lookup path. |
| Validate `note` but pass the full body to `update` | Leaves protected-field mutation possible | Appears to retain updates | Rejected: contract tests cover mass assignment and partial mutation before rejection. |

## Repair and patch

`can_access` now rejects missing actors and unknown operations, grants admin access, restricts managers to read-only access within their team, and restricts ordinary users to their own invoices. The handler invokes this policy for both direct invoice and indirect receipt lookups. `apply_patch` accepts exactly one `note` field, validates it before mutation, and assigns only that field, preventing partial mutation and mass assignment.

The challenge-specific diff is retained in [`patch.diff`](patch.diff).

## After-fix evidence and regression checks

- Fixed-state run ID: `917a3fd9-e4ff-4cf7-9420-3c86e13b53b9`; source SHA-256: `995911f993bd9826e2b5accafcbb9577365d04612f6b3657da6a120804eee32c`; expected state: `fixed`; expectation met: `True`.
- Challenge 01 fixed gates: security=True, functionality=True, technical=True; baseline reproduced in fixed state=False.
- Restart run ID: `eed39d5c-d19f-40f8-bbb1-70dd5fa4c274`; same source SHA-256: `995911f993bd9826e2b5accafcbb9577365d04612f6b3657da6a120804eee32c`; challenge gates after restart: security=True, functionality=True, technical=True.
- The final native `check.py --expect fixed --json` run ID was `4860887a-8c19-43bd-aba1-1e514e81ef90`, source SHA-256 `45b99110d90915f30d1dede7a4ec51128a4b11e1a40f7843a6029b173a38b62a`; technical flag: `FLAG{repair_01_00a0895f4a33}`.
- Evidence: [`after.json`](after.json), [`restart.json`](restart.json), and full reports under [`../../evidence/native/`](../../evidence/native/).

The automated suite checks multiple generated identities and object shapes, direct and receipt routes, audit denials, legitimate reads/writes, note restoration, and rejected protected-field updates. The native end-to-end `reference` and `restart` phases each report security, functionality and technical gates as passing for challenge 01.

The local fixture model is not a substitute for production IAM, policy centralization, tenant isolation, concurrency controls or a complete API authorization review. This work was performed with substantial ChatGPT/AI assistance; it is not a claim of an independent participant investigation. The baseline and repair reports are automated evidence, not a human-authored transcript.

## Facilitator review — pending independent reviewer

| Criterion | Score |
| --- | --- |
| Reproduction and impact | Pending /2 |
| Root cause and classification | Pending /3 |
| Repair rationale | Pending /2 |
| Regression evidence | Pending /2 |
| Clarity and limits | Pending /1 |
| Total | Pending /10 |

Technical gates verified from trusted grader: **Yes — automated technical gates passed**
Accepted as full completion: **Pending facilitator decision**
Reviewer / date / feedback: Pending

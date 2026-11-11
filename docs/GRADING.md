# Pass contracts and review rubric

Each challenge has `security` and `functionality` assertion groups. Both must
pass without errors to produce a technical flag. The written finding is required
separately. The grader reports observations, baseline witnesses, a run ID,
timestamp and source/fixture hash; it never marks a prose submission accepted.

| Challenge | Security | Functionality |
| --- | --- | --- |
| 01 | Authentication; exact list scope; denied direct/receipt reads and writes; no protected-field or partial updates; correlated denial logs without tokens | Own/admin access; manager team reads; valid note changes; restoration; missing-resource log distinct from denial |
| 02 | Canonical public containment; key changed; old signatures rejected; backup and deployed old-key copies absent; invalid signatures rejected | Exact public downloads including randomized name/content; runtime catalog; current signing and verification; missing file 404 |
| 03 | Real owner/mode policy before and after checkpoint creation; no group/other access to private files; no shared-directory or public-file group/other writes; no special bits | Current-user read/write/checkpoint; public read/traversal mode contract; checker restores counter |

`--expect fixed` is the default. `--expect vulnerable` succeeds only when all
recorded defect witnesses occur, functionality passes, and there are no errors.
For 01/02 the witnesses are unauthorized HTTP behavior and key exposure/use. For
03 they are unsafe **mode assignments**, not demonstrated reads by another UID.

Exit status: 0 = requested state observed; 1 = contract mismatch; 2 = operational
or evidence error. A refusal to connect, missing file or unavailable audit log is
never a successful access denial. The security assertion changes from FAIL to
PASS after repair; it is the attack attempt, not the assertion, that should fail.

The permissions policy is stricter than a full effective-access calculation:
broad bits fail even if a restrictive ancestor would mask them. Conversely,
mode checks do not prove access for a different identity. Extended ACLs are
inconclusive in this exercise and produce an error. Public status shareability is
also a metadata contract, not a separate-user read claim.

## Written finding: 10 points per challenge

| Criterion | Points | Evidence |
| --- | --- | --- |
| Reproduction and impact | 2 | Actual local observations; for 03 distinguish unsafe modes from hypothetical cross-user impact |
| Root cause and classification | 3 | Affected component, trust boundary, wrong decision and defensible CWE mapping |
| Repair rationale | 2 | Patch/diff and reasoning that generalizes beyond fixture values |
| Regression evidence | 2 | Before/after JSON, preserved operation and restart results |
| Clarity and limits | 1 | Reproducible commands, limits, hints and assistance disclosure |

Full completion requires technical PASS, at least **8/10**, and at least **2/3**
for root cause. Strong prose cannot compensate for broken functionality.

A facilitator should use a trusted grader, reset to fresh fixtures, inspect only
scoped challenge changes, and reject hardcoded results or changes to assessment
inputs. Reference solutions and this guide can be removed from participant copies
for an unaided exercise. Local flags are forgeable markers, not a scoreboard.

Logging checks are included in challenge 01's security gate. Counting denials by
actor/time or sending a lab-only stream to a SIEM remains an optional extension.
Do not map ordinary denial events to a specific adversary technique without
additional evidence.

# Finding: [challenge number and title]

Participant ID: [pseudonym]
Date / environment: [date; Linux/WSL details; Python version; project version]
Highest hint used: [none / 1 / 2 / 3 / reference solution]

## Classification and scope

- CWE and reason for mapping:
- Affected component, file, and function/policy:
- Attacker identity and access before exploitation:
- Intended trust boundary and legitimate behavior:

## Before-fix reproduction

1. Reset/start command:
2. Minimal local request or filesystem-metadata observation:
3. Observed response/output:
4. Impact demonstrated (for 03, observed mode assignment versus inferred access):
5. Baseline report path and relevant failed security assertion:

Include a short transcript using only the lab's synthetic data.

## Root cause

Explain why the original decision was wrong. Identify what the server or OS
trusted, which check/permission was missing or excessive, and how the supplied
input or identity crossed the boundary. Do not merely restate the symptom.

## Repair

Include a patch/diff and explain why it handles other users, IDs, filenames, or
untrusted processes rather than only the reproduced example.

## After-fix evidence and regression checks

- Checker command, exit code, and after-report path:
- Original attack result after repair:
- Successful legitimate operation, with observed result:
- Result after stopping and restarting the native runner:
- Technical flag, source hash and run ID:

## Limits and assistance

List assumptions, untested cases, hint/solution use, tools or AI assistance, and
anything you would change for a production implementation.

## Facilitator review

Leave this section for the reviewer.

| Criterion | Score |
| --- | --- |
| Reproduction and impact | /2 |
| Root cause and classification | /3 |
| Repair rationale | /2 |
| Regression evidence | /2 |
| Clarity and limits | /1 |
| Total | /10 |

Technical gates verified from trusted grader: [yes/no]
Accepted as full completion: [yes/no]
Reviewer / date / feedback:

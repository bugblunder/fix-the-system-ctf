# Optional small participant evaluation

This protocol is a template. **No classmates have been evaluated in this
delivery, and no participant results are supplied.** Keep this study separate
from the automated implementation validation.

## Procedure

1. Invite 3–5 willing classmates and explain what will be recorded. Use pseudonyms.
2. Give each the same release and baseline, participant guide, and finding template.
3. Record broad prior experience and chosen challenge order. Rotate order across
   participants if practical and disclose the order used.
4. Start each challenge's clock after environment setup is complete. Record
   infrastructure interruptions separately and pause the working-time clock.
5. Allow up to 60 working minutes per challenge, including the finding. Participants
   may stop sooner. Record unfinished attempts as unfinished rather than assigning
   a fictional completion time. Hint level 1–3 is available on request.
6. Ask them to save each checker report after submitting a patch. Record the first
   concrete impact demonstration and first technical pass. Review the finding
   independently using the same rubric.
7. Ask one debrief question: "Which step was unclear or most likely to break
   legitimate behavior?" Record a brief anonymized answer.

## Metric definitions

| Metric | Definition |
| --- | --- |
| Time to demonstrated impact | Working minutes from challenge start to the first reproducible unauthorized read/write, config disclosure, or unsafe mode observation (03) |
| Time to technical repair | Working minutes from challenge start to the first report with both technical gates passing |
| Time to full submission | Working minutes from challenge start until the participant submits the written finding; reviewer time excluded |
| Patch attempts | Number of checker runs on modified challenge files; baseline run excluded |
| Functionality-breaking attempts | Patch attempts with at least one functionality failure, regardless of security result |
| Secure but broken attempts | Patch attempts with security PASS and functionality FAIL |
| Hint level | Highest of none, 1, 2, or 3; reference-solution access recorded separately |
| Full completion | Technical pass plus accepted finding per the rubric |

Use `not reached` for milestones that did not occur within the time limit. Record
environment interruptions, voluntary stops, reference-solution access, and any
protocol deviations. Do not count infrastructure errors as broken fixes.

## Analysis

Report participant count and completed/attempted challenges first. For each
challenge, show completion count, raw times or median/range among completers,
hint levels, and how many patch attempts broke functionality. State the number
excluded from each timing summary because the milestone was not reached. With
3–5 participants, favor the individual rows and qualitative observations over
statistical claims. Disclose small sample, convenience recruitment, prior
experience, order effects, and possible hint/solution influence.

Do not claim causality or broad learning improvement from this pilot. Its purpose
is to identify challenge ambiguity and whether the repair-plus-functionality
requirement reveals mistakes worth discussing.

For version 2, use Linux or WSL with Linux filesystem storage. Log setup time separately.
Challenge 03 measures identification and repair of an unsafe permission policy; do not
record a mode observation as demonstrated access by another OS account.

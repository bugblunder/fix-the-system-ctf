# A 4–6 week project plan

Question: **Can a participant repair a vulnerability while preserving the
application's intended behavior?** The implementation enables investigation;
your portfolio argument comes from work and evidence you can explain.

| Week | Work | Exit evidence |
| --- | --- | --- |
| 1 | Run the native lab and tests; inspect trust boundaries; reproduce all baseline defects | Environment record, baseline JSON, HTTP examples and permission-mode observations |
| 2 | Write your own repairs and findings; compare each against the behavior contract | Three diffs, three findings, fixed JSON and legitimate-operation examples |
| 3 | Challenge the grader with bad fixes; test several fixture shapes; review denial logs; restart and reset | Counterexample table, regression logs, source review and limitations |
| 4 | Reproduce from a clean extraction; refine documentation and record a five-minute walkthrough | Release, final report, before/after evidence and demonstration |
| 5 (optional) | Run the separate protocol with 3–5 willing classmates | Anonymized observed data, hint use, saved reports and reviewed findings |
| 6 (optional) | Analyze pilot results and refine unclear hints/contracts | Descriptive results with denominators and explicit limitations |

Keep automated implementation validation separate from the participant study.
No pilot data is supplied. Do not describe supplied reference patches or
assistant-generated code as your independent work. Record what you implemented,
changed, tested and learned, plus the help you used.

Suggested final report: question and scope; architecture and trust boundaries;
three before/root-cause/repair/regression case studies; automated evaluation;
optional pilot; limits and authorship disclosure. For challenge 03 explicitly
state that metadata and same-user I/O replace independent OS-identity testing.

For a short demo, show an unauthorized request, explain the code defect, apply a
repair, restart, show the request denied, and show an allowed operation succeed.
Open the written finding and checker report. Then reset to reproduce the flaw.
Repeat the complete evidence process for every challenge in the report.

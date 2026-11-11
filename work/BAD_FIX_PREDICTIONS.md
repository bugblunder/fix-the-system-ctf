# Bad-fix predictions — unfilled

Write and commit a prediction before running each experiment. Do not overwrite
an incorrect prediction after observing the result. Fill the actual column only
from the saved checker output, including exit code and evidence path.

Use PASS/FAIL for the security and functionality gates. Record operational errors
as ERROR, not as a successful denial or a broken-feature result. Predict both
gates even if your patch targets only one. No test cases have been supplied here.

| Patch idea | Predicted security result | Predicted functionality result | Actual result and report path |
| --- | --- | --- | --- |

## Notes for each experiment

Use one short entry per case: prediction commit; implementation/test commit;
reasoning; command; observed discrepancy (if any); revised understanding; assistance.
Keep the original row when your prediction was wrong.

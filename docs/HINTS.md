# Progressive hints

Record the highest level opened for each challenge.

## 01 · Whose invoice?

<details><summary>Hint 1 — Follow every lookup</summary>

A valid token identifies a caller. Compare list, direct ID, receipt ID and PATCH
paths. Which of these actually authorizes the resolved invoice?

</details>
<details><summary>Hint 2 — Separate role, scope and operation</summary>

A manager may read a team invoice but may not change it. A caller's editable
payload must not change ownership, team or amount. Reject mixed updates atomically.

</details>
<details><summary>Hint 3 — Keep policy and enforcement consistent</summary>

Filter lists and enforce reads/writes after both lookup types. Derive scope from
server-side actor and invoice fields. Allow only the note field, validating the
entire request before mutation. Emit denial logs with request correlation IDs.

</details>

## 02 · The forgotten backup

<details><summary>Hint 1 — Inspect the permitted tree</summary>

Containing requests inside the whole site still includes private configuration.
Find the intended public root.

</details>
<details><summary>Hint 2 — Containment is only part of remediation</summary>

Resolve before checking containment; an extension blocklist is incomplete. Once
a key has leaked, blocking its URL does not make the old key unusable.

</details>
<details><summary>Hint 3 — Preserve runtime behavior</summary>

Keep private runtime config, generate a fresh random signing key, remove the
backup and deployed old-key copies. New signatures must verify and old signatures
must fail. Do not delete config or disable signing/downloads.

</details>

## 03 · Who can touch this file?

<details><summary>Hint 1 — Inspect real files</summary>

Compare mode bits on private state, its directory, the exchange directory and
checkpoints. The evidence here is permission assignment, not a guest-user probe.

</details>
<details><summary>Hint 2 — Check new files too</summary>

A checkpoint replaces a file with a newly created one. What controls the mode of
that new file? Removing only world access can leave group access intact.

</details>
<details><summary>Hint 3 — Preserve the shared public status</summary>

Use owner-only private state and a restrictive creation mask, while retaining
read/traversal bits needed by public status. Repair startup policy and verify it
after restart; a one-off chmod is insufficient.

</details>

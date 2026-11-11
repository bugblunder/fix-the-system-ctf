# Sources and design notes

The following primary references inform the design; they are not independent
validation of the code. Authorization, secret-remediation and filesystem
references were consulted for the native revision on 11 November 2026.

- [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html): validate authorization at every relevant access point.
- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html): containment after exposure includes revocation, rotation and removal of exposed copies.
- [MITRE CWE-639](https://cwe.mitre.org/data/definitions/639.html): authorization bypass through a user-controlled key.
- [MITRE CWE-915](https://cwe.mitre.org/data/definitions/915.html): uncontrolled modification of dynamically determined object attributes.
- [MITRE CWE-530](https://cwe.mitre.org/data/definitions/530.html) and [CWE-538](https://cwe.mitre.org/data/definitions/538.html): exposed backups and sensitive files.
- [MITRE CWE-732](https://cwe.mitre.org/data/definitions/732.html): incorrect permission assignment for critical resources.
- [Linux path resolution](https://man7.org/linux/man-pages/man7/path_resolution.7.html): actual access depends on identity and path traversal as well as file mode.
- [Linux ACLs](https://man7.org/linux/man-pages/man5/acl.5.html): extended access rules need more than a simplified mode-only policy check.
- [Python os.chmod](https://docs.python.org/3.12/library/os.html#os.chmod): Windows chmod does not implement the POSIX mode model required by this exercise.
- [Python http.server](https://docs.python.org/3/library/http.server.html): the dependency-free lab server is not a production deployment recommendation.

All identities, keys, records and secrets are synthetic. The local fixture store
and grader are trusted. Randomized values improve test coverage but do not create
a secret grading environment. The lab does not scan or interact with external
targets. Native processes run under the user's account; there is no container or
OS-user isolation boundary around them.

# Security Policy

## Supported versions

Security fixes target the latest published release and the current `main` branch. Older versions may receive a fix when the issue affects the stable `1.x` public contract and the correction can be backported safely.

## Reporting a vulnerability

Do not open a public issue for vulnerabilities, leaked secrets, private data exposure, unsafe path handling, or a bypass of authorization and confirmation boundaries.

Use the repository host's private vulnerability-reporting feature. If private reporting is unavailable, email [support@complexenough.com](mailto:support@complexenough.com) with the subject prefix `[SECURITY]`. Include:

- the affected version or commit;
- the smallest reproducible case;
- the expected and observed behavior;
- impact and required preconditions;
- whether any secret or personal data was exposed.

Do not include real secrets or unrelated private data. Support is best effort with no guaranteed response or resolution time. A maintainer will try to acknowledge the report privately, reproduce it, coordinate a fix and disclosure window, and credit the reporter when requested and appropriate.

## Scope notes

The current release is a skills-only package with no publisher-controlled server, authentication, telemetry, or remote storage. Reports about OpenAI account or platform security should be sent through OpenAI's official security channel rather than this project.

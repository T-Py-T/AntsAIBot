# Security policy

## Supported versions

Security fixes are applied to the current `main` branch. The repository does
not yet publish a long-term-support release line.

## Reporting a vulnerability

Please use GitHub's private vulnerability-reporting form for this repository
rather than opening a public issue. Include the affected revision, a minimal
reproduction, expected impact, and any suggested mitigation.

Do not include credentials, private replay data, or other sensitive material
in issues, pull requests, logs, or retained benchmark artifacts.

This project executes locally supplied bot processes. Treat untrusted bots as
untrusted code: use a disposable environment, keep networking disabled when
possible, and do not mount credential-bearing directories into the runtime.

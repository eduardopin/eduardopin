# Security Policy

## Reporting

Open an issue for documentation or example problems that do not expose sensitive data. For anything that could reveal credentials, internal endpoints or exploitable configuration, contact the maintainer privately before publishing details.

## Public-Safe Content

- Do not commit secrets, account IDs, customer names or internal hostnames.
- Use placeholders such as `example-account`, `example.com` and `us-east-1`.
- Prefer least-privilege examples and call out any elevated permissions.
- Review generated artifacts before committing them.

## Supported Scope

Security review covers examples, workflows, scripts and documentation in this repository. Production deployment hardening remains the responsibility of the adopting team.

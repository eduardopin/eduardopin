# Reliability Model

## Reliability Goals

Examples should be understandable, repeatable and easy to roll back. Automation should fail closed when validation cannot determine a safe result.

## Failure Modes

- Missing environment variables or credentials.
- Provider/API throttling.
- Incomplete tagging or ownership metadata.
- Manual changes outside the documented workflow.
- Assumptions that differ between development and production environments.

## Recovery Practices

Keep changes small, capture command output during validation and document rollback steps next to operational procedures.

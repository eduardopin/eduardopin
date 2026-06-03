# Security Guidance

## Baseline Controls

- Keep credentials outside the repository.
- Use short-lived identity where possible.
- Validate infrastructure and workflow changes before merge.
- Record exceptions with owner, reason and expiration date.

## Review Checklist

- Are permissions scoped to the task?
- Are inputs validated before use?
- Are logs free of sensitive values?
- Can the workflow run safely from forks or pull requests?
- Does documentation identify residual risk?

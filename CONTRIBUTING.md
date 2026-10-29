# Contributing to NER-LIS

Thank you for contributing to NER-LIS.

NER-LIS is developed as a collaborative engineering project, so code quality, documentation and integration are important.

## Development Process

1. Check existing GitHub Issues before starting work.
2. Create or assign yourself an issue.
3. Create a feature branch.
4. Implement the change.
5. Add tests where applicable.
6. Update documentation when behavior changes.
7. Open a Pull Request.
8. Request review from another team member.
9. Resolve review comments.
10. Merge only after checks pass.

## Branch Naming

Use descriptive names:

```text
feat/dashboard-map
feat/incident-api
feat/disruption-model
feat/risk-routing
feat/offline-sync
fix/gps-validation
docs/api-documentation
```

## Commit Convention

Use:

```text
feat: add road accessibility layer
fix: handle duplicate incident reports
docs: update API documentation
test: add routing scenarios
refactor: simplify shipment service
chore: update dependencies
```

## Pull Requests

Every PR should include:

* What changed
* Why it changed
* How it was tested
* Screenshots for UI changes
* Related issue number

Avoid large unrelated changes in one PR.

## Code Quality

Before opening a PR:

* Run tests
* Check formatting
* Remove debug code
* Do not commit secrets
* Update documentation where required
* Verify that existing functionality still works

## Data and ML

For ML changes, document:

* Dataset/version
* Feature changes
* Model changes
* Evaluation metrics
* Baseline comparison
* Known limitations

Do not report model results without reproducible evaluation.

## Security

Never commit:

* API keys
* passwords
* tokens
* private certificates
* production credentials

Report security issues privately rather than publishing sensitive information in a public issue.

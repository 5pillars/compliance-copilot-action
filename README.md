# 6pillars Compliance Copilot

## Features

## Requirements

The following is an example GitHub Actions workflow:

```yaml
on:
  pull_request:
    types: [opened, reopened, synchronize]
jobs:
    compliance-copilot:
      runs-on: ubuntu-latest
      environment: production
      permissions:
        contents: read
        issues: write
        pull-requests: write
      steps:
      - uses: actions/checkout@v4

      - uses: 5pillars/compliance-copilot-action@v1.0.0
        env:
            SIXPILLARS_API_TOKEN: ${{ secrets.SIXPILLARS_API_TOKEN }}
            GITHUB_TOKEN: ${{ github.token }}
            GITHUB_REPOSITORY: $GITHUB_REPOSITORY
            PULL_REQUEST_NUMBER: ${{ github.event.pull_request.number }}
        with:
            minimumSeverity: 'CRITICAL'
```

## Parameters

## Secrets

## License

MIT License

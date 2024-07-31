# 6pillars Compliance Copilot

## Features

## Requirements

The following is an example GitHub Actions workflow:

```yaml
on:
  pull_request:
    types: [opened, reopened, synchronize]
jobs:
    6pillars-compliance-copilot:
    runs-on: ubuntu-latest
    name: compliance-copilot-action
    env:
      GITHUB_TOKEN: ${{ github.token }}
    permissions:
      contents: read
      issues: write
      pull-requests: write
    steps:
    - name: Checkout repo
        uses: actions/checkout@v4
    - name: 6pillars ComplianceCopilot Github Action
        id: 6pillars
        uses: 5pillars/compliance-copilot-action@v1.0.0
        env:
            SIXPILLARS_API_TOKEN: ${{ secrets.SIXPILLARS_API_TOKEN }}
            GITHUB_TOKEN: ${{ github.token }}
            GITHUB_REPOSITORY: $GITHUB_REPOSITORY
            PULL_REQUEST_NUMBER: ${{ github.event.pull_request.number }}
```

## Parameters

## Secrets

## License

MIT License

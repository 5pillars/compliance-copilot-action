# 6pillars Compliance Copilot

## Features
- Infrastructure-as-Code Security Checks
- Out-of-the-box compliance regulations including AWS CIS, AWS Well-Architected, AWS Secure Landing Zone, SOC2, ISO27001, NIST & PCI-DSS
- AI-generated code suggestions for AWS CloudFormation and AWS Terraform templates
- Support for file extensions .tf, .tf.json, .tfvars, .yml, .json, .yaml, .dockerfile, .txt, .template


## Requirements

To run a scan on your code, you need access to [6pillars platform](https://app.6pillars.ai) and obtain an API key.

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
            skipPullRequestComments: true
            folderPath: /
            excludeFolder: .github

```

## Parameters
- `minimumSeverity` - **_(Required)_** The threshold at which the detected finding severity level  will cause your workflow to fail. One of `NONE`, `LOW`, `MODERATE`, `HIGH`, or `CRITICAL`.
- `skipPullRequestComments` - **_(Optional)_** Do you like skip pull request file level comments ?. Defaults to false.
- `folderPath` - **_(Optional)_** Specific folder path to search file changes. Defaults to /.
- `excludeFolder` - **_(Optional)_** Specific folder to avoid being scanned. Defaults to .github
  
## Secrets

- `SIXPILLARS_API_TOKEN` - **_(Required)_** This is the API key for your 6pillars Compliance Copilot action workflow. The API key can be obtained from [6pillars API KEY Generation Page](https://app.6pillars.ai/profile)
- `GITHUB_REPOSITORY`: $GITHUB*REPOSITORY - \*\**(Optional)\_\*\* Your GitHub Repository referenced in the Pipeline.
- `GITHUB_TOKEN`: ${{ secrets.GITHUB_TOKEN }} - **_(Optional)_** Your GitHub Token.
- `PULL_REQUEST_NUMBER`: ${{ github.event.pull_request.number }} - Your pull request number to add comments

## License

MIT License

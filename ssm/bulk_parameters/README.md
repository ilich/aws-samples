# bulk-parameters

A CLI tool that bulk exports AWS SSM Parameter Store parameters to a CSV file, and bulk imports them back from a CSV file.

## What it does

- `pull` — finds every parameter whose name starts with the given prefix (recursively) and writes `name`, `value` and `type` (`String`, `StringList` or `SecureString`) to a CSV file, decrypting `SecureString` values along the way.
- `push` — reads `name`, `value` and `type` from a CSV file and creates or updates each parameter in SSM Parameter Store (`Overwrite=True`). The parameter type is preserved as-is from the CSV. Use `--dry-run` to preview what would be written without making any changes.

## Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- AWS credentials configured (profile, environment variables, or instance role)

## CSV format

| Column | Description |
| --- | --- |
| `name` | Full SSM parameter path, e.g. `/my-app/db/password` |
| `value` | Parameter value (decrypted for `SecureString`) |
| `type` | `String`, `StringList`, or `SecureString` |

## Installation

```sh
uv tool install .
```

After installation the `ssm-bulk` command is available globally. To upgrade after pulling new changes, re-run the same command.

## Usage

### pull

```sh
ssm-bulk pull PREFIX [--file parameters.csv] [--profile PROFILE] [--region REGION]
```

| Argument / option | Description |
| --- | --- |
| `PREFIX` | SSM Parameter Store path prefix, e.g. `/my-app/` |
| `--file`, `-f` | CSV output file path (default: `parameters.csv`) |
| `--profile` | AWS profile name (defaults to the standard AWS credential chain) |
| `--region` | AWS region name (defaults to the profile/environment configuration) |

### push

```sh
ssm-bulk push [--file parameters.csv] [--profile PROFILE] [--region REGION] [--dry-run]
```

| Option | Description |
| --- | --- |
| `--file`, `-f` | CSV input file path (default: `parameters.csv`) |
| `--profile` | AWS profile name (defaults to the standard AWS credential chain) |
| `--region` | AWS region name (defaults to the profile/environment configuration) |
| `--dry-run` | Print parameters that would be written without making any changes to SSM |

## Examples

```sh
# Export all parameters under /my-app/ to my-app.csv
ssm-bulk pull /my-app/ --profile dev --region us-east-1 --file my-app.csv

# Preview what would be imported (no changes made)
ssm-bulk push --profile dev --region us-east-1 --file my-app.csv --dry-run

# Import parameters from a CSV file, creating or updating them in SSM
ssm-bulk push --profile dev --region us-east-1 --file my-app.csv
```

## Development

```sh
uv sync          # set up the virtual environment
uv run ssm-bulk  # run without installing globally
make lint        # ruff format/check + mypy
```

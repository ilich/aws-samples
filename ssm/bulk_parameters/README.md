# bulk-parameters

A CLI tool that bulk exports AWS SSM Parameter Store parameters to a CSV file, and bulk imports them back from a CSV file.

## What it does

- `pull` — finds every parameter whose name starts with the given prefix (recursively) and writes `name`, `value`, `type` (`String`, `StringList` or `SecureString`) and `keep` to a CSV file, decrypting `SecureString` values along the way.
- `push` — reads `name`, `value` and `type` from a CSV file and creates or updates each parameter in SSM Parameter Store (`Overwrite=True`). The parameter type is preserved as-is from the CSV. Use `--dry-run` to preview what would be written without making any changes.
- `merge` — merges a changes CSV into a base CSV: parameters only in the changes file are added, parameters in both are updated (unless `keep` is `True` in the base file, in which case the base value/type is preserved), and parameters only in the base file are dropped from the output.

All CSV output (from both `pull` and `merge`) is written sorted by `name`.

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
| `keep` | `True` or `False` (default). When `True` in the base file passed to `merge`, the existing value/type is preserved instead of being overwritten by the changes file. If a CSV has no `keep` column at all, rows read from it default to `True` (treated as protected); this only affects `push`/`merge` reads — `pull` always writes freshly fetched parameters with `keep=False`. |

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

### merge

```sh
ssm-bulk merge BASE CHANGES [--output parameters.csv]
```

| Argument / option | Description |
| --- | --- |
| `BASE` | Base CSV file path |
| `CHANGES` | Changes CSV file path |
| `--output`, `-o` | Output CSV file path (default: `parameters.csv`) |

## Examples

```sh
# Export all parameters under /my-app/ to my-app.csv
ssm-bulk pull /my-app/ --profile dev --region us-east-1 --file my-app.csv

# Preview what would be imported (no changes made)
ssm-bulk push --profile dev --region us-east-1 --file my-app.csv --dry-run

# Import parameters from a CSV file, creating or updating them in SSM
ssm-bulk push --profile dev --region us-east-1 --file my-app.csv

# Merge a staging changes file into the current parameters, keeping any
# parameter marked keep=True in parameters.csv untouched
ssm-bulk merge parameters.csv staging_parameters.csv --output parameters.csv
```

## Development

```sh
uv sync          # set up the virtual environment
uv run ssm-bulk  # run without installing globally
make lint        # ruff format/check + mypy
```

from pathlib import Path

import typer

from app.csv_io import read_csv, write_csv
from app.ssm import fetch_parameters, get_ssm_client, put_parameters

app = typer.Typer(add_completion=False)


@app.command()
def pull(
    prefix: str = typer.Argument(..., help="SSM Parameter Store path prefix, e.g. /my-app/"),
    file: Path = typer.Option(Path("parameters.csv"), "--file", "-f", help="CSV file path"),
    profile: str | None = typer.Option(None, "--profile", help="AWS profile name"),
    region: str | None = typer.Option(None, "--region", help="AWS region name"),
) -> None:
    """Export SSM parameters starting with PREFIX to a CSV file."""
    client = get_ssm_client(profile=profile, region=region)
    records = fetch_parameters(client, prefix)
    write_csv(file, records)
    typer.echo(f"Saved {len(records)} parameter(s) starting with '{prefix}' to {file}")


@app.command()
def push(
    file: Path = typer.Option(Path("parameters.csv"), "--file", "-f", help="CSV file path"),
    profile: str | None = typer.Option(None, "--profile", help="AWS profile name"),
    region: str | None = typer.Option(None, "--region", help="AWS region name"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print parameters without writing to SSM"),
) -> None:
    """Import SSM parameters from a CSV file, creating or updating each one."""
    records = read_csv(file)
    if dry_run:
        for record in records:
            typer.echo(f"{record.name}  ({record.type})  {record.value}")
        typer.echo(f"Dry run: {len(records)} parameter(s) would be written to SSM Parameter Store")
        return
    client = get_ssm_client(profile=profile, region=region)
    put_parameters(client, records)
    typer.echo(f"Wrote {len(records)} parameter(s) from {file} to SSM Parameter Store")


@app.command()
def merge(
    base: Path = typer.Argument(..., help="Base CSV file path"),
    changes: Path = typer.Argument(..., help="Changes CSV file path"),
    output: Path = typer.Option(Path("parameters.csv"), "--output", "-o", help="Output CSV file path"),
) -> None:
    """Merge changes CSV into base CSV: add new, update existing, remove missing."""
    base_records = {r.name: r for r in read_csv(base)}
    changes_records = {r.name: r for r in read_csv(changes)}

    added, updated, removed = 0, 0, 0
    for name in changes_records.keys() - base_records.keys():
        typer.echo(f"  add     {name}")
        added += 1
    for name in changes_records.keys() & base_records.keys():
        before, after = base_records[name], changes_records[name]
        if before.keep:
            after.value = before.value
            after.type = before.type
            typer.echo(f"  keep    {name}  (keep=True, skipping update)")
            continue

        diff = ""
        if before.value != after.value:
            diff += f"  {before.value!r} -> {after.value!r}"
        if before.type != after.type:
            diff += f"  (type: {before.type.value} -> {after.type.value})"
        typer.echo(f"  change  {name}{diff}")
        updated += 1
    for name in base_records.keys() - changes_records.keys():
        typer.echo(f"  remove  {name}")
        removed += 1

    write_csv(output, list(changes_records.values()))
    typer.echo(f"Merged to {output}: +{added} added, ~{updated} updated, -{removed} removed")


def main() -> None:
    app()


if __name__ == "__main__":
    main()

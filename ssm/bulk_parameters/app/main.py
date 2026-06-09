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


def main() -> None:
    app()


if __name__ == "__main__":
    main()

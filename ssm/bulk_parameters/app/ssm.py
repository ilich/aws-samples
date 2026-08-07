from collections.abc import Iterable
from typing import Any

import boto3
import typer

from app.models import ParameterRecord, ParameterType


def get_ssm_client(profile: str | None, region: str | None) -> Any:
    session = boto3.Session(profile_name=profile, region_name=region)
    return session.client("ssm")


def fetch_parameters(client: Any, prefix: str) -> list[ParameterRecord]:
    records: list[ParameterRecord] = []
    paginator = client.get_paginator("get_parameters_by_path")
    for page in paginator.paginate(Path=prefix, Recursive=True, WithDecryption=True):
        for parameter in page["Parameters"]:
            records.append(
                ParameterRecord(
                    name=parameter["Name"],
                    value=parameter["Value"],
                    type=ParameterType(parameter["Type"]),
                    keep=False,  # Default to False; user can set to True in CSV if desired
                )
            )

            typer.echo(f"Fetched parameter: {parameter['Name']}  ({parameter['Type']})")

    return records


def put_parameters(client: Any, records: Iterable[ParameterRecord]) -> None:
    for record in records:
        client.put_parameter(
            Name=record.name,
            Value=record.value,
            Type=record.type.value,
            Overwrite=True,
        )

        typer.echo(f"Put parameter: {record.name}  ({record.type})")

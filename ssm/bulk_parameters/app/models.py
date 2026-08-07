from enum import StrEnum

from pydantic import BaseModel


class ParameterType(StrEnum):
    STRING = "String"
    STRING_LIST = "StringList"
    SECURE_STRING = "SecureString"


class ParameterRecord(BaseModel):
    name: str
    value: str
    type: ParameterType
    keep: bool = False

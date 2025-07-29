import enum
import logging
import os
import sys
from typing import Annotated

from pydantic import BaseModel, model_validator, StringConstraints, field_validator, Field


class FieldEncodingType(enum.Enum):
    NATIVE = "-n"
    NATIVE_UNICODE = "-N"
    CHAR = "-c"
    UNICODE = "-w"


def _get_default_code_page_specifier() -> str | None:
    if sys.platform.startswith("win"):
        return "65001"  # utf-8
    return None


class BcpEncodingSettings(BaseModel):
    """
    Represents encoding settings to be used by bcp.
    default to `-N` - native Unicode.

    :param field_encoding_type: Specifies the encoding mode of the downloaded data fields.
    :param field_delimiter: the field delimiter of the downloaded data. Defaults to bcp default which is `\t`.
        not supported if `field_encoding_type` is `FieldEncodingMode.NATIVE` or `FieldEncodingMode.NATIVE_UNICODE`.
    :param row_terminator: the row terminator of the downloaded data. Defaults to bcp default which is `\n`.
        not supported if `field_encoding_type` is `FieldEncodingMode.NATIVE` or `FieldEncodingMode.NATIVE_UNICODE`.
    """
    field_encoding_type: FieldEncodingType = FieldEncodingType.NATIVE_UNICODE
    field_delimiter: Annotated[str, StringConstraints(min_length=1)] | None = None
    row_terminator: Annotated[str, StringConstraints(min_length=1)] | None = None
    code_page_specifier: Annotated[str, StringConstraints(min_length=1)] | None = Field(
        default_factory=_get_default_code_page_specifier,
        description="The -C flag for bcp, control the encoding conversion of the data that is downloaded/uploaded with bcp. "
                    "Relevant only for Windows and will be ignored otherwise. Defaults to 65001 which is utf-8. "
                    "Read more about it under https://learn.microsoft.com/en-us/sql/tools/bcp-utility#-c--acp--oem--raw--code_page-"
    )

    @model_validator(mode='after')
    def __validate(self):
        if self.field_encoding_type in (FieldEncodingType.NATIVE, FieldEncodingType.NATIVE_UNICODE) and (
                self.field_delimiter is not None or self.row_terminator is not None):
            raise ValueError(
                "field_delimiter and row_terminator are not supported when field_encoding_type is `FieldEncodingMode.NATIVE`")
        return self

    @field_validator("code_page_specifier")
    @classmethod
    def __warn_code_page_specifier(cls, code_page_specifier):
        if not sys.platform.startswith("win") and code_page_specifier is not None:
            logging.getLogger(cls.__name__).warning(
                "code_page_specifier is supported only for windows and therefor will be ignored")
            return None
        return code_page_specifier

    @property
    def command_options(self) -> dict[str, str | None]:
        command_options: dict[str, str | None] = {
            self.field_encoding_type.value: None,
        }
        if self.field_delimiter is not None:
            command_options["-t"] = self.field_delimiter
        if self.row_terminator is not None:
            command_options["-r"] = self.row_terminator
        if self.code_page_specifier is not None:
            command_options["-C"] = self.code_page_specifier
        return command_options

    @classmethod
    def csv_settings(cls, *, line_separator: str = os.linesep) -> 'BcpEncodingSettings':
        return cls(
            field_encoding_type=FieldEncodingType.CHAR,
            field_delimiter=',',
            row_terminator=line_separator,
        )

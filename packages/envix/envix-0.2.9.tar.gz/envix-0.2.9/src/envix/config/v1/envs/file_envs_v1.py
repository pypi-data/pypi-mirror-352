from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from envix.pattern import ENVNAME_PATTERN

from ._common import OverwriteType


class FileEnvsV1(BaseModel):
    """
    Environment variables read from a file.
    """

    model_config = ConfigDict(extra="forbid")

    type: Annotated[
        Literal["File"],
        Field(
            title="File environment variables.",
            description="Environment variable settings to be read from a file.",
        ),
    ]

    items: Annotated[
        dict[Annotated[str, Field(pattern=ENVNAME_PATTERN)], Path],
        Field(
            title="Environment variables",
            description="Environment variables to be read from the file.",
        ),
    ]

    overwrite: OverwriteType = True

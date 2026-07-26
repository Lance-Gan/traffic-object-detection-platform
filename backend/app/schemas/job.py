from datetime import datetime
from typing import Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from app.models.detection_job import (
    DetectionJobStatus,
    DetectionSourceType,
)


class DetectionJobListQuery(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    page: int = Field(
        default=1,
        ge=1,
    )

    page_size: int = Field(
        default=20,
        ge=1,
        le=100,
    )

    status: DetectionJobStatus | None = None
    source_type: DetectionSourceType | None = None

    search: str | None = Field(
        default=None,
        max_length=255,
    )

    created_from: datetime | None = None
    created_to: datetime | None = None

    @field_validator(
        "search",
        mode="before",
    )
    @classmethod
    def normalize_search(
        cls,
        value: object,
    ) -> object:
        if not isinstance(value, str):
            return value

        normalized_value = value.strip()
        return normalized_value or None

    @model_validator(mode="after")
    def validate_date_range(self) -> Self:
        if (
            self.created_from is not None
            and self.created_to is not None
            and self.created_from > self.created_to
        ):
            raise ValueError("created_from must not be later than created_to")

        return self

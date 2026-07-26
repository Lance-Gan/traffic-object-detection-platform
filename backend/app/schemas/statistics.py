from datetime import date

from pydantic import BaseModel, Field

from app.models.detection_job import (
    DetectionSourceType,
)


class StatisticsPeriodResponse(BaseModel):
    days: int = Field(ge=1)
    start_date: date
    end_date: date
    timezone: str


class StatisticsMetricsResponse(BaseModel):
    total_jobs: int = Field(ge=0)
    completed_jobs: int = Field(ge=0)
    failed_jobs: int = Field(ge=0)
    processing_jobs: int = Field(ge=0)
    pending_jobs: int = Field(ge=0)

    total_detected_objects: int = Field(ge=0)

    success_rate: float = Field(
        ge=0,
        le=100,
    )

    average_confidence: float | None
    average_duration_ms: float | None


class ClassStatisticsItemResponse(BaseModel):
    class_name: str
    object_count: int = Field(ge=0)
    average_confidence: float | None


class DailyStatisticsItemResponse(BaseModel):
    date: date

    total_jobs: int = Field(ge=0)
    completed_jobs: int = Field(ge=0)
    failed_jobs: int = Field(ge=0)
    detected_objects: int = Field(ge=0)


class SourceStatisticsItemResponse(BaseModel):
    source_type: DetectionSourceType
    job_count: int = Field(ge=0)


class DashboardStatisticsResponse(BaseModel):
    period: StatisticsPeriodResponse
    metrics: StatisticsMetricsResponse

    classes: list[ClassStatisticsItemResponse]
    daily: list[DailyStatisticsItemResponse]
    sources: list[SourceStatisticsItemResponse]

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models import (
    DetectionJob,
    DetectionJobStatus,
    DetectionObject,
    DetectionSourceType,
)


@dataclass(frozen=True, slots=True)
class JobMetricsData:
    total_jobs: int
    completed_jobs: int
    failed_jobs: int
    processing_jobs: int
    pending_jobs: int
    average_duration_ms: float | None


@dataclass(frozen=True, slots=True)
class ObjectMetricsData:
    total_objects: int
    average_confidence: float | None


@dataclass(frozen=True, slots=True)
class ClassStatisticsData:
    class_name: str
    object_count: int
    average_confidence: float | None


@dataclass(frozen=True, slots=True)
class DailyJobStatisticsData:
    bucket_date: date
    total_jobs: int
    completed_jobs: int
    failed_jobs: int


@dataclass(frozen=True, slots=True)
class DailyObjectStatisticsData:
    bucket_date: date
    object_count: int


@dataclass(frozen=True, slots=True)
class SourceStatisticsData:
    source_type: DetectionSourceType
    job_count: int


class StatisticsRepository:
    def __init__(
        self,
        session: Session,
    ) -> None:
        self.session = session

    def get_job_metrics(
        self,
        start_at: datetime,
        end_at: datetime,
    ) -> JobMetricsData:
        statement = select(
            func.count(DetectionJob.id).label("total_jobs"),
            func.sum(
                case(
                    (
                        DetectionJob.status == DetectionJobStatus.COMPLETED,
                        1,
                    ),
                    else_=0,
                )
            ).label("completed_jobs"),
            func.sum(
                case(
                    (
                        DetectionJob.status == DetectionJobStatus.FAILED,
                        1,
                    ),
                    else_=0,
                )
            ).label("failed_jobs"),
            func.sum(
                case(
                    (
                        DetectionJob.status == DetectionJobStatus.PROCESSING,
                        1,
                    ),
                    else_=0,
                )
            ).label("processing_jobs"),
            func.sum(
                case(
                    (
                        DetectionJob.status == DetectionJobStatus.PENDING,
                        1,
                    ),
                    else_=0,
                )
            ).label("pending_jobs"),
            func.avg(
                case(
                    (
                        DetectionJob.status == DetectionJobStatus.COMPLETED,
                        DetectionJob.duration_ms,
                    ),
                    else_=None,
                )
            ).label("average_duration_ms"),
        ).where(
            DetectionJob.created_at >= start_at,
            DetectionJob.created_at < end_at,
        )

        row = self.session.execute(statement).one()

        return JobMetricsData(
            total_jobs=self._to_int(row.total_jobs),
            completed_jobs=self._to_int(row.completed_jobs),
            failed_jobs=self._to_int(row.failed_jobs),
            processing_jobs=self._to_int(row.processing_jobs),
            pending_jobs=self._to_int(row.pending_jobs),
            average_duration_ms=self._to_float(row.average_duration_ms),
        )

    def get_object_metrics(
        self,
        start_at: datetime,
        end_at: datetime,
    ) -> ObjectMetricsData:
        statement = (
            select(
                func.count(DetectionObject.id).label("total_objects"),
                func.avg(DetectionObject.confidence).label("average_confidence"),
            )
            .select_from(DetectionObject)
            .join(
                DetectionJob,
                DetectionObject.job_id == DetectionJob.id,
            )
            .where(
                DetectionJob.created_at >= start_at,
                DetectionJob.created_at < end_at,
            )
        )

        row = self.session.execute(statement).one()

        return ObjectMetricsData(
            total_objects=self._to_int(row.total_objects),
            average_confidence=self._to_float(row.average_confidence),
        )

    def get_class_statistics(
        self,
        start_at: datetime,
        end_at: datetime,
    ) -> list[ClassStatisticsData]:
        statement = (
            select(
                DetectionObject.class_name,
                func.count(DetectionObject.id).label("object_count"),
                func.avg(DetectionObject.confidence).label("average_confidence"),
            )
            .select_from(DetectionObject)
            .join(
                DetectionJob,
                DetectionObject.job_id == DetectionJob.id,
            )
            .where(
                DetectionJob.created_at >= start_at,
                DetectionJob.created_at < end_at,
            )
            .group_by(DetectionObject.class_name)
            .order_by(func.count(DetectionObject.id).desc())
        )

        rows = self.session.execute(statement).all()

        return [
            ClassStatisticsData(
                class_name=str(class_name),
                object_count=self._to_int(object_count),
                average_confidence=self._to_float(average_confidence),
            )
            for (
                class_name,
                object_count,
                average_confidence,
            ) in rows
        ]

    def get_daily_job_statistics(
        self,
        start_at: datetime,
        end_at: datetime,
    ) -> list[DailyJobStatisticsData]:
        bucket_date = func.date(DetectionJob.created_at).label("bucket_date")

        statement = (
            select(
                bucket_date,
                func.count(DetectionJob.id).label("total_jobs"),
                func.sum(
                    case(
                        (
                            DetectionJob.status == DetectionJobStatus.COMPLETED,
                            1,
                        ),
                        else_=0,
                    )
                ).label("completed_jobs"),
                func.sum(
                    case(
                        (
                            DetectionJob.status == DetectionJobStatus.FAILED,
                            1,
                        ),
                        else_=0,
                    )
                ).label("failed_jobs"),
            )
            .where(
                DetectionJob.created_at >= start_at,
                DetectionJob.created_at < end_at,
            )
            .group_by(bucket_date)
            .order_by(bucket_date)
        )

        rows = self.session.execute(statement).all()

        return [
            DailyJobStatisticsData(
                bucket_date=current_date,
                total_jobs=self._to_int(total_jobs),
                completed_jobs=self._to_int(completed_jobs),
                failed_jobs=self._to_int(failed_jobs),
            )
            for (
                current_date,
                total_jobs,
                completed_jobs,
                failed_jobs,
            ) in rows
        ]

    def get_daily_object_statistics(
        self,
        start_at: datetime,
        end_at: datetime,
    ) -> list[DailyObjectStatisticsData]:
        bucket_date = func.date(DetectionJob.created_at).label("bucket_date")

        statement = (
            select(
                bucket_date,
                func.count(DetectionObject.id).label("object_count"),
            )
            .select_from(DetectionObject)
            .join(
                DetectionJob,
                DetectionObject.job_id == DetectionJob.id,
            )
            .where(
                DetectionJob.created_at >= start_at,
                DetectionJob.created_at < end_at,
            )
            .group_by(bucket_date)
            .order_by(bucket_date)
        )

        rows = self.session.execute(statement).all()

        return [
            DailyObjectStatisticsData(
                bucket_date=current_date,
                object_count=self._to_int(object_count),
            )
            for (
                current_date,
                object_count,
            ) in rows
        ]

    def get_source_statistics(
        self,
        start_at: datetime,
        end_at: datetime,
    ) -> list[SourceStatisticsData]:
        statement = (
            select(
                DetectionJob.source_type,
                func.count(DetectionJob.id).label("job_count"),
            )
            .where(
                DetectionJob.created_at >= start_at,
                DetectionJob.created_at < end_at,
            )
            .group_by(DetectionJob.source_type)
            .order_by(func.count(DetectionJob.id).desc())
        )

        rows = self.session.execute(statement).all()

        return [
            SourceStatisticsData(
                source_type=source_type,
                job_count=self._to_int(job_count),
            )
            for (
                source_type,
                job_count,
            ) in rows
        ]

    @staticmethod
    def _to_int(
        value: object,
    ) -> int:
        if value is None:
            return 0

        if isinstance(
            value,
            (
                int,
                float,
                Decimal,
            ),
        ):
            return int(value)

        raise TypeError(f"Expected a numeric value, got {type(value).__name__}")

    @staticmethod
    def _to_float(
        value: object,
    ) -> float | None:
        if value is None:
            return None

        if isinstance(
            value,
            (
                int,
                float,
                Decimal,
            ),
        ):
            return float(value)

        raise TypeError(f"Expected a numeric value, got {type(value).__name__}")

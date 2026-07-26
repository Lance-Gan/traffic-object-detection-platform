from datetime import (
    UTC,
    datetime,
    time,
    timedelta,
)

from sqlalchemy.orm import Session

from app.repositories.statistics_repository import (
    StatisticsRepository,
)
from app.schemas.statistics import (
    ClassStatisticsItemResponse,
    DailyStatisticsItemResponse,
    DashboardStatisticsResponse,
    SourceStatisticsItemResponse,
    StatisticsMetricsResponse,
    StatisticsPeriodResponse,
)


class StatisticsService:
    def __init__(
        self,
        session: Session,
    ) -> None:
        self.repository = StatisticsRepository(session)

    def build_dashboard(
        self,
        days: int,
    ) -> DashboardStatisticsResponse:
        today = datetime.now(UTC).date()

        start_date = today - timedelta(days=days - 1)

        end_date = today

        start_at = datetime.combine(
            start_date,
            time.min,
        )

        end_at = datetime.combine(
            end_date + timedelta(days=1),
            time.min,
        )

        job_metrics = self.repository.get_job_metrics(
            start_at=start_at,
            end_at=end_at,
        )

        object_metrics = self.repository.get_object_metrics(
            start_at=start_at,
            end_at=end_at,
        )

        terminal_jobs = job_metrics.completed_jobs + job_metrics.failed_jobs

        success_rate = (
            round(
                (job_metrics.completed_jobs / terminal_jobs) * 100,
                2,
            )
            if terminal_jobs > 0
            else 0.0
        )

        class_rows = self.repository.get_class_statistics(
            start_at=start_at,
            end_at=end_at,
        )

        source_rows = self.repository.get_source_statistics(
            start_at=start_at,
            end_at=end_at,
        )

        daily_jobs = {
            item.bucket_date: item
            for item in (
                self.repository.get_daily_job_statistics(
                    start_at=start_at,
                    end_at=end_at,
                )
            )
        }

        daily_objects = {
            item.bucket_date: item.object_count
            for item in (
                self.repository.get_daily_object_statistics(
                    start_at=start_at,
                    end_at=end_at,
                )
            )
        }

        daily_items: list[DailyStatisticsItemResponse] = []

        current_date = start_date

        while current_date <= end_date:
            job_row = daily_jobs.get(current_date)

            daily_items.append(
                DailyStatisticsItemResponse(
                    date=current_date,
                    total_jobs=(job_row.total_jobs if job_row is not None else 0),
                    completed_jobs=(job_row.completed_jobs if job_row is not None else 0),
                    failed_jobs=(job_row.failed_jobs if job_row is not None else 0),
                    detected_objects=(
                        daily_objects.get(
                            current_date,
                            0,
                        )
                    ),
                )
            )

            current_date += timedelta(days=1)

        return DashboardStatisticsResponse(
            period=StatisticsPeriodResponse(
                days=days,
                start_date=start_date,
                end_date=end_date,
                timezone="UTC",
            ),
            metrics=StatisticsMetricsResponse(
                total_jobs=(job_metrics.total_jobs),
                completed_jobs=(job_metrics.completed_jobs),
                failed_jobs=(job_metrics.failed_jobs),
                processing_jobs=(job_metrics.processing_jobs),
                pending_jobs=(job_metrics.pending_jobs),
                total_detected_objects=(object_metrics.total_objects),
                success_rate=success_rate,
                average_confidence=(
                    round(
                        object_metrics.average_confidence,
                        5,
                    )
                    if object_metrics.average_confidence is not None
                    else None
                ),
                average_duration_ms=(
                    round(
                        job_metrics.average_duration_ms,
                        2,
                    )
                    if job_metrics.average_duration_ms is not None
                    else None
                ),
            ),
            classes=[
                ClassStatisticsItemResponse(
                    class_name=item.class_name,
                    object_count=(item.object_count),
                    average_confidence=(
                        round(
                            item.average_confidence,
                            5,
                        )
                        if item.average_confidence is not None
                        else None
                    ),
                )
                for item in class_rows
            ],
            daily=daily_items,
            sources=[
                SourceStatisticsItemResponse(
                    source_type=(item.source_type),
                    job_count=item.job_count,
                )
                for item in source_rows
            ],
        )


def create_statistics_service(
    session: Session,
) -> StatisticsService:
    return StatisticsService(session)

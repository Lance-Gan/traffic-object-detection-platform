from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.sql.elements import ColumnElement

from app.models import DetectionJob, DetectionObject
from app.schemas.job import DetectionJobListQuery


@dataclass(frozen=True, slots=True)
class DetectionJobPage:
    jobs: tuple[DetectionJob, ...]
    summaries: dict[int, dict[str, int]]
    total: int


class DetectionRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, job: DetectionJob) -> None:
        self.session.add(job)

    def get_by_public_id(
        self,
        public_id: str,
    ) -> DetectionJob | None:
        statement = (
            select(DetectionJob)
            .options(selectinload(DetectionJob.objects))
            .where(DetectionJob.public_id == public_id)
        )

        return self.session.scalar(statement)

    def list_jobs(
        self,
        filters: DetectionJobListQuery,
    ) -> DetectionJobPage:
        conditions = self._build_conditions(filters)

        total_statement = select(func.count(DetectionJob.id)).where(*conditions)

        total = self.session.scalar(total_statement) or 0

        offset = (filters.page - 1) * filters.page_size

        jobs_statement = (
            select(DetectionJob)
            .where(*conditions)
            .order_by(
                DetectionJob.created_at.desc(),
                DetectionJob.id.desc(),
            )
            .offset(offset)
            .limit(filters.page_size)
        )

        jobs = tuple(self.session.scalars(jobs_statement).all())

        summaries = self._load_summaries(jobs)

        return DetectionJobPage(
            jobs=jobs,
            summaries=summaries,
            total=int(total),
        )

    def _build_conditions(
        self,
        filters: DetectionJobListQuery,
    ) -> list[ColumnElement[bool]]:
        conditions: list[ColumnElement[bool]] = []

        if filters.status is not None:
            conditions.append(DetectionJob.status == filters.status)

        if filters.source_type is not None:
            conditions.append(DetectionJob.source_type == filters.source_type)

        if filters.created_from is not None:
            conditions.append(DetectionJob.created_at >= self._to_utc_naive(filters.created_from))

        if filters.created_to is not None:
            conditions.append(DetectionJob.created_at <= self._to_utc_naive(filters.created_to))

        if filters.search is not None:
            escaped_search = self._escape_like(filters.search)

            search_pattern = f"%{escaped_search}%"

            conditions.append(
                or_(
                    DetectionJob.original_filename.like(
                        search_pattern,
                        escape="\\",
                    ),
                    DetectionJob.public_id.like(
                        search_pattern,
                        escape="\\",
                    ),
                )
            )

        return conditions

    def _load_summaries(
        self,
        jobs: tuple[DetectionJob, ...],
    ) -> dict[int, dict[str, int]]:
        if not jobs:
            return {}

        job_ids = [job.id for job in jobs]

        statement = (
            select(
                DetectionObject.job_id,
                DetectionObject.class_name,
                func.count(DetectionObject.id).label("object_count"),
            )
            .where(DetectionObject.job_id.in_(job_ids))
            .group_by(
                DetectionObject.job_id,
                DetectionObject.class_name,
            )
        )

        summaries: dict[
            int,
            dict[str, int],
        ] = {}

        rows = self.session.execute(statement).all()

        for job_id, class_name, object_count in rows:
            summaries.setdefault(
                int(job_id),
                {},
            )[str(class_name)] = int(object_count)

        return summaries

    @staticmethod
    def _to_utc_naive(
        value: datetime,
    ) -> datetime:
        if value.tzinfo is None:
            return value

        return value.astimezone(UTC).replace(tzinfo=None)

    @staticmethod
    def _escape_like(value: str) -> str:
        return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")

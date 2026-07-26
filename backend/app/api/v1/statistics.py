from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas.statistics import (
    DashboardStatisticsResponse,
)
from app.services.statistics_service import (
    create_statistics_service,
)

router = APIRouter(
    prefix="/statistics",
    tags=["Statistics"],
)


@router.get(
    "/dashboard",
    response_model=DashboardStatisticsResponse,
)
def get_dashboard_statistics(
    session: Annotated[
        Session,
        Depends(get_db_session),
    ],
    days: Annotated[
        int,
        Query(
            ge=1,
            le=365,
        ),
    ] = 30,
) -> DashboardStatisticsResponse:
    service = create_statistics_service(session)

    return service.build_dashboard(days)

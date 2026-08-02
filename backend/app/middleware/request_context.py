import logging
import re
from time import perf_counter
from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.responses import Response

from app.core.logging import (
    request_id_context,
)

logger = logging.getLogger(__name__)

REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._-]{1,64}$")


def resolve_request_id(
    request: Request,
) -> str:
    supplied_request_id = request.headers.get("X-Request-ID")

    if supplied_request_id and REQUEST_ID_PATTERN.fullmatch(supplied_request_id):
        return supplied_request_id

    return uuid4().hex


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        request_id = resolve_request_id(request)

        token = request_id_context.set(request_id)

        started_at = perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            logger.exception(
                "Unhandled request error",
                extra={
                    "method": (request.method),
                    "path": (request.url.path),
                },
            )

            raise

        duration_ms = max(
            0,
            round((perf_counter() - started_at) * 1000),
        )

        response.headers["X-Request-ID"] = request_id

        logger.info(
            "Request completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": (response.status_code),
                "duration_ms": (duration_ms),
            },
        )

        request_id_context.reset(token)

        return response

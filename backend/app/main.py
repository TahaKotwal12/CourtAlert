from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.api.exception import CourtAlertFatalException, CourtAlertNonFatalException
from app.api.schemas.common_schemas import CommonResponse
from app.config.logger import get_logger
from app.core.config import settings

# Routers
from app.routers import auth, cases, notifications, webhooks, stats

APP_TITLE = "CourtAlert API"

app = FastAPI(title=APP_TITLE, version="1.0.0")

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

API_PREFIX = "/api/v1"

app.include_router(auth.router,          prefix=API_PREFIX)
app.include_router(cases.router,         prefix=API_PREFIX)
app.include_router(notifications.router, prefix=API_PREFIX)
app.include_router(webhooks.router,      prefix=API_PREFIX)
app.include_router(stats.router,         prefix=API_PREFIX)

# ---------------------------------------------------------------------------
# Health / Root
# ---------------------------------------------------------------------------

@app.get("/")
async def root():
    return {"message": APP_TITLE, "status": "running", "docs": "/docs"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": APP_TITLE}


# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------

@app.exception_handler(CourtAlertFatalException)
async def fatal_exception_handler(request: Request, exc: CourtAlertFatalException):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=CommonResponse[dict](
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=exc.detail,
            message_id="0",
            data={},
        ).model_dump(),
    )


@app.exception_handler(CourtAlertNonFatalException)
async def non_fatal_exception_handler(request: Request, exc: CourtAlertNonFatalException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=CommonResponse[dict](
            code=status.HTTP_400_BAD_REQUEST,
            message=exc.detail,
            message_id="0",
            data={},
        ).model_dump(),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger = get_logger(__name__)
    first_error = exc.errors()[0]
    location_parts = [str(loc) for loc in first_error["loc"]]
    if location_parts and location_parts[0] == "body":
        location_parts.pop(0)
    location = ".".join(location_parts)
    message = f"{location}: {first_error['msg']}"
    logger.error(f"Request validation error: {message}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=CommonResponse[dict](
            code=status.HTTP_400_BAD_REQUEST,
            message=message,
            message_id="0",
            data={},
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger = get_logger(__name__)
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=CommonResponse[dict](
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"An unexpected error occurred: {str(exc)}",
            message_id="0",
            data={},
        ).model_dump(),
    )

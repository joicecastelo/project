# @Author: Rafael Direito
# @Date:   2022-08-03 18:45:14 (WEST)
# @Email:  rdireito@av.it.pt
# @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-04-10 17:02:06


# generic imports
import logging
import sys
import asyncio
from logging.handlers import RotatingFileHandler
from fastapi import (
    FastAPI,
    HTTPException,
    status
)
from fastapi.exceptions import RequestValidationError
from http import HTTPStatus
# custom imports
from aux import startup

# Logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
fh = RotatingFileHandler(
    filename='./server.log',
    maxBytes=10485760,  # 10 MBytes
    backupCount=5
    )
formatter = logging.Formatter(
    "%(asctime)s - %(module)s - %(funcName)s - line:%(lineno)d " +
    "- %(levelname)s - %(message)s"
)
ch.setFormatter(formatter)
fh.setFormatter(formatter)

# Exporting logs to the screen
# logger.addHandler(ch)
# Exporting logs to a file
#logger.addHandler(fh)
logger = logging.getLogger(__name__)


# Verify if we can proceed (all envs correctly defined)
load_envs_result = startup.load_envs()
if not load_envs_result[0]:
    logging.error(load_envs_result[1])
    sys.exit(1)
else:
    # If all the envs are defined, we can import all database-related module
    from database.database import SessionLocal
    from database.database import engine
    from database.models import models
    from routers import organizations_router
    from routers import aux as RouterAux
    

logging.info("Starting API..")

fast_api_tags_metadata = [
    {
        "name": "organization",
        "description": "Operations related with the organizations.",
    },
]

fast_api_description = "REST API of Resource Manager"

# Start Fast API
app = FastAPI(
    title="Resources Manager",
    description=fast_api_description,
    version="0.0.1",
    contact={
        "name": "Rafael Direito",
    },
    openapi_tags=fast_api_tags_metadata
)

# Load Routers
app.include_router(organizations_router.router)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# __init__
@app.on_event("startup")
async def startup_event():
    models.Base.metadata.create_all(bind=engine)

@app.get("/healthcheck")
async def healthcheck():
    return {"Health": "OK"}

# This function will handle all default pydantic exceptions raised in the
# routers and parse them to TMF632 standardized exceptions
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):

    error_messages = [
        f"Error=(payload_location={'/'.join(error['loc'])}, " +
        f"message='{error['msg']}')"
        for error
        in exc.errors()
    ]

    logger.error("Exception Occurred in Payload's Validation: " +
                 ", ".join(error_messages))

    return RouterAux.create_http_response(
            http_status=HTTPStatus.BAD_REQUEST,
            content=RouterAux.compose_error_payload(
                code=HTTPStatus.BAD_REQUEST,
                reason=", ".join(error_messages),
            )
        )


# This function will handle all default FastAPIKeycloak exceptions raised in
# the routers and parse them to TMF632 standardized exceptions
@app.exception_handler(HTTPException)
async def validation_authentication_authorization(request, exc):

    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        return RouterAux.create_http_response(
            http_status=HTTPStatus.UNAUTHORIZED,
            content=RouterAux.compose_error_payload(
                code=HTTPStatus.UNAUTHORIZED,
                reason="You should be authenticated in order to perform " +
                "this request",
            )
        )
    elif exc.status_code == status.HTTP_403_FORBIDDEN:
        return RouterAux.create_http_response(
            http_status=HTTPStatus.FORBIDDEN,
            content=RouterAux.compose_error_payload(
                code=HTTPStatus.FORBIDDEN,
                reason=exc.detail,
            )
        )
    else:
        raise exc

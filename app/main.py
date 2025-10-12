import logging

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from app import settings
from app.core.api_client import LogRequestMiddleware
from app.core.exceptions import AuthException
from app.router.api_v1.endpoints import api_router

logger = logging.getLogger(__name__)

app = FastAPI(
    title="FinOps for Cloud API Modifier",
    version="4.0.0",
    root_path="/modifier/v1",
    debug=settings.debug,
)
# Todo: remove * from allow_origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router)
app.add_middleware(LogRequestMiddleware)


@app.exception_handler(AuthException)
async def jwt_bearer_exception_handler(request: Request, exc: AuthException):
    return JSONResponse(
        status_code=401,
        content={
            "error": f"{exc.title}",
            "error_code": f"{exc.error.get('error_code', '')}",
            "params": [],
            "reason": f"{exc.error.get('reason', 'Wrong Authentication')}",
        },
    )


if __name__ == "__main__":
    # TODO: get port and host from settings
    uvicorn.run("main:app", port=8080, host="0.0.0.0", reload=True)  # nosec B104

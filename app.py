"""Main config for fastapi app"""

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from starlette.middleware.cors import CORSMiddleware

from configs import settings
from core.handle_event import handle_app_startup, handle_app_shutdown
from routers.api import router as router_api

app = FastAPI(title="Insurance API")
app.include_router(router_api, prefix="/api")
app.add_event_handler("startup", handle_app_startup)
app.add_event_handler("shutdown", handle_app_shutdown)

if settings.get("VERSION") == "local":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def custom_openapi():
    """
    custom API
    """
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title, version=app.version, routes=app.routes
    )
    http_methods = ["post", "get", "put", "delete"]
    # look for the error 422 and removes it
    for method in openapi_schema["paths"]:
        for http_method in http_methods:
            try:
                del openapi_schema["paths"][method][http_method]["responses"]["422"]
            except KeyError:
                pass

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

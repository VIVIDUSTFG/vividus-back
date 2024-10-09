from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from starlette.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.core.utils.dynamic_router import Routers
from src.modules.modules import router_urls

app = FastAPI(**settings.fastapi_kwargs)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            str(origin) for origin in settings.BACKEND_CORS_ORIGINS
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

Routers(app, router_urls, prefix=settings.API_STR)()


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

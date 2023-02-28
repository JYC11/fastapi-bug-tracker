import uvicorn
from fastapi import FastAPI
from starlette import status
from starlette.middleware.cors import CORSMiddleware

from app.common.settings import settings
from app.entrypoints.router import api_v1_router

app = FastAPI(
    title="bug tracking app",
    redoc_url="/redoc",
    docs_url="/docs",
    openapi_url=f"{settings.api_v1_str}/openapi.json",
)

app.include_router(api_v1_router, prefix=settings.api_v1_str)


@app.get("/health", status_code=status.HTTP_200_OK)
def health():
    return "ok"


if settings.backend_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.backend_cors_origins],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


if __name__ == "__main__":
    uvicorn.run("app.main:app", port=8000, reload=True)

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config import get_settings
from app.db.session import init_db
from app.logging_config import setup_logging
from app.scheduler import start_scheduler, stop_scheduler

settings = get_settings()
setup_logging(settings)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    start_scheduler(settings)
    yield
    stop_scheduler()


app = FastAPI(title=settings.app_name, version='2.0.0', lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list(),
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
app.include_router(router)


@app.get('/')
def root() -> dict[str, object]:
    return {'ok': True, 'app': settings.app_name, 'docs': '/docs'}

from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from src.api.routes import router as api_router
from src.db.database import engine, Base
import src.models.db  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Finance Assistant API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API is running"}


# Serve frontend static files if they exist
frontend_dist = os.path.join(os.getcwd(), "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount(
        "/", StaticFiles(directory=frontend_dist, html=True), name="static"
    )

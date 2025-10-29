from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine, Base

# Import routers (will be added as we build them)
from app.routers import auth
# from app.routers import auth, mentorship_logs, users, facilities, follow_ups, reports

# Note: Database tables are managed via Alembic migrations
# For local development, run: alembic upgrade head


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Application starting up...")
    yield
    # Shutdown
    print("Application shutting down...")


app = FastAPI(
    title="Digital Mentorship Log API",
    description="API for managing mentorship activities",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

# Include routers (will be added as we build them)
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
# app.include_router(mentorship_logs.router, prefix="/api/mentorship-logs", tags=["mentorship_logs"])
# app.include_router(users.router, prefix="/api/users", tags=["users"])
# app.include_router(facilities.router, prefix="/api/facilities", tags=["facilities"])
# app.include_router(follow_ups.router, prefix="/api/follow-ups", tags=["follow_ups"])
# app.include_router(reports.router, prefix="/api/reports", tags=["reports"])


@app.get("/")
async def root():
    return {"message": "Digital Mentorship Log API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

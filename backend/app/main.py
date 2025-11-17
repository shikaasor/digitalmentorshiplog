from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine, Base, get_pool_status

# Import routers (will be added as we build them)
from app.routers import auth, facilities, mentorship_logs, users, follow_ups, reports, attachments, comments, notifications, constants

# Note: Database tables are managed via Alembic migrations
# For local development, run: alembic upgrade head


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Application starting up...")

    # Initialize Supabase Storage bucket
    try:
        from app.storage import storage_service
        storage_service.create_bucket_if_not_exists()
    except Exception as e:
        print(f"Warning: Could not initialize storage: {str(e)}")

    yield
    # Shutdown
    print("Application shutting down...")
    # Dispose of all database connections
    engine.dispose()
    print("Database connections closed")


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

# Include routers
app.include_router(auth.router)
app.include_router(constants.router)
app.include_router(facilities.router)
app.include_router(mentorship_logs.router)
app.include_router(users.router)
app.include_router(follow_ups.router)
app.include_router(reports.router)
app.include_router(attachments.router)
app.include_router(comments.router)
app.include_router(notifications.router)


@app.get("/")
async def root():
    return {"message": "Digital Mentorship Log API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """
    Health check endpoint with database connection status.

    Returns application health status and database connection information.
    """
    try:
        db_status = get_pool_status()
        return {
            "status": "healthy",
            "database": db_status
        }
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

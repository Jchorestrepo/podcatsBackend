"""Main entrypoint for the FastAPI application."""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .utils.env_loader import load_env
from .routes import router
import os

# Load environment variables from .env file
load_env()

# Create FastAPI app instance
app = FastAPI(
    title="AI Podcast Generator",
    description="An API to generate podcasts from text using AI.",
    version="1.0.0"
)

# --- Mount Static Files ---
# This allows serving files from the 'files' directory at the /files endpoint.
# Note: The GET /files/{filename} route in routes.py provides a more controlled way to do this.
# If you prefer only using the route, you can comment out the next line.
# However, mounting is efficient for serving static content.
files_dir = "files"
os.makedirs(files_dir, exist_ok=True)
app.mount("/files", StaticFiles(directory=files_dir), name="files")


# --- Include API Routes ---
# All routes defined in routes.py will be included under the main app.
app.include_router(router)

# --- Root Endpoint ---
@app.get("/", summary="Root Endpoint")
async def root():
    """
    A simple root endpoint that provides a welcome message and a link to the API docs.
    """
    return {
        "message": "Welcome to the AI Podcast Generator API!",
        "docs_url": "/docs"
    }

# To run this app:
# uvicorn app.main:app --reload

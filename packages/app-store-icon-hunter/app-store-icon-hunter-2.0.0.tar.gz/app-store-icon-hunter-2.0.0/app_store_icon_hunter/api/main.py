"""
FastAPI server for App Store Icon Hunter
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import asyncio
import os
import json
from pathlib import Path
import uuid
import logging

try:
    from ..core.app_store import AppStoreAPI
    from ..core.google_play import GooglePlayAPI
    from ..core.downloader import IconDownloader
    from ..utils.helpers import validate_store_name, validate_country_code, validate_icon_sizes
except ImportError:
    # Fallback for direct execution
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from core.app_store import AppStoreAPI
    from core.google_play import GooglePlayAPI
    from core.downloader import IconDownloader
    from utils.helpers import validate_store_name, validate_country_code, validate_icon_sizes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="App Store Icon Hunter API",
    description="A powerful REST API for searching apps and downloading their icons from App Store and Google Play Store",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize APIs
app_store_api = AppStoreAPI()
google_play_api = GooglePlayAPI()
downloader = IconDownloader()

# Pydantic models
class AppSearchResult(BaseModel):
    name: str
    bundle_id: str
    icon_url: str
    store: str
    price: str
    rating: Optional[float] = None
    description: Optional[str] = None
    developer: Optional[str] = None
    category: Optional[str] = None
    url: Optional[str] = None

class SearchRequest(BaseModel):
    term: str = Field(..., description="Search term for apps")
    store: str = Field(default="both", description="Store to search: 'appstore', 'googleplay', or 'both'")
    country: str = Field(default="us", description="Country code")
    limit: int = Field(default=10, description="Maximum number of results")

class DownloadRequest(BaseModel):
    apps: List[Dict] = Field(..., description="List of apps to download")
    sizes: List[int] = Field(default=[64, 128, 256, 512], description="Icon sizes to download")
    format: str = Field(default="zip", description="Download format: 'zip' or 'individual'")

class DownloadStatus(BaseModel):
    job_id: str
    status: str  # 'pending', 'running', 'completed', 'failed'
    progress: int
    total: int
    completed_apps: List[str] = []
    failed_apps: List[Dict] = []
    download_url: Optional[str] = None
    error_message: Optional[str] = None


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "App Store Icon Hunter API",
        "version": "2.0.0",
        "description": "Search apps and download icons from App Store and Google Play",
        "endpoints": {
            "search": "/search",
            "download": "/download",
            "status": "/status/{job_id}",
            "download_file": "/download/{job_id}",
            "docs": "/docs"
        }
    }


@app.post("/search", response_model=List[AppSearchResult])
async def search_apps(request: SearchRequest):
    """
    Search for apps in App Store and/or Google Play Store
    
    - **term**: Search term (required)
    - **store**: Which store to search ('appstore', 'googleplay', or 'both')
    - **country**: Country code (default: 'us')
    - **limit**: Maximum results per store (default: 10)
    """
    # Validate inputs
    if not validate_store_name(request.store):
        raise HTTPException(status_code=400, detail="Invalid store name")
    
    if not validate_country_code(request.country):
        raise HTTPException(status_code=400, detail="Invalid country code")
    
    if request.limit < 1 or request.limit > 50:
        raise HTTPException(status_code=400, detail="Limit must be between 1 and 50")
    
    all_apps = []
    
    try:
        # Search App Store
        if request.store in ["appstore", "both"]:
            app_store_results = app_store_api.search_apps(
                request.term, request.country, request.limit
            )
            all_apps.extend(app_store_results)
        
        # Search Google Play
        if request.store in ["googleplay", "both"]:
            google_play_results = google_play_api.search_apps(
                request.term, request.country, request.limit
            )
            all_apps.extend(google_play_results)
        
        # Convert to response model
        results = []
        for app in all_apps:
            try:
                result = AppSearchResult(**app)
                results.append(result)
            except Exception as e:
                logger.warning(f"Failed to parse app result: {e}")
                continue
        
        return results
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail="Search failed")


@app.post("/download")
async def start_download(request: DownloadRequest, background_tasks: BackgroundTasks):
    """
    Start downloading icons for selected apps
    
    - **apps**: List of app dictionaries to download
    - **sizes**: List of icon sizes to generate (default: [64, 128, 256, 512])
    - **format**: Download format ('zip' only supported currently)
    """
    # Validate inputs
    if not request.apps:
        raise HTTPException(status_code=400, detail="No apps provided")
    
    if not validate_icon_sizes(request.sizes):
        raise HTTPException(status_code=400, detail="Invalid icon sizes")
    
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    # Start background download task
    background_tasks.add_task(
        download_icons_background, 
        job_id, 
        request.apps, 
        request.sizes
    )
    
    return {
        "job_id": job_id,
        "status": "started",
        "message": f"Download started for {len(request.apps)} apps"
    }


@app.get("/status/{job_id}")
async def get_download_status(job_id: str):
    """
    Get the status of a download job
    
    - **job_id**: The ID of the download job
    """
    status = downloader.get_job_status(job_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return status


@app.get("/download/{job_id}")
async def download_file(job_id: str):
    """
    Download the completed ZIP file for a job
    
    - **job_id**: The ID of the completed download job
    """
    status = downloader.get_job_status(job_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if status["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed")
    
    zip_path = status.get("zip_path")
    if not zip_path or not os.path.exists(zip_path):
        raise HTTPException(status_code=404, detail="Download file not found")
    
    return FileResponse(
        zip_path, 
        media_type="application/zip",
        filename=f"icons_{job_id[:8]}.zip"
    )


@app.get("/jobs")
async def list_jobs():
    """List all download jobs and their status"""
    jobs = {}
    for job_id, status in downloader.jobs.items():
        jobs[job_id] = {
            "job_id": job_id,
            "status": status["status"],
            "progress": f"{status['progress']}/{status['total']}",
            "completed_apps": len(status.get("completed_apps", [])),
            "failed_apps": len(status.get("failed_apps", []))
        }
    
    return {"jobs": jobs}


@app.delete("/jobs/{job_id}")
async def cleanup_job(job_id: str):
    """Clean up a completed job and its files"""
    status = downloader.get_job_status(job_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Remove files
    zip_path = status.get("zip_path")
    if zip_path and os.path.exists(zip_path):
        try:
            os.remove(zip_path)
        except OSError:
            pass
    
    # Remove job from memory
    if job_id in downloader.jobs:
        del downloader.jobs[job_id]
    
    return {"message": f"Job {job_id} cleaned up"}


async def download_icons_background(job_id: str, apps: List[Dict], sizes: List[int]):
    """Background task for downloading icons"""
    try:
        result = await downloader.download_icons_async(apps, sizes, job_id)
        logger.info(f"Download job {job_id} completed: {result['status']}")
    except Exception as e:
        logger.error(f"Download job {job_id} failed: {e}")


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "App Store Icon Hunter API",
        "version": "2.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

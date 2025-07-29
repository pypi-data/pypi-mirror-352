"""
Icon downloading and processing functionality
"""

import requests
import asyncio
import aiohttp
import aiofiles
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging
import zipfile
import tempfile
import uuid
from PIL import Image
import io

logger = logging.getLogger(__name__)


class IconDownloader:
    """Handles downloading and resizing app icons"""
    
    STANDARD_SIZES = [16, 32, 48, 64, 128, 256, 512, 1024]
    DEFAULT_SIZES = [64, 128, 256, 512]
    
    def __init__(self, output_dir: str = "icons"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.jobs = {}  # Track download jobs
    
    async def download_icons_async(self, apps: List[Dict], sizes: List[int] = None, 
                                 job_id: str = None) -> Dict:
        """
        Download icons for multiple apps asynchronously
        
        Args:
            apps: List of app dictionaries
            sizes: List of icon sizes to generate
            job_id: Optional job ID for tracking
            
        Returns:
            Job status dictionary
        """
        if sizes is None:
            sizes = self.DEFAULT_SIZES
        
        if job_id is None:
            job_id = str(uuid.uuid4())
        
        # Initialize job status
        self.jobs[job_id] = {
            "status": "running",
            "progress": 0,
            "total": len(apps),
            "completed_apps": [],
            "failed_apps": [],
            "error_message": None,
            "zip_path": None
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                tasks = []
                for app in apps:
                    task = self._download_app_icon(session, app, sizes, job_id)
                    tasks.append(task)
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                successful_downloads = []
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        self.jobs[job_id]["failed_apps"].append({
                            "app": apps[i]["name"],
                            "error": str(result)
                        })
                    else:
                        successful_downloads.append(result)
                        self.jobs[job_id]["completed_apps"].append(apps[i]["name"])
                
                # Create ZIP file if there are successful downloads
                if successful_downloads:
                    zip_path = await self._create_zip_file(successful_downloads, job_id)
                    self.jobs[job_id]["zip_path"] = zip_path
                
                self.jobs[job_id]["status"] = "completed"
                self.jobs[job_id]["progress"] = self.jobs[job_id]["total"]
                
        except Exception as e:
            logger.error(f"Download job {job_id} failed: {e}")
            self.jobs[job_id]["status"] = "failed"
            self.jobs[job_id]["error_message"] = str(e)
        
        return self.jobs[job_id]
    
    async def _download_app_icon(self, session: aiohttp.ClientSession, 
                               app: Dict, sizes: List[int], job_id: str) -> Dict:
        """Download and process a single app's icon"""
        app_name = self._sanitize_filename(app["name"])
        app_dir = self.output_dir / job_id / app_name
        app_dir.mkdir(parents=True, exist_ok=True)
        
        icon_url = app.get("icon_url", "")
        if not icon_url:
            raise ValueError(f"No icon URL for {app['name']}")
        
        try:
            # Download original icon
            async with session.get(icon_url) as response:
                response.raise_for_status()
                image_data = await response.read()
            
            # Save original
            original_path = app_dir / "original.png"
            async with aiofiles.open(original_path, "wb") as f:
                await f.write(image_data)
            
            # Generate different sizes
            generated_files = [str(original_path)]
            if len(sizes) > 1 or sizes[0] != "original":
                generated_files.extend(await self._resize_icon(image_data, app_dir, sizes))
            
            # Update progress
            self.jobs[job_id]["progress"] += 1
            
            return {
                "app": app,
                "files": generated_files,
                "directory": str(app_dir)
            }
            
        except Exception as e:
            logger.error(f"Failed to download icon for {app['name']}: {e}")
            raise
    
    async def _resize_icon(self, image_data: bytes, output_dir: Path, 
                         sizes: List[int]) -> List[str]:
        """Resize icon to different sizes using PIL"""
        generated_files = []
        
        try:
            # Open image with PIL
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGBA if necessary
            if image.mode != "RGBA":
                image = image.convert("RGBA")
            
            for size in sizes:
                if size in self.STANDARD_SIZES:
                    resized = image.resize((size, size), Image.Resampling.LANCZOS)
                    
                    # Save as PNG
                    output_path = output_dir / f"icon_{size}x{size}.png"
                    resized.save(output_path, "PNG", optimize=True)
                    generated_files.append(str(output_path))
            
        except Exception as e:
            logger.error(f"Failed to resize icon: {e}")
            # If resizing fails, just copy the original for each size
            for size in sizes:
                output_path = output_dir / f"icon_{size}x{size}.png"
                async with aiofiles.open(output_path, "wb") as f:
                    await f.write(image_data)
                generated_files.append(str(output_path))
        
        return generated_files
    
    async def _create_zip_file(self, downloads: List[Dict], job_id: str) -> str:
        """Create a ZIP file containing all downloaded icons"""
        zip_path = self.output_dir / f"icons_{job_id}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for download in downloads:
                app_name = download["app"]["name"]
                for file_path in download["files"]:
                    file_path = Path(file_path)
                    if file_path.exists():
                        # Create archive path: app_name/filename
                        archive_path = f"{self._sanitize_filename(app_name)}/{file_path.name}"
                        zipf.write(file_path, archive_path)
        
        return str(zip_path)
    
    def get_job_status(self, job_id: str) -> Optional[Dict]:
        """Get the status of a download job"""
        return self.jobs.get(job_id)
    
    def download_icon_sync(self, icon_url: str, app_name: str, 
                          sizes: List[int] = None) -> List[str]:
        """
        Synchronous version for single icon download
        
        Args:
            icon_url: URL of the icon to download
            app_name: Name of the app (for folder naming)
            sizes: List of sizes to generate
            
        Returns:
            List of generated file paths
        """
        if sizes is None:
            sizes = self.DEFAULT_SIZES
        
        app_dir = self.output_dir / self._sanitize_filename(app_name)
        app_dir.mkdir(exist_ok=True)
        
        downloaded_files = []
        
        try:
            # Download original icon
            response = requests.get(icon_url, timeout=10)
            response.raise_for_status()
            
            # Save original
            original_path = app_dir / "original.png"
            with open(original_path, "wb") as f:
                f.write(response.content)
            downloaded_files.append(str(original_path))
            
            # Generate different sizes
            if len(sizes) > 1 or (len(sizes) == 1 and sizes[0] != "original"):
                try:
                    image = Image.open(io.BytesIO(response.content))
                    if image.mode != "RGBA":
                        image = image.convert("RGBA")
                    
                    for size in sizes:
                        if size in self.STANDARD_SIZES:
                            resized = image.resize((size, size), Image.Resampling.LANCZOS)
                            size_path = app_dir / f"icon_{size}x{size}.png"
                            resized.save(size_path, "PNG", optimize=True)
                            downloaded_files.append(str(size_path))
                            
                except Exception as e:
                    logger.warning(f"Could not resize icon for {app_name}: {e}")
                    # Fall back to copying original
                    for size in sizes:
                        size_path = app_dir / f"icon_{size}x{size}.png"
                        with open(size_path, "wb") as f:
                            f.write(response.content)
                        downloaded_files.append(str(size_path))
            
            return downloaded_files
            
        except Exception as e:
            logger.error(f"Failed to download icon for {app_name}: {e}")
            return []
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for filesystem compatibility"""
        import re
        # Remove or replace invalid characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Remove leading/trailing spaces and dots
        sanitized = sanitized.strip(' .')
        # Limit length
        if len(sanitized) > 50:
            sanitized = sanitized[:50]
        return sanitized or "unknown_app"

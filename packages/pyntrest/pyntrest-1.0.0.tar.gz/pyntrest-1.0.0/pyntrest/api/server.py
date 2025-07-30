from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import random
import aiohttp
from ..client.pinterest import PinterestClient
from pydantic import BaseModel
from typing import Optional, List
import os
import importlib.resources as pkg_resources

app = FastAPI(
    title="Pyntrest API",
    description="A FastAPI service for searching and downloading Pinterest images",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Pinterest client
pinterest = PinterestClient()

class ImageResponse(BaseModel):
    url: str
    width: Optional[int]
    height: Optional[int]
    title: Optional[str]
    description: Optional[str]

class SearchResponse(BaseModel):
    query: str
    results: List[ImageResponse]

@app.get("/api/search/", response_model=SearchResponse)
async def search_images(query: str, num: int = 5):
    """
    Search for Pinterest images
    - query: Search term
    - num: Number of images to return (default: 5)
    """
    results = pinterest.get_image_links(query, num)
    if not results:
        raise HTTPException(status_code=404, detail="No images found")
    
    return {
        "query": query,
        "results": results
    }

@app.get("/api/random/", response_model=ImageResponse)
async def get_random_image(query: str = None):
    """
    Get a single random image for the given search query
    - query: Search term (optional)
    """
    if query:
        results = pinterest.get_image_links(query, num_images=10)
        if not results:
            raise HTTPException(status_code=404, detail="No images found")
        return random.choice(results)
    else:
        result = pinterest.get_random_inspiration()
        if not result:
            raise HTTPException(status_code=404, detail="No images found")
        return result

@app.get("/api/inspire/", response_model=ImageResponse)
async def get_inspiration():
    """Get a random inspiration image"""
    result = pinterest.get_random_inspiration()
    if not result:
        raise HTTPException(status_code=404, detail="No images found")
    return result

@app.get("/api/one/", response_model=ImageResponse)
async def get_one_image(query: str):
    """
    Get a single image for the given search query
    - query: Search term
    """
    result = pinterest.get_one_image(query)
    if not result:
        raise HTTPException(status_code=404, detail="No images found")
    return result

@app.get("/api/download/")
async def download_image(url: str):
    """
    Download an image from the given URL
    - url: Image URL to download
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise HTTPException(status_code=404, detail="Image not found")
                
                # Get filename from URL
                filename = url.split('/')[-1]
                
                # Set response headers for download
                headers = {
                    'Content-Disposition': f'attachment; filename="{filename}"'
                }
                
                return StreamingResponse(
                    response.content,
                    media_type=response.headers.get('content-type', 'image/jpeg'),
                    headers=headers
                )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api")
async def api_info():
    """API information endpoint"""
    return {
        "name": "Pyntrest API",
        "version": "1.0.0",
        "endpoints": [
            "/api/search/ - Search for Pinterest images",
            "/api/random/ - Get a random image for a search query",
            "/api/one/ - Get a single image quickly",
            "/api/inspire/ - Get a random inspiration image",
            "/api/download/ - Download an image by URL"
        ]
    }

# Create function to locate static files directory
def get_static_path():
    """Get the path to static files"""
    try:
        # Try to get path from package resources
        with pkg_resources.path('pyntrest.web', 'static') as static_path:
            return str(static_path)
    except Exception:
        # Fallback to local path
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, 'web', 'static')

def run():
    """Run the FastAPI server"""
    import uvicorn
    
    # Mount static files
    static_path = get_static_path()
    app.mount("/static", StaticFiles(directory=static_path, html=True), name="static")
    
    @app.get("/")
    async def serve_spa():
        """Serve the Single Page Application"""
        return FileResponse(os.path.join(static_path, "index.html"))
    
    # Handle other routes to support SPA
    @app.get("/{full_path:path}")
    async def serve_spa_paths(full_path: str):
        """Serve the Single Page Application for all other routes"""
        return FileResponse(os.path.join(static_path, "index.html"))
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    run()

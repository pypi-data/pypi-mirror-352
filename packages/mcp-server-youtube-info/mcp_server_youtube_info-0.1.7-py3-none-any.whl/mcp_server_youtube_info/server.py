from fastmcp import FastMCP, Image
import yt_dlp
import io
import httpx
from PIL import Image as PILImage

mcp = FastMCP("MCP YouTube Info Server", dependencies=["httpx", "Pillow"])

def _extract_info(video_id: str) -> dict:
    """Retrieve meta info of YouTube video using yt-dlp.

    Args:
        video_id (str): YouTube video ID

    Returns:
        dict: Video meta information
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            url = f"https://www.youtube.com/watch?v={video_id}"
            info = ydl.extract_info(url, download=False)
            return info
        except Exception as e:
            raise Exception(f"Failed to retrieve video information: {str(e)}")

@mcp.tool()
def youtube_metainfo(video_id: str) -> dict:
    """Retrieve meta info of YouTube video。

    Args:
        video_id (str): YouTube video ID

    Returns:
        dict: Video meta information
    """
    try:
        return _extract_info(video_id)
    except Exception as e:
        raise Exception(f"Failed to retrieve metadata: {str(e)}")

@mcp.tool()
def youtube_thumbnail_url(video_id: str) -> str:
    """Retrieve the thumbnail URL of a YouTube video.

    Args:
        video_id (str): YouTube Video ID

    Returns:
        str: Thumbnail URL
    """
    try:
        info = _extract_info(video_id)
        thumbnail_url = info.get('thumbnail')
        if not thumbnail_url:
            raise Exception("Cannot find thumbnail URL")
        return thumbnail_url
    except Exception as e:
        raise Exception(f"Failed to get thumbnail URL: {str(e)}")

@mcp.tool()
def youtube_thumbnail_image(video_id: str) -> Image:
    """
    Retrieve and download the thumbnail of a YouTube video as an Image.
    
    Args:
        video_id: YouTube Video ID
    Returns:
        Image: Image object containing the thumbnail data
    """
    try:
        info = _extract_info(video_id)
        thumbnail_url = info.get('thumbnail')
        if not thumbnail_url:
            raise Exception("Cannot find thumbnail URL")
    except Exception as e:
        raise Exception(f"Failed to get thumbnail URL: {str(e)}")
    
    try:
        with httpx.Client() as client:
            response = client.get(thumbnail_url)
            response.raise_for_status()
            
            image = PILImage.open(io.BytesIO(response.content)).convert('RGB')
            buffer = io.BytesIO()
            image.save(buffer, format="JPEG", quality=60, optimize=True)
            
            return Image(data=buffer.getvalue(), format="jpeg")
    except httpx.HTTPStatusError as e:
        raise Exception(f"HTTP Error: {e.response.status_code}")
    except PILImage.UnidentifiedImageError:
        raise Exception("Not a valid image format")
    except Exception as e:
        raise Exception(f"Failed to download image: {str(e)}")

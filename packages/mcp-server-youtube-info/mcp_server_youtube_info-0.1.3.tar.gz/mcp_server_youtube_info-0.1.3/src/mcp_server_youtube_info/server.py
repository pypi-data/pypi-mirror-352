from fastmcp import FastMCP, Image
import yt_dlp
import io
import httpx
from PIL import Image as PILImage

mcp = FastMCP("MCP YouTube Info Server", dependencies=["httpx", "Pillow"])

def _extract_info(video_id: str) -> dict:
    """YouTubeの動画情報を取得します。

    Args:
        video_id (str): YouTube動画ID

    Returns:
        dict: 動画情報
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
            raise Exception(f"動画情報の取得に失敗しました: {str(e)}")

@mcp.tool()
def youtube_metainfo(video_id: str) -> dict:
    """YouTube動画のメタ情報を取得します。

    Args:
        video_id (str): YouTube動画ID

    Returns:
        dict: yt-dlpから取得した生のメタ情報
    """
    try:
        return _extract_info(video_id)
    except Exception as e:
        raise Exception(f"メタ情報の取得に失敗しました: {str(e)}")

@mcp.tool()
def youtube_thumbnail_url(video_id: str) -> str:
    """YouTubeのサムネイルURLを取得します。

    Args:
        video_id (str): YouTube動画ID

    Returns:
        str: サムネイル画像のURL
    """
    try:
        info = _extract_info(video_id)
        thumbnail_url = info.get('thumbnail')
        if not thumbnail_url:
            raise Exception("サムネイルURLが見つかりません")
        return thumbnail_url
    except Exception as e:
        raise Exception(f"サムネイルの取得に失敗しました: {str(e)}")
@mcp.tool()
def youtube_thumbnail_image(video_id: str) -> Image:
    """
    指定されたYouTube動画のサムネイルをダウンロードし、Imageとして返す。
    
    Args:
        video_id: ダウンロードするyoutubeサムネイルのvideo_id
    Returns:
        Image: ダウンロードした画像データ
    """
    try:
        info = _extract_info(video_id)
        thumbnail_url = info.get('thumbnail')
        if not thumbnail_url:
            raise Exception("サムネイルURLが見つかりません")
    except Exception as e:
        raise Exception(f"サムネイルの取得に失敗しました: {str(e)}")
    
    try:
        with httpx.Client() as client:
            response = client.get(thumbnail_url)
            response.raise_for_status()
            
            # 画像を読み込んで圧縮
            image = PILImage.open(io.BytesIO(response.content)).convert('RGB')
            buffer = io.BytesIO()
            # image.save(buffer, format="JPEG", quality=60, optimize=True)
            image.save(buffer, format="JPEG", quality=60)
            
            return Image(data=buffer.getvalue(), format="jpeg")
    except httpx.HTTPStatusError as e:
        raise Exception(f"HTTPエラー: {e.response.status_code}")
    except PILImage.UnidentifiedImageError:
        raise Exception("有効な画像ファイルではありません")
    except Exception as e:
        raise Exception(f"画像のダウンロードに失敗しました: {str(e)}")
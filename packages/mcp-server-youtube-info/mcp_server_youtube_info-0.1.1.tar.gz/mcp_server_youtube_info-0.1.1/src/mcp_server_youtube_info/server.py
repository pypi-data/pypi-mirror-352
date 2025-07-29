from fastmcp import FastMCP
import yt_dlp

mcp = FastMCP("MCP YouTube Info Server")

def extract_info(video_id: str) -> dict:
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
def thumbnail(video_id: str) -> str:
    """YouTubeのサムネイルURLを取得します。

    Args:
        video_id (str): YouTube動画ID

    Returns:
        str: サムネイル画像のURL
    """
    try:
        info = extract_info(video_id)
        thumbnail_url = info.get('thumbnail')
        if not thumbnail_url:
            raise Exception("サムネイルURLが見つかりません")
        return thumbnail_url
    except Exception as e:
        raise Exception(f"サムネイルの取得に失敗しました: {str(e)}")

@mcp.tool()
def metainfo(video_id: str) -> dict:
    """YouTube動画のメタ情報を取得します。

    Args:
        video_id (str): YouTube動画ID

    Returns:
        dict: yt-dlpから取得した生のメタ情報
    """
    try:
        return extract_info(video_id)
    except Exception as e:
        raise Exception(f"メタ情報の取得に失敗しました: {str(e)}")

import yt_dlp

def get_video_info(video_id):
    """Get basic information about the YouTube video."""
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(
                f"https://www.youtube.com/watch?v={video_id}", 
                download=False
            )
        
        return {
            "title": info.get('title', 'Unknown'),
            "channel": info.get('uploader', 'Unknown'),
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "thumbnail": info.get('thumbnail', '')
        }
    except Exception as e:
        print(f"Error fetching video info: {str(e)}")
        return None
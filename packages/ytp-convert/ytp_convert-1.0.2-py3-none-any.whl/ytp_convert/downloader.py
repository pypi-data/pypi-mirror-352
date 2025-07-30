from pydub import AudioSegment
import tempfile
import os
from yt_dlp import YoutubeDL
from yt_dlp.utils import (
    DownloadError,
    ExtractorError,
    UnsupportedError,
)
from urllib.parse import urlparse, parse_qs

class PlaylistDownloader:
    """
    Downloads a YouTube playlist, extracts audio from each video, and combines all tracks into a single MP3 file.
    
    Attributes:
        playlist_link (str): The URL of the YouTube playlist to process.
    """
    class QuietLogger:
        def debug(self, msg): pass
        def warning(self, msg): pass
        def error(self, msg): print(f"❌ {msg}")


    def __init__(self, playlist_url: str):
        """
        Initialize the PlaylistDownloader with a YouTube playlist URL.
        
        Args:
            playlist_url (str): The URL of the YouTube playlist.
        """
        if not self._is_valid_playlist_url(playlist_url):
            raise ValueError(f"Invalid YouTube playlist URL - {playlist_url}")
        
        self.playlist_link = playlist_url
        self.total_videos: int = 0
        self.completed_downloads: int = 0
    
    def _progress_hook(self, d):
        if d['status'] == 'finished':
            self.completed_downloads += 1
            filename = os.path.basename(d['filename'])
            print(f"✅ ({self.completed_downloads}/{self.total_videos}) Finished: {filename}")

    def _is_valid_playlist_url(self, url: str) -> bool:
        """
        Validates whether the URL is a valid YouTube playlist URL.

        Args:
            url (str): The URL to validate.

        Returns:
            bool: True if valid, False otherwise.
        """
        parsed = urlparse(url)

        if not parsed.scheme.startswith("http"):
            return False
        if "youtube.com" not in parsed.netloc:
            return False
        if not parsed.path.startswith("/playlist"):
            return False
        query_params = parse_qs(parsed.query)
        list_param = query_params.get("list", [""])[0]

        return bool(list_param.strip())

    def downloadPlaylist(self, output_file: str = "combined.mp3", ignore_errors: bool = False) -> None:
        """
        Downloads all audio tracks from the playlist, merges them into a single MP3 file and writes it to disk. 

        Args:
            output_file (str): The filename for the final combined MP3 output. Defaults to 'combined.mp3'.
            ignore_errors (bool): Continue downloading the rest of the playlist even if some videos fail.

        Raises:
            Exception: If no MP3 audio files are downloaded.
        """
        output_file = output_file.strip()
        if not output_file.lower().endswith(".mp3"):
            raise ValueError(f"Invalid output file - '{output_file}'. The filename must end with '.mp3'")

        with tempfile.TemporaryDirectory(prefix="ytp2mp3_") as tmpdir:
            ydl_opts: dict = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(tmpdir, '%(playlist_index)03d_%(title).200s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'progress_hooks': [self._progress_hook],
                'logger': self.QuietLogger(),
                'noplaylist': False,
                'ignoreerrors': ignore_errors,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }

            # get num videos in the playlist
            with YoutubeDL({'quiet': True}) as probe:
                info = probe.extract_info(self.playlist_link, download=False)
                self.total_videos = len(info.get('entries', []))
            print(f"🎵 Found {self.total_videos} videos in the playlist.")
            if ignore_errors:
                print("⚠️ 'Force' mode enabled: will skip failed downloads.")
            else:
                print("🚫 'Force' mode not enabled: will abort on first error.")
                  
            try:
                with YoutubeDL(ydl_opts) as ydl:
                    print("\nDownloading playlist...")
                    ydl.download([self.playlist_link])
            except (DownloadError, UnsupportedError, ExtractorError) as e:
                raise RuntimeError(f"Youtube Download Failed: {e}")

            audio_files = sorted(
                [f for f in os.listdir(tmpdir) if f.endswith('.mp3')]
            )

            if not audio_files:
                raise Exception("No audio files found!")

            print("Combining audio...")
            combined = AudioSegment.empty()
            for fname in audio_files:
                path = os.path.join(tmpdir, fname)
                combined += AudioSegment.from_file(path)

            combined.export(output_file, format="mp3")
            print(f"🎧 Combined MP3 saved to: {output_file}")
            print("\n📊 Download Summary:")
            print(f"✅ Success: {self.completed_downloads}")
            print(f"❌ Skipped: {self.total_videos - self.completed_downloads}")

# test usage
if __name__ == "__main__":
    url = "https://youtube.com/playlist?list=PLERI1_ESTKAyaWKpE5I_uVpzbzmm4HkI5&si=DxlpgQkG3dBdNXdL" 
    downloader = PlaylistDownloader(url)
    downloader.downloadPlaylist()


    


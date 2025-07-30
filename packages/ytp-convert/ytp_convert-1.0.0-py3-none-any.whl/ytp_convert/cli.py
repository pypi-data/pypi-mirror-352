import argparse
from .downloader import PlaylistDownloader
import sys

def main():
    parser = argparse.ArgumentParser(
        description="Convert a YouTube playlist into a single combined file."
    )
    parser.add_argument("url", help="YouTube playlist URL to download")
    parser.add_argument(
        "-o", "--output",
        default="combined.mp3",
        help="Output MP3 filename (default: combined.mp3)"
    )
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Continue downloading the rest of the playlist even if some videos fail."
    )
    args = parser.parse_args()

    downloader = PlaylistDownloader(args.url)
    try:
        downloader.downloadPlaylist(output_file=args.output, ignore_errors=args.force)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
import os
import subprocess
import argparse
from pathlib import Path


def extract_keyframes(video_path: str, output_dir: str = "./tmp_keyframes_out") -> None:
    """
    Extract keyframes from an MP4 video file using ffmpeg.
    
    Args:
        video_path: Path to the input MP4 file
        output_dir: Directory to save extracted keyframes (default: ./tmp_keyframes_out)
    """
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Clear directory contents each run
    for file in output_path.glob("*"):
        if file.is_file():
            file.unlink()

    # Split the video into keyframes using mpdecimate and thumbnail filters
    # mcdecimate removes duplicate frames, thumbnail selects keyframes
    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-vf", "mpdecimate=hi=12800,thumbnail=5",
        "-vsync", "0",
        os.path.join(output_dir, "keyframe_%03d.jpg"),
    ]
    
    try:
        # Run ffmpeg command
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"Keyframes extracted successfully to {output_dir}")
        
        # Count extracted frames
        output_files = list(Path(output_dir).glob("keyframe_*.jpg"))
        print(f"Extracted {len(output_files)} keyframes")
        
    except subprocess.CalledProcessError as e:
        print(f"Error extracting keyframes: {e}")
        print(f"FFmpeg stderr: {e.stderr}")
        raise
    except FileNotFoundError:
        print("Error: ffmpeg not found. Please ensure ffmpeg is installed and in your PATH.")
        raise


def main():
    """Main method to run the keyframe extraction utility."""
    parser = argparse.ArgumentParser(description="Extract keyframes from MP4 video files")
    parser.add_argument("video_path", help="Path to the input MP4 file")
    parser.add_argument(
        "-o", "--output", 
        default="./tmp_keyframes_out",
        help="Output directory for extracted keyframes (default: ./tmp_keyframes_out)"
    )
    
    args = parser.parse_args()
    
    # Validate input file exists
    if not os.path.exists(args.video_path):
        print(f"Error: Video file not found: {args.video_path}")
        return 1
    
    # Validate input file is MP4
    if not args.video_path.lower().endswith('.mp4'):
        print("Error: Input file must be an MP4 file")
        return 1
    
    try:
        extract_keyframes(args.video_path, args.output)
        return 0
    except Exception as e:
        print(f"Failed to extract keyframes: {e}")
        return 1


if __name__ == "__main__":
    exit(main())

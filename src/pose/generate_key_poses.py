import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import List

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.keyframing.extract_keyframes import extract_keyframes
from src.pose.pose import Pose
from src.google.mediapipe.pose_extraction import extract_pose_from_image


def generate_key_poses(video_path: str) -> List[Pose]:
    """
    Extract keyframes from an MP4 video file and generate poses from each keyframe.
    
    Args:
        video_path: Path to the input MP4 file
        
    Returns:
        List[Pose]: List of Pose objects extracted from keyframes
    """
    # Create temporary directory for keyframes
    temp_dir = tempfile.mkdtemp(prefix="keyframes_")
    
    try:
        # Extract keyframes from video
        print(f"Extracting keyframes from {video_path}...")
        extract_keyframes(video_path, temp_dir)
        
        # Get list of extracted keyframe images
        keyframe_files = sorted(Path(temp_dir).glob("keyframe_*.jpg"))
        
        if not keyframe_files:
            print("No keyframes were extracted")
            return []
        
        print(f"Found {len(keyframe_files)} keyframes")
        
        poses: List[Pose] = []
        
        # Process each keyframe
        for i, keyframe_path in enumerate(keyframe_files):
            print(f"Processing keyframe {i+1}/{len(keyframe_files)}: {keyframe_path.name}")
            
            try:
                # Extract pose from keyframe using the existing function
                pose = extract_pose_from_image(str(keyframe_path))
                
                # Only add pose if landmarks were detected
                if pose.nodes:
                    poses.append(pose)
                    print(f"  - Extracted pose with {len(pose.nodes)} landmarks")
                else:
                    print(f"  - No pose detected in keyframe")
                    
            except Exception as e:
                print(f"  - Error processing keyframe {keyframe_path.name}: {e}")
                continue
        
        print(f"Successfully generated {len(poses)} poses from {len(keyframe_files)} keyframes")
        return poses
        
    finally:
        # Clean up temporary directory
        try:
            shutil.rmtree(temp_dir)
            print(f"Cleaned up temporary directory: {temp_dir}")
        except Exception as e:
            print(f"Warning: Could not clean up temporary directory {temp_dir}: {e}")


def main():
    """Main method to run the key pose generation utility."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate poses from keyframes in MP4 video files")
    parser.add_argument("video_path", help="Path to the input MP4 file")
    
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
        poses = generate_key_poses(args.video_path)
        
        if poses:
            print(f"\nGenerated {len(poses)} poses:")
            for i, pose in enumerate(poses):
                print(f"  Pose {i+1}: {pose}")
        else:
            print("No poses were generated")
            
        return 0
        
    except Exception as e:
        print(f"Failed to generate poses: {e}")
        return 1


if __name__ == "__main__":
    exit(main())

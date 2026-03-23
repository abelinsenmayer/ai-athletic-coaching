import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import mediapipe as mp
import argparse
import cv2
from src.pose.pose import Pose


def extract_pose_from_image(image_path: str) -> Pose:
    """
    Extract pose landmarks from an image at the given path.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Dictionary containing pose landmarks data or None if no pose detected
    """
    model_path = 'C:\\Users\\abeli\\OneDrive\\Desktop\\pose_landmarker_lite.task'

    BaseOptions = mp.tasks.BaseOptions
    PoseLandmarker = mp.tasks.vision.PoseLandmarker
    PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
    VisionRunningMode = mp.tasks.vision.RunningMode

    options = PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=model_path),
        running_mode=VisionRunningMode.IMAGE,
        output_segmentation_masks=True)

    mp_image = mp.Image.create_from_file(image_path)

    with PoseLandmarker.create_from_options(options) as landmarker:
        # Perform pose landmarking on the provided image
        pose_landmarker_result = landmarker.detect(mp_image)
        
        # Convert to Pose representation and return
        pose = Pose()
        cv2img = cv2.imread(image_path)
        h, w, _ = cv2img.shape
        pose.from_pose_landmarker_result(pose_landmarker_result, w, h)
        return pose


def preview_image(image_path):
    img = cv2.imread(image_path)
    cv2.imshow("Image", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def preview_segmentation_mask(mask):
    mask_np = mask.numpy_view()
    cv2.imshow("Segmentation Mask", mask_np)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser(description='Extract pose from image')
    parser.add_argument('image_path', type=str, help='Path to the image file')
    args = parser.parse_args()
    
    extract_pose_from_image(args.image_path)


if __name__ == "__main__":
    main()

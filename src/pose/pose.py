from typing import List, Dict
from .pose_node import PoseNode
import matplotlib.pyplot as plt
import numpy as np


class Pose:
    def __init__(self):
        self.nodes: Dict[str, PoseNode] = {}
        self.vectorRepresentation: List[float] = []

    def plot(self):
        """
        Plot the pose using matplotlib.
        """

        # Plot pose nodes
        absMinY = abs(min(-node.y for node in self.nodes.values()))

        xs = [node.x for node in self.nodes.values()]
        ys = [-node.y + absMinY for node in self.nodes.values()]
        zs = [node.z for node in self.nodes.values()]

        fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
        ax.scatter(xs, zs, ys)

        # ax.set(yticklabels=[], xticklabels=[])

        ax.set_xlabel('X')
        ax.set_xlim(-2.5, 2.5)

        ax.set_ylabel('Y')
        ax.set_ylim(-2.5, 2.5)

        ax.set_zlabel('Z')
        ax.set_zlim(0, 5)

        # A list of connections (start_name, end_name) based on MediaPipe Pose Map
        POSE_CONNECTIONS = [
            # Face connections
            ("nose", "left eye (inner)"),
            ("left eye (inner)", "left eye"),
            ("left eye", "left eye (outer)"),
            ("left eye (outer)", "left ear"),
            ("nose", "right eye (inner)"),
            ("right eye (inner)", "right eye"),
            ("right eye", "right eye (outer)"),
            ("right eye (outer)", "right ear"),
            ("mouth (left)", "mouth (right)"),
            
            # Arm connections
            ("left shoulder", "right shoulder"), 
            ("left shoulder", "left elbow"), 
            ("left elbow", "left wrist"), 
            ("right shoulder", "right elbow"), 
            ("right elbow", "right wrist"),
            
            # Hand connections
            ("left wrist", "left pinky"),
            ("left wrist", "left index"),
            ("left wrist", "left thumb"),
            ("right wrist", "right pinky"),
            ("right wrist", "right index"),
            ("right wrist", "right thumb"),
            
            # Torso connections
            ("left shoulder", "left hip"), 
            ("right shoulder", "right hip"), 
            ("left hip", "right hip"),
            
            # Leg connections
            ("left hip", "left knee"), 
            ("right hip", "right knee"), 
            ("left knee", "left ankle"), 
            ("right knee", "right ankle"),
            
            # Foot connections
            ("left ankle", "left heel"),
            ("left heel", "left foot index"),
            ("left ankle", "left foot index"),
            ("right ankle", "right heel"),
            ("right heel", "right foot index"),
            ("right ankle", "right foot index"),
        ]
        
        # Plot skeleton lines
        for connection in POSE_CONNECTIONS:
            start = self.nodes[connection[0]]
            end = self.nodes[connection[1]]
            ax.plot([start.x, end.x], [start.z, end.z], [-start.y + absMinY, -end.y + absMinY], c='b')

        plt.show()

    
    def from_pose_landmarker_result(self, landmarker_result, image_width, image_height):
        """
        Create a Pose from a PoseLandmarkerResult.
        
        Args:
            landmarker_result: The PoseLandmarkerResult to convert
            
        Returns:
            Pose: The created Pose object
        """
        # Landmark names mapping
        landmark_names = [
            "nose", "left eye (inner)", "left eye", "left eye (outer)",
            "right eye (inner)", "right eye", "right eye (outer)", "left ear", "right ear",
            "mouth (left)", "mouth (right)", "left shoulder", "right shoulder", "left elbow",
            "right elbow", "left wrist", "right wrist", "left pinky", "right pinky",
            "left index", "right index", "left thumb", "right thumb", "left hip", "right hip",
            "left knee", "right knee", "left ankle", "right ankle", "left heel", "right heel",
            "left foot index", "right foot index"
        ]
        
        # Clear existing nodes and vector representation
        self.nodes = {}
        self.vectorRepresentation = []
        
        # Iterate through pose landmarks
        if landmarker_result.pose_world_landmarks and len(landmarker_result.pose_world_landmarks) > 0:
            landmarks = landmarker_result.pose_world_landmarks[0]
            
            # Create PoseNode objects first
            for i, landmark in enumerate(landmarks):
                if i < len(landmark_names):
                    pose_node = PoseNode(
                        x=landmark.x,
                        y=landmark.y,
                        z=landmark.z,
                        name=landmark_names[i]
                    )
                    self.nodes[pose_node.name] = pose_node
            
            # Normalize pose so shoulder distance is 1
            self._normalize_shoulder_distance()
            
            # Calculate reference points after all nodes are created
            right_hip = None
            left_hip = None
            right_shoulder = None
            left_shoulder = None
            
            if "right hip" in self.nodes:
                right_hip = (self.nodes["right hip"].x, self.nodes["right hip"].y, self.nodes["right hip"].z)
            if "left hip" in self.nodes:
                left_hip = (self.nodes["left hip"].x, self.nodes["left hip"].y, self.nodes["left hip"].z)
            if "right shoulder" in self.nodes:
                right_shoulder = (self.nodes["right shoulder"].x, self.nodes["right shoulder"].y, self.nodes["right shoulder"].z)
            if "left shoulder" in self.nodes:
                left_shoulder = (self.nodes["left shoulder"].x, self.nodes["left shoulder"].y, self.nodes["left shoulder"].z)
            
            # Calculate average shoulder position
            avg_shoulder = None
            if right_shoulder and left_shoulder:
                avg_shoulder = (
                    (right_shoulder[0] + left_shoulder[0]) / 2,
                    (right_shoulder[1] + left_shoulder[1]) / 2,
                    (right_shoulder[2] + left_shoulder[2]) / 2
                )
            
            # Calculate vector representation using distances to reference points
            reference_points = []
            if right_hip:
                reference_points.append(right_hip)
            if left_hip:
                reference_points.append(left_hip)
            if avg_shoulder:
                reference_points.append(avg_shoulder)
            
            # For each node, calculate distance to each reference point
            for node in self.nodes.values():
                node_coords = (node.x, node.y, node.z)
                for ref_point in reference_points:
                    # Calculate 3D Euclidean distance
                    distance = (
                        (node_coords[0] - ref_point[0]) ** 2 +
                        (node_coords[1] - ref_point[1]) ** 2 +
                        (node_coords[2] - ref_point[2]) ** 2
                    ) ** 0.5
                    self.vectorRepresentation.append(distance)
        
        return self
    
    def _normalize_shoulder_distance(self):
        """
        Normalize all pose coordinates so that the distance between right shoulder 
        and left shoulder is always 1. All other coordinates are scaled proportionally.
        """
        if "right shoulder" not in self.nodes or "left shoulder" not in self.nodes:
            return  # Cannot normalize if shoulders are not available
        
        # Get shoulder coordinates
        right_shoulder = self.nodes["right shoulder"]
        left_shoulder = self.nodes["left shoulder"]
        
        # Calculate current shoulder distance
        shoulder_distance = (
            (right_shoulder.x - left_shoulder.x) ** 2 +
            (right_shoulder.y - left_shoulder.y) ** 2 +
            (right_shoulder.z - left_shoulder.z) ** 2
        ) ** 0.5
        
        if shoulder_distance == 0:
            return  # Cannot normalize if shoulders are at the same position
        
        # Calculate scaling factor to make shoulder distance = 1
        scale_factor = 1.0 / shoulder_distance
        
        # Scale all coordinates around the origin (0, 0, 0)
        for node in self.nodes.values():
            node.x *= scale_factor
            node.y *= scale_factor
            node.z *= scale_factor
    
    def __repr__(self):
        nodes = ", ".join([f"{name}:{node}" for name, node in self.nodes.items()])
        return f"Pose(nodes={nodes})"

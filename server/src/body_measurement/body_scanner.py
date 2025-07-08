"""
Computer Vision Body Measurement System
Uses MediaPipe Pose detection to analyze body proportions from multiple angles
"""

import mediapipe as mp
import cv2
import numpy as np
import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Import our existing recommendation engine types
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'style_engine'))
from recommendation_engine import BodyMeasurements, BodyType, determine_body_shape

class PhotoAngle(Enum):
    FRONT = "front"
    SIDE = "side"
    BACK = "back"

@dataclass
class BodyLandmarks:
    """Stores pose landmarks for body measurement analysis"""
    angle: PhotoAngle
    landmarks: List[Tuple[float, float]]  # (x, y) coordinates
    image_width: int
    image_height: int
    confidence: float

@dataclass
class BodyRatios:
    """Calculated body ratios from pose analysis"""
    shoulder_to_hip_ratio: float
    waist_to_hip_ratio: float
    waist_to_shoulder_ratio: float
    shoulder_width_pixels: float
    waist_width_pixels: float
    hip_width_pixels: float

class BodyScanner:
    """Computer vision body measurement system using MediaPipe Pose"""
    
    def __init__(self):
        """Initialize MediaPipe pose detection"""
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=True,
            model_complexity=2,  # Higher accuracy
            enable_segmentation=False,
            min_detection_confidence=0.7
        )
        self.mp_drawing = mp.solutions.drawing_utils
    
    def analyze_photo(self, image_path: str, angle: PhotoAngle) -> Optional[BodyLandmarks]:
        """
        Analyze a single photo for pose landmarks
        
        Args:
            image_path: Path to the image file
            angle: Which angle this photo represents
            
        Returns:
            BodyLandmarks object or None if analysis failed
        """
        # Read and process image
        image = cv2.imread(image_path)
        if image is None:
            print(f"Error: Could not load image from {image_path}")
            return None
        
        # Convert BGR to RGB for MediaPipe
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Detect pose
        results = self.pose.process(rgb_image)
        
        if not results.pose_landmarks:
            print(f"No pose detected in {image_path}")
            return None
        
        # Extract landmark coordinates
        landmarks = []
        for landmark in results.pose_landmarks.landmark:
            # Convert normalized coordinates to pixel coordinates
            x = int(landmark.x * image.shape[1])
            y = int(landmark.y * image.shape[0])
            landmarks.append((x, y))
        
        # Calculate average confidence
        confidence = np.mean([lm.visibility for lm in results.pose_landmarks.landmark])
        
        return BodyLandmarks(
            angle=angle,
            landmarks=landmarks,
            image_width=image.shape[1],
            image_height=image.shape[0],
            confidence=confidence
        )
    
    def calculate_body_ratios(self, front_landmarks: BodyLandmarks) -> Optional[BodyRatios]:
        """
        Calculate body ratios from front-view landmarks
        
        MediaPipe Pose landmark indices:
        - 11, 12: Left and right shoulders
        - 23, 24: Left and right hips
        - Waist: Estimated as midpoint between shoulders and hips
        
        Args:
            front_landmarks: Pose landmarks from front view
            
        Returns:
            BodyRatios object with calculated measurements
        """
        if len(front_landmarks.landmarks) < 25:  # Need at least hip landmarks
            return None
        
        landmarks = front_landmarks.landmarks
        
        # Get key landmark coordinates
        left_shoulder = landmarks[11]   # Left shoulder
        right_shoulder = landmarks[12]  # Right shoulder
        left_hip = landmarks[23]        # Left hip
        right_hip = landmarks[24]       # Right hip
        
        # Calculate shoulder width (distance between shoulders)
        shoulder_width = self._calculate_distance(left_shoulder, right_shoulder)
        
        # Calculate hip width (distance between hips)
        hip_width = self._calculate_distance(left_hip, right_hip)
        
        # Estimate waist width (typically 0.7-0.8 of shoulder width for most body types)
        # We'll use pose landmarks to estimate this better
        waist_width = self._estimate_waist_width(front_landmarks)
        
        # Calculate ratios
        shoulder_to_hip_ratio = shoulder_width / hip_width if hip_width > 0 else 1.0
        waist_to_hip_ratio = waist_width / hip_width if hip_width > 0 else 1.0
        waist_to_shoulder_ratio = waist_width / shoulder_width if shoulder_width > 0 else 1.0
        
        return BodyRatios(
            shoulder_to_hip_ratio=shoulder_to_hip_ratio,
            waist_to_hip_ratio=waist_to_hip_ratio,
            waist_to_shoulder_ratio=waist_to_shoulder_ratio,
            shoulder_width_pixels=shoulder_width,
            waist_width_pixels=waist_width,
            hip_width_pixels=hip_width
        )
    
    def _calculate_distance(self, point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        """Calculate Euclidean distance between two points"""
        return math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)
    
    def _estimate_waist_width(self, front_landmarks: BodyLandmarks) -> float:
        """
        Estimate waist width using pose landmarks
        Uses the narrowest point between shoulders and hips
        """
        landmarks = front_landmarks.landmarks
        
        # Get shoulder and hip y-coordinates for vertical reference
        shoulder_y = (landmarks[11][1] + landmarks[12][1]) / 2
        hip_y = (landmarks[23][1] + landmarks[24][1]) / 2
        
        # Estimate waist y-coordinate (roughly 60% down from shoulders to hips)
        waist_y = shoulder_y + 0.6 * (hip_y - shoulder_y)
        
        # For waist width, we'll use a proportion of shoulder width
        # This is an estimation - in a more advanced system, we'd use body contour detection
        shoulder_width = self._calculate_distance(landmarks[11], landmarks[12])
        
        # Typical waist is 70-85% of shoulder width depending on body type
        estimated_waist_width = shoulder_width * 0.75  # Conservative estimate
        
        return estimated_waist_width
    
    def convert_ratios_to_measurements(self, ratios: BodyRatios, reference_measurement: float = 36.0) -> BodyMeasurements:
        """
        Convert pixel ratios to inch measurements using a reference
        
        Args:
            ratios: Calculated body ratios
            reference_measurement: Reference measurement in inches (default: assume 36" shoulders)
            
        Returns:
            BodyMeasurements object for use with recommendation engine
        """
        # Use reference as shoulder measurement
        shoulders = reference_measurement
        
        # Calculate other measurements based on ratios
        hips = shoulders / ratios.shoulder_to_hip_ratio
        waist = shoulders * ratios.waist_to_shoulder_ratio
        bust = shoulders  # Approximate bust as shoulder width for now
        
        return BodyMeasurements(
            shoulders=shoulders,
            bust=bust,
            waist=waist,
            hips=hips
        )
    
    def analyze_body_shape_from_photos(self, photo_paths: Dict[PhotoAngle, str], reference_measurement: float = 36.0) -> Dict:
        """
        Complete body shape analysis from multiple photo angles
        
        Args:
            photo_paths: Dictionary mapping PhotoAngle to image file paths
            reference_measurement: Reference measurement in inches
            
        Returns:
            Dictionary with analysis results, body shape, and measurements
        """
        results = {
            "success": False,
            "landmarks": {},
            "ratios": None,
            "measurements": None,
            "body_shape": None,
            "confidence": 0.0,
            "errors": []
        }
        
        # Analyze each photo
        for angle, path in photo_paths.items():
            landmarks = self.analyze_photo(path, angle)
            if landmarks:
                results["landmarks"][angle] = landmarks
                print(f"[SUCCESS] Successfully analyzed {angle.value} view")
            else:
                results["errors"].append(f"Failed to analyze {angle.value} view from {path}")
        
        # We need at least front view for body shape analysis
        if PhotoAngle.FRONT not in results["landmarks"]:
            results["errors"].append("Front view is required for body shape analysis")
            return results
        
        # Calculate ratios from front view
        front_landmarks = results["landmarks"][PhotoAngle.FRONT]
        ratios = self.calculate_body_ratios(front_landmarks)
        
        if not ratios:
            results["errors"].append("Failed to calculate body ratios")
            return results
        
        results["ratios"] = ratios
        results["confidence"] = front_landmarks.confidence
        
        # Convert to measurements
        measurements = self.convert_ratios_to_measurements(ratios, reference_measurement)
        results["measurements"] = measurements
        
        # Determine body shape
        body_shape = determine_body_shape(measurements)
        results["body_shape"] = body_shape
        
        results["success"] = True
        return results
    
    def visualize_landmarks(self, image_path: str, output_path: str, angle: PhotoAngle):
        """
        Create visualization of detected landmarks on the image
        
        Args:
            image_path: Path to input image
            output_path: Path to save annotated image
            angle: Photo angle for labeling
        """
        landmarks = self.analyze_photo(image_path, angle)
        if not landmarks:
            print(f"Cannot visualize - no landmarks detected in {image_path}")
            return
        
        # Load original image
        image = cv2.imread(image_path)
        
        # Create pose landmarks object for drawing
        pose_landmarks = self.mp_pose.PoseLandmark
        connections = self.mp_pose.POSE_CONNECTIONS
        
        # Draw landmarks
        # Note: This is a simplified version - in practice you'd recreate the MediaPipe results object
        
        # Draw key measurement points
        key_points = {
            "Left Shoulder": landmarks.landmarks[11],
            "Right Shoulder": landmarks.landmarks[12],
            "Left Hip": landmarks.landmarks[23],
            "Right Hip": landmarks.landmarks[24]
        }
        
        for label, point in key_points.items():
            cv2.circle(image, (int(point[0]), int(point[1])), 10, (0, 255, 0), -1)
            cv2.putText(image, label, (int(point[0]) + 15, int(point[1])), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        # Draw measurement lines
        if len(landmarks.landmarks) > 24:
            # Shoulder width line
            cv2.line(image, 
                    (int(landmarks.landmarks[11][0]), int(landmarks.landmarks[11][1])),
                    (int(landmarks.landmarks[12][0]), int(landmarks.landmarks[12][1])),
                    (255, 0, 0), 3)
            
            # Hip width line
            cv2.line(image, 
                    (int(landmarks.landmarks[23][0]), int(landmarks.landmarks[23][1])),
                    (int(landmarks.landmarks[24][0]), int(landmarks.landmarks[24][1])),
                    (0, 0, 255), 3)
        
        # Add title
        cv2.putText(image, f"{angle.value.title()} View - Body Analysis", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Save annotated image
        cv2.imwrite(output_path, image)
        print(f"Visualization saved to {output_path}")
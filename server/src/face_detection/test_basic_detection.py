import mediapipe as mp
import cv2
import math

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=True,
    max_num_faces = 1,
    refine_landmarks = True,
    min_detection_confidence=.5)
testimage = cv2.imread("../../../data/testimage.jpg")
rgb_image = cv2.cvtColor(testimage, cv2.COLOR_BGR2RGB)
res = face_mesh.process(rgb_image)

print("testimage.shape: ", testimage.shape)
print("res.multi_face_landmarks: ", res.multi_face_landmarks)

def unnormalize_xy(normalized_x, normalized_y, image_width, image_height):
    pixel_x = int(normalized_x * image_width)
    pixel_y = int(normalized_y * image_height)
    return (pixel_x, pixel_y)

def render_landmarks(image, landmarks):
    unnormalized_landmarks = []
    for face_landmarks in landmarks:
        for landmark in face_landmarks.landmark:
            unnormalized_landmarks.append(unnormalize_xy(landmark.x, landmark.y, testimage.shape[1], testimage.shape[0]))

    for landmark in unnormalized_landmarks:
        cv2.circle(image, landmark, 4, (255, 0, 0), -1)

    return image
rendered_image = render_landmarks(testimage, res.multi_face_landmarks)
cv2.imwrite("../../../data/testimage_alllandmarks.jpg", rendered_image)
# Key landmark indices for face measurements
KEY_LANDMARKS = {
    'face_outline': [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109],
    'measurement_points': {
        'chin': 152,
        'forehead': 10, 
        'left_face': 234,
        'right_face': 454,
        'left_eye_outer': 33,
        'right_eye_outer': 263
    }
}

def render_key_landmarks(image, landmarks):
    """Render only key landmarks for face measurements with different colors"""
    if not landmarks:
        return image
    
    face_landmarks = landmarks[0]  # Get first face
    
    # Draw face outline in blue
    for idx in KEY_LANDMARKS['face_outline']:
        landmark = face_landmarks.landmark[idx]
        pixel_coords = unnormalize_xy(landmark.x, landmark.y, image.shape[1], image.shape[0])
        cv2.circle(image, pixel_coords, 6, (255, 0, 0), -1)  # Blue
    
    # Draw measurement points in different colors
    colors = {
        'chin': (0, 255, 0),        # Green
        'forehead': (0, 255, 0),    # Green  
        'left_face': (0, 0, 255),   # Red
        'right_face': (0, 0, 255),  # Red
        'left_eye_outer': (255, 255, 0),  # Cyan
        'right_eye_outer': (255, 255, 0)  # Cyan
    }
    
    for point_name, idx in KEY_LANDMARKS['measurement_points'].items():
        landmark = face_landmarks.landmark[idx]
        pixel_coords = unnormalize_xy(landmark.x, landmark.y, image.shape[1], image.shape[0])
        color = colors[point_name]
        cv2.circle(image, pixel_coords, 10, color, -1)
    
    return image

def calculate_face_measurements(landmarks):
    """Calculate key face measurements for shape classification"""
    if not landmarks:
        return None
    
    face_landmarks = landmarks[0]  # Get first face
    
    # Get key points as (x, y) coordinates
    def get_point(idx):
        landmark = face_landmarks.landmark[idx]
        return (landmark.x, landmark.y)
    
    # Calculate distance between two points
    def distance(point1, point2):
        return math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)
    
    # Get key measurement points
    chin = get_point(KEY_LANDMARKS['measurement_points']['chin'])
    forehead = get_point(KEY_LANDMARKS['measurement_points']['forehead'])
    left_face = get_point(KEY_LANDMARKS['measurement_points']['left_face'])
    right_face = get_point(KEY_LANDMARKS['measurement_points']['right_face'])
    left_eye_outer = get_point(KEY_LANDMARKS['measurement_points']['left_eye_outer'])
    right_eye_outer = get_point(KEY_LANDMARKS['measurement_points']['right_eye_outer'])
    
    # Calculate measurements
    measurements = {
        'face_length': distance(forehead, chin),
        'face_width': distance(left_face, right_face),
        'eye_width': distance(left_eye_outer, right_eye_outer),
        'face_ratio': 0,  # Will calculate after getting measurements
    }
    
    # Calculate face ratio (length/width)
    if measurements['face_width'] > 0:
        measurements['face_ratio'] = measurements['face_length'] / measurements['face_width']
    
    return measurements

rendered_key_image = render_key_landmarks(testimage, res.multi_face_landmarks)
cv2.imwrite("../../../data/testimage_key_landmarks.jpg", rendered_key_image)

# Calculate face measurements
measurements = calculate_face_measurements(res.multi_face_landmarks)
if measurements:
    print("\n=== FACE MEASUREMENTS ===")
    print(f"Face Length: {measurements['face_length']:.4f}")
    print(f"Face Width: {measurements['face_width']:.4f}")
    print(f"Eye Width: {measurements['eye_width']:.4f}")
    print(f"Face Ratio (L/W): {measurements['face_ratio']:.4f}")
    print("\n=== FACE SHAPE ANALYSIS ===")
    
    # Basic face shape classification based on research
    ratio = measurements['face_ratio']
    if ratio < 1.1:
        print("Face Shape: ROUND (ratio < 1.1)")
    elif ratio < 1.3:
        print("Face Shape: OVAL (1.1 ≤ ratio < 1.3)")
    elif ratio < 1.6:
        print("Face Shape: OBLONG (1.3 ≤ ratio < 1.6)")
    else:
        print("Face Shape: LONG (ratio ≥ 1.6)")
else:
    print("No measurements could be calculated")




import mediapipe as mp
import cv2

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=True,
    max_num_faces = 1,
    refine_landmarks = True,
    min_detection_confidence=.5)
testimage = cv2.imread("../../../data/testimage.jpg")
rgb_image = cv2.cvtColor(testimage, cv2.COLOR_BGR2RGB)
res = face_mesh.process(rgb_image)

print(res.multi_face_landmarks)
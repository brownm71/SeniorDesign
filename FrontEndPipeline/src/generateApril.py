import cv2

# --- 1. GENERATING THE APRILTAG ---

# Fetch the AprilTag dictionary (36h11 is the most robust and widely used family)
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36h11)

# Generate a marker with ID=42, size=200x200 pixels
marker_id = 42
marker_size = 3840
marker_image = cv2.aruco.generateImageMarker(dictionary, marker_id, marker_size)

# Save the generated tag
cv2.imwrite("apriltag_42.png", marker_image)
print(f"Generated AprilTag ID {marker_id} saved as 'apriltag_42.png'")
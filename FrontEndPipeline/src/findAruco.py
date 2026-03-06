import cv2
import numpy as np

from PIL import Image


def detect_high_accuracy_marker_zero(image):
    """
    Detects ArUco marker ID=0 in an image and applies sub-pixel 
    refinement to its corners for maximum geometric accuracy.
    
    Args:
        image: A BGR image/frame from your camera.
        
    Returns:
        corners: A numpy array of shape (4, 2) containing the precise 
                 (x, y) coordinates of the marker's corners, or None if not found.
    """
    # 1. Convert to grayscale (required for optimal ArUco detection)
    image = Image.open(image) # Load image
    image = np.array(image)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 2. Load the exact dictionary we used to generate the marker
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    
    # 3. Initialize the detector parameters
    parameters = cv2.aruco.DetectorParameters()
    
    # --- THE CRITICAL STEP FOR HIGH ACCURACY ---
    # Enable sub-pixel corner refinement. 
    parameters.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
    
    # Optional but helpful: Tune the sub-pixel window size. 
    # This dictates how many pixels around the rough corner the algorithm 
    # looks at to find the exact sub-pixel corner. Default is usually fine, 
    # but you can increase it slightly if your marker is very large in the frame.
    parameters.cornerRefinementWinSize = 5 
    
    # 4. Create the detector object (Modern OpenCV 4.7+ syntax)
    detector = cv2.aruco.ArucoDetector(dictionary, parameters)
    
    # 5. Detect all markers in the frame
    # 'corners' is a list of arrays containing the pixel coordinates.
    # 'ids' is a list of the detected marker IDs.
    corners, ids, rejected = detector.detectMarkers(gray)
    
    # 6. Filter for ID == 0
    if ids is not None:
        for i, marker_id in enumerate(ids):
            if marker_id[0] == 0:
                # We found marker ID 0! 
                # Extract its specific corners. Shape is (1, 4, 2), we return (4, 2)
                marker_0_corners = corners[i][0]
                
                # Optional: Draw the detection on the image for debugging
                # cv2.aruco.drawDetectedMarkers(image, corners, ids)
                
                return marker_0_corners
                
    # Return None if the marker wasn't found in this frame
    return None

# --- Example Usage ---
# cap = cv2.VideoCapture(0)
# ret, frame = cap.read()
# if ret:
#     precise_corners = detect_high_accuracy_marker_zero(frame)
#     if precise_corners is not None:
#         print("Precise Sub-pixel Corners for ID 0:\n", precise_corners)
#         # Order is: Top-Left, Top-Right, Bottom-Right, Bottom-Left

if __name__ == "__main__":
    print(detect_high_accuracy_marker_zero(r"C:\Users\Mike\Desktop\Senior Design\frames\frame_0000.png"))
import cv2
import numpy as np
from findAruco import *

# 16.5 cm

def calculate_homography(marker_pixel_corners, marker_size_cm):
    """
    Calculates the 3x3 Homography matrix based on the reference marker.
    
    Args:
        marker_pixel_corners: List or array of 4 pixel coordinates [(u1,v1), (u2,v2), ...].
                              Order: Top-Left, Top-Right, Bottom-Right, Bottom-Left.
        marker_size_cm: Physical width/height of the square marker.
        
    Returns:
        H: 3x3 Homography matrix.
    """
    # Define the real-world corners in cm
    world_corners = np.array([
        [0, 0],                               # Top-Left
        [marker_size_cm, 0],                  # Top-Right
        [marker_size_cm, marker_size_cm],     # Bottom-Right
        [0, marker_size_cm]                   # Bottom-Left
    ], dtype=np.float32)
    
    # Format the pixel corners as a float32 numpy array
    pixel_corners = np.array(marker_pixel_corners, dtype=np.float32)
    
    # Find the matrix. RANSAC helps ignore small detection errors in the corners.
    H, _ = cv2.findHomography(pixel_corners, world_corners, cv2.RANSAC)
    
    return H

def get_2d_localization_homography(object_pixel, H):
    """
    Transforms a pixel coordinate to a real-world coordinate using Homography.
    
    Args:
        object_pixel: (u, v) pixel coordinate of the object.
        H: 3x3 Homography matrix.
        
    Returns:
        (X, Y): Real-world coordinates relative to the marker's top-left corner.
    """
    # cv2.perspectiveTransform expects a 3D array of shape (1, N, 2)
    obj_pt_array = np.array([[object_pixel]], dtype=np.float32)
    
    # Apply the homography transformation
    world_pt_array = cv2.perspectiveTransform(obj_pt_array, H)
    
    # Extract the X and Y coordinates
    X_cm = world_pt_array[0, 0, 0]
    Y_cm = world_pt_array[0, 0, 1]
    
    return (X_cm, Y_cm)

# --- Example Usage ---
# Suppose you detected the marker's corners at these pixels:
# qr_pixels = [(100, 100), (300, 110), (290, 310), (90, 300)]
# marker_size = 5.0  # 5 cm marker

# 1. Calculate the Homography matrix once per frame
# H_matrix = calculate_homography(qr_pixels, marker_size)

# 2. Localize your objects using that matrix
# object_pixel = (450, 600)
# X, Y = get_2d_localization_homography(object_pixel, H_matrix)
# print(f"Object is located at X: {X:.2f} cm, Y: {Y:.2f} cm")

if __name__ == "__main__":
    locationArray = detect_high_accuracy_marker_zero(r"C:\Users\Mike\Desktop\Senior Design\frames\frame_0000.png")
    print(calculate_homography(locationArray, 16.5))
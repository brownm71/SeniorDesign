import cv2
import numpy as np

def generate_aruco_marker(marker_id, pixel_size, output_filename):
    """
    Generates a high-resolution ArUco marker and saves it as an image.
    
    Args:
        marker_id: The ID of the marker (e.g., 0).
        pixel_size: The width/height of the output image in pixels (e.g., 1000).
        output_filename: The file path to save the image (e.g., 'marker_0.png').
    """
    # Load a predefined dictionary. 
    # DICT_4X4_50 is great for single-marker setups (large blocks, easily visible)
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    
    # Generate the marker image
    marker_image = np.zeros((pixel_size, pixel_size), dtype=np.uint8)
    marker_image = cv2.aruco.generateImageMarker(dictionary, marker_id, pixel_size)
    
    # Save the image
    cv2.imwrite(output_filename, marker_image)
    print(f"Marker ID {marker_id} saved to {output_filename} at {pixel_size}x{pixel_size} pixels.")

# --- Example Usage ---
# Generate a crisp 1000x1000 pixel marker with ID 0
generate_aruco_marker(marker_id=0, pixel_size=1000, output_filename="aruco_marker_id0.png")
import cv2
import numpy as np
import os
from findApril import *
from Detection_and_Tracking import TrackingSystem

# 16.5 cm marker

def calculate_homography(marker_pixel_corners, marker_size_cm):
    world_corners = np.array([
        [0, 0],
        [marker_size_cm, 0],
        [marker_size_cm, marker_size_cm],
        [0, marker_size_cm]
    ], dtype=np.float32)
    
    pixel_corners = np.array(marker_pixel_corners, dtype=np.float32)

    H, _ = cv2.findHomography(pixel_corners, world_corners, cv2.RANSAC)

    return H

def get_2d_localization_homography(object_pixel, H) -> tuple[float, float]:
    obj_pt_array = np.array([[object_pixel]], dtype=np.float32)
    world_pt_array = cv2.perspectiveTransform(obj_pt_array, H)

    X_cm = world_pt_array[0, 0, 0]
    Y_cm = world_pt_array[0, 0, 1]

    return (float(X_cm), float(Y_cm))

if __name__ == "__main__":

    # Initialize tracking system
    system = TrackingSystem()

    frame_folder = "frames"
    frames = sorted(os.listdir(frame_folder))

    f = 0
    for frame_path in frames:
        # Detect reference marker
        markerLocationArray_n = detect_high_accuracy_marker_zero_april('frames\\'+frame_path)
        if markerLocationArray_n is not None:
            markerLocationArray = markerLocationArray_n
            print("Marker Corners:", markerLocationArray)
        else:
            continue
        # Build homography matrix
        H = calculate_homography(markerLocationArray, .165)

        # Run Detection
        frame = system.process_frame("frames\\"+frame_path,f)
        f += 1

    # Access tracked pixel positions
    objectPixelDict = system.timeline
    print("\nTracked Pixel Positions:")
    print(objectPixelDict)

    # Convert tracked pixels to real-world coordinates
    print("\nReal World Coordinates (cm):")
    
    for t in range(len(frames)):
        print(f"\n######## TIMESTEP: {t} #########\n")
        for obj_id in objectPixelDict[t].keys():
            pixel_point = objectPixelDict[t][obj_id]["bottom_middle"]
            world_coords = get_2d_localization_homography(pixel_point, H)
            print(f"{obj_id}: {world_coords}")

        cv2.imwrite("I5.png", frame)
        # cv2.destroyAllWindows()
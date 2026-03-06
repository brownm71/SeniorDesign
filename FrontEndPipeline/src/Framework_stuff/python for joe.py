import torch
import cv2
import numpy as np
from PIL import Image
from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection
import numpy as np
from scipy.optimize import linear_sum_assignment

def compute_iou(boxA, boxB):
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interArea = max(0, xB - xA) * max(0, yB - yA)

    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

    return interArea / float(boxAArea + boxBArea - interArea + 1e-6)

class SimpleTracker:
    def __init__(self, iou_threshold=0.3, max_age=30):
        self.next_id = 0
        self.tracks = {}  # id -> {box, age, velocity}
        self.iou_threshold = iou_threshold
        self.max_age = max_age

    def predict_box(self, box, velocity):
        # Predict next box using last velocity
        return box + velocity

    def update(self, detections):
        updated_tracks = {}
        track_ids = list(self.tracks.keys())
        track_boxes = []
        predicted_boxes = []

        # Prepare predicted boxes
        for tid in track_ids:
            data = self.tracks[tid]
            box = data["box"]
            vel = data.get("velocity", np.array([0,0,0,0]))
            pred_box = self.predict_box(box, vel)
            track_boxes.append(box)
            predicted_boxes.append(pred_box)

        # If we have both tracks and detections, do assignment
        if len(track_boxes) > 0 and len(detections) > 0:
            cost_matrix = np.zeros((len(track_boxes), len(detections)))

            for i, pred_box in enumerate(predicted_boxes):
                for j, det_box in enumerate(detections):
                    cost_matrix[i, j] = 1 - compute_iou(pred_box, det_box)

            row_ind, col_ind = linear_sum_assignment(cost_matrix)

            assigned_dets = set()

            for r, c in zip(row_ind, col_ind):
                if 1 - cost_matrix[r, c] >= self.iou_threshold:
                    tid = track_ids[r]
                    old_box = self.tracks[tid]["box"]
                    # Update velocity: simple difference
                    velocity = detections[c] - old_box
                    updated_tracks[tid] = {
                        "box": detections[c],
                        "age": 0,
                        "velocity": velocity
                    }
                    assigned_dets.add(c)

            # Unmatched detections → new tracks
            for i, det in enumerate(detections):
                if i not in assigned_dets:
                    updated_tracks[self.next_id] = {
                        "box": det,
                        "age": 0,
                        "velocity": np.array([0,0,0,0])
                    }
                    self.next_id += 1

        else:
            # No tracks yet → create new ones
            for det in detections:
                updated_tracks[self.next_id] = {
                    "box": det,
                    "age": 0,
                    "velocity": np.array([0,0,0,0])
                }
                self.next_id += 1

        # Age old tracks
        for tid in self.tracks:
            if tid not in updated_tracks:
                age = self.tracks[tid]["age"] + 1
                if age < self.max_age:
                    # Keep previous velocity
                    updated_tracks[tid] = {
                        "box": self.tracks[tid]["box"],
                        "age": age,
                        "velocity": self.tracks[tid].get("velocity", np.array([0,0,0,0]))
                    }

        self.tracks = updated_tracks
        return self.tracks


# 1. Load DINO
model_id = "IDEA-Research/grounding-dino-base"
processor = AutoProcessor.from_pretrained(model_id)
model = AutoModelForZeroShotObjectDetection.from_pretrained(model_id)

device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

# 2. Initialize tracker
tracker = SimpleTracker(iou_threshold=0.2, max_age=40)

text_prompt = "computer mouse cursor. "

def detect_and_track(image_path):
    print(f"\nProcessing: {image_path}")

    image = Image.open(image_path).convert("RGB")
    inputs = processor(images=image, text=text_prompt, return_tensors="pt").to(device)

    with torch.no_grad():
        outputs = model(**inputs)
    target_sizes = torch.tensor([image.size[::-1]]).to(device)

    results = processor.post_process_grounded_object_detection(
        outputs,
        inputs.input_ids,
        text_threshold=0.3,
        target_sizes=target_sizes
    )

    results = results[0]

    boxes = results["boxes"].cpu().numpy()
    scores = results['scores']

    print(scores)

    tracks = tracker.update(boxes)

    cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    for track_id, data in tracks.items():
        box = data["box"]
        x1, y1, x2, y2 = box.astype(int)

        # Compute center point
        cx = int((x1 + x2) / 2)
        cy = int((y1 + y2) / 2)

        # ---- PRINT LOCATION + ID ----
        print(f"ID {track_id} | "
              f"Box: ({x1}, {y1}, {x2}, {y2}) | "
              f"Center: ({cx}, {cy})")

        # Draw rectangle
        cv2.rectangle(cv_image, (x1, y1), (x2, y2), (0,255,0), 2)

        # Draw ID
        cv2.putText(cv_image, f"ID {track_id}", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

        # Draw center dot
        cv2.circle(cv_image, (cx, cy), 4, (0,0,255), -1)

    cv2.imshow("Tracked", cv_image)
    cv2.waitKey(1)

    print("Frame Done")

# 3. Run on All Frames
import os

frame_folder = "frames"
frames = sorted(os.listdir(frame_folder))

for frame_name in frames:
    detect_and_track(os.path.join(frame_folder, frame_name))

cv2.destroyAllWindows()
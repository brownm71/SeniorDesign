import torch
import cv2
import numpy as np
from PIL import Image
from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection
from scipy.optimize import linear_sum_assignment
import os

# -----------------------------
# Utility Functions
# -----------------------------

def compute_iou(boxA, boxB):
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interArea = max(0, xB - xA) * max(0, yB - yA)

    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

    return interArea / float(boxAArea + boxBArea - interArea + 1e-6)


def get_object_location(box):
    x1, y1, x2, y2 = box.astype(int)
    return (x1, y1, x2, y2)


def get_bottom_middle(box):
    x1, y1, x2, y2 = box.astype(int)
    x_mid = int((x1 + x2) / 2)
    y_bottom = int(y2)
    return (x_mid, y_bottom)


# -----------------------------
# Tracker
# -----------------------------

class SimpleTracker:
    def __init__(self, iou_threshold=0.3, max_age=30):
        self.next_id = 0
        self.tracks = {}
        self.iou_threshold = iou_threshold
        self.max_age = max_age

    def predict_box(self, box, velocity):
        return box + velocity

    def update(self, detections):

        updated_tracks = {}
        track_ids = list(self.tracks.keys())
        track_boxes = []
        predicted_boxes = []

        for tid in track_ids:
            data = self.tracks[tid]
            box = data["box"]
            vel = data.get("velocity", np.array([0,0,0,0]))
            pred_box = self.predict_box(box, vel)

            track_boxes.append(box)
            predicted_boxes.append(pred_box)

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

                    velocity = detections[c] - old_box

                    updated_tracks[tid] = {
                        "box": detections[c],
                        "age": 0,
                        "velocity": velocity
                    }

                    assigned_dets.add(c)

            for i, det in enumerate(detections):

                if i not in assigned_dets:

                    updated_tracks[self.next_id] = {
                        "box": det,
                        "age": 0,
                        "velocity": np.array([0,0,0,0])
                    }

                    self.next_id += 1

        else:

            for det in detections:

                updated_tracks[self.next_id] = {
                    "box": det,
                    "age": 0,
                    "velocity": np.array([0,0,0,0])
                }

                self.next_id += 1

        for tid in self.tracks:

            if tid not in updated_tracks:

                age = self.tracks[tid]["age"] + 1

                if age < self.max_age:

                    updated_tracks[tid] = {
                        "box": self.tracks[tid]["box"],
                        "age": age,
                        "velocity": self.tracks[tid].get("velocity", np.array([0,0,0,0]))
                    }

        self.tracks = updated_tracks

        return self.tracks


# -----------------------------
# Load DINO Model
# -----------------------------

model_id = "IDEA-Research/grounding-dino-base"

processor = AutoProcessor.from_pretrained(model_id)
model = AutoModelForZeroShotObjectDetection.from_pretrained(model_id)

device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

# -----------------------------
# Initialize Tracker
# -----------------------------

tracker = SimpleTracker(iou_threshold=0.2, max_age=40)

text_prompt = "computer mouse cursor. "

# -----------------------------
# Timeline Dictionary
# -----------------------------

timeline = {}

# -----------------------------
# Detection + Tracking Function
# -----------------------------

def detect_and_track(image_path, timestep):

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
    )[0]

    boxes = results["boxes"].cpu().numpy()

    tracks = tracker.update(boxes)

    cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    timeline[timestep] = {}

    for track_id, data in tracks.items():

        box = data["box"]

        loc = get_object_location(box)
        bottom = get_bottom_middle(box)

        timeline[timestep][track_id] = {
            "box": loc,
            "bottom_middle": bottom
        }

        x1, y1, x2, y2 = loc
        bx, by = bottom

        print(f"t={timestep} | ID {track_id} | Box {loc} | Bottom {bottom}")

        cv2.rectangle(cv_image, (x1, y1), (x2, y2), (0,255,0), 2)

        cv2.putText(
            cv_image,
            f"ID {track_id}",
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0,255,0),
            2
        )

        cv2.circle(cv_image, (bx, by), 4, (255,0,0), -1)

    cv2.imshow("Tracked", cv_image)
    cv2.waitKey(1)

    print("Frame Done")


# -----------------------------
# Run Over Frames
# -----------------------------

frame_folder = "frames"
frames = sorted(os.listdir(frame_folder))

for t, frame_name in enumerate(frames):

    detect_and_track(os.path.join(frame_folder, frame_name), t)

cv2.destroyAllWindows()


# -----------------------------
# Example Access
# -----------------------------

print("\nTimeline Example:")
print(timeline)
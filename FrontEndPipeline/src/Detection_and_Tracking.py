import torch
import cv2
import numpy as np
from PIL import Image
from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection
import os
from scipy.optimize import linear_sum_assignment
import multiprocessing

class Tracker:
    def __init__(self, iou_threshold=0.3, max_age=30, smooth_factor=0.7, max_dist=150, alpha=0.5):
        """
        Initializes the Tracker with parameters for matching and state estimation.

        Args:
            iou_threshold (float): Threshold for Intersection over Union (IoU) to consider a match valid.
            max_age (int): Maximum number of frames to keep a track alive without new detections.
            smooth_factor (float): Factor for exponential smoothing of bounding box position (0 to 1).
            max_dist (float): Maximum pixel distance allowed between predicted and detected centers for matching.
            alpha (float): Weighting factor for combining IOU and color similarity (0=only IOU, 1=only color).
        """
        self.next_id = 0
        self.tracks = {}
        self.iou_threshold = iou_threshold
        self.max_age = max_age
        self.smooth_factor = smooth_factor
        self.max_dist = max_dist
        self.alpha = alpha  # appearance weight

    @staticmethod
    def center(box):
        """
        Calculates the center coordinates of a bounding box.
        Args:
            box (tuple or np.array): Bounding box coordinates [x1, y1, x2, y2].
        Returns:
            np.array: A numpy array containing the center [x_center, y_center].
        """
        x1, y1, x2, y2 = box
        return np.array([(x1 + x2)/2, (y1 + y2)/2])

    @staticmethod
    def compute_iou(boxA, boxB):
        """
        Computes the Intersection over Union (IoU) between two bounding boxes.
        Args:
            boxA (tuple or np.array): First bounding box [x1, y1, x2, y2].
            boxB (tuple or np.array): Second bounding box [x1, y1, x2, y2].
        Returns:
            float: The IoU value ranging from 0.0 to 1.0.
        """
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])
        interW = max(0, xB - xA)
        interH = max(0, yB - yA)
        interArea = interW * interH
        boxAArea = (boxA[2]-boxA[0])*(boxA[3]-boxA[1])
        boxBArea = (boxB[2]-boxB[0])*(boxB[3]-boxB[1])
        union = boxAArea + boxBArea - interArea
        if union == 0:
            return 0
        return interArea / union

    @staticmethod
    def bottom_middle(box):
        """
        Calculates the bottom-middle point of a bounding box, typically used for ground plane projection.
        Args:
            box (tuple or np.array): Bounding box coordinates [x1, y1, x2, y2].
        Returns:
            tuple: A tuple (x_mid, y_bottom) representing the bottom-middle pixel coordinates.
        """
        x1, y1, x2, y2 = box
        x_mid = int((x1 + x2)/2)
        y_bottom = int(y2)
        return (x_mid, y_bottom)

    @staticmethod
    def color_hist(frame, box, bins=(8,8,8)):
        """
        Returns a normalized 3D color histogram for the cropped box.
        Args:
            frame (np.array): The image frame (BGR).
            box (tuple or np.array): Bounding box coordinates [x1, y1, x2, y2].
            bins (tuple): Number of bins for each color channel (B, G, R).
        Returns:
            np.array: A flattened, normalized histogram array. Returns zeros if the crop is empty.
        """
        x1, y1, x2, y2 = map(int, box)
        crop = frame[y1:y2, x1:x2]
        if crop.size == 0:
            return np.zeros(bins[0]*bins[1]*bins[2])
        hist = cv2.calcHist([crop], [0,1,2], None, bins, [0,256,0,256,0,256])
        hist = cv2.normalize(hist, hist).flatten()
        return hist

    @staticmethod
    def hist_similarity(hist1, hist2):
        """
        Returns a similarity measure in [0,1] using correlation.
        Args:
            hist1 (np.array): First histogram.
            hist2 (np.array): Second histogram.
        Returns:
            float: Similarity score between 0.0 and 1.0.
        """
        if hist1 is None or hist2 is None or len(hist1)==0 or len(hist2)==0:
            return 0
        return cv2.compareHist(hist1.astype('float32'), hist2.astype('float32'), cv2.HISTCMP_CORREL)

    def predict_box(self, box, velocity):
        cx, cy = self.center(box)
        new_center = np.array([cx, cy]) + velocity
        w = box[2] - box[0]
        h = box[3] - box[1]
        x1 = new_center[0] - w/2
        y1 = new_center[1] - h/2
        x2 = new_center[0] + w/2
        y2 = new_center[1] + h/2
        return np.array([x1, y1, x2, y2])

    def update(self, detections, scores=None, frame=None):
        """
        Updates the state of the tracker with new detections from the current frame.
        Args:
            detections (list): List of detected bounding boxes (np.array([x1, y1, x2, y2])).
            scores (list, optional): Confidence scores for the detections. Defaults to None.
            frame (np.array, optional): The current image frame, used for appearance feature extraction. Defaults to None.
        Returns:
            dict: A dictionary of active tracks, formatted as {track_id: {"box": box, "score": score}}.
        """
        updated_tracks = {}
        track_ids = list(self.tracks.keys())
        predicted_boxes = []

        # Predict positions of existing tracks
        for tid in track_ids:
            data = self.tracks[tid]
            box = data["box"]
            vel = data.get("velocity", np.array([0,0]))
            pred_box = self.predict_box(box, vel)
            predicted_boxes.append(pred_box)

        # Compute color histograms for detections
        det_hists = []
        for det_box in detections:
            hist = self.color_hist(frame, det_box) if frame is not None else None
            det_hists.append(hist)

        if len(predicted_boxes) > 0 and len(detections) > 0:
            cost_matrix = np.zeros((len(predicted_boxes), len(detections)))

            for i, tid in enumerate(track_ids):
                pred_box = predicted_boxes[i]
                pred_center = self.center(pred_box)
                track_hist = self.tracks[tid].get("hist", None)
                for j, det_box in enumerate(detections):
                    det_center = self.center(det_box)
                    dist = np.linalg.norm(pred_center - det_center)
                    if dist > self.max_dist:
                        cost_matrix[i,j] = 1e6
                        continue
                    iou_cost = 1 - self.compute_iou(pred_box, det_box)
                    if track_hist is not None and det_hists[j] is not None:
                        color_sim = self.hist_similarity(track_hist, det_hists[j])
                        color_cost = 1 - color_sim
                    else:
                        color_cost = 0
                    # Combined cost: IOU + alpha*color
                    cost_matrix[i,j] = (1 - self.alpha)*iou_cost + self.alpha*color_cost

            row_ind, col_ind = linear_sum_assignment(cost_matrix)
            assigned_dets = set()

            # Update matched tracks
            for r, c in zip(row_ind, col_ind):
                if cost_matrix[r,c] < (1 - self.iou_threshold):
                    tid = track_ids[r]
                    old_box = self.tracks[tid]["box"]
                    old_center = self.center(old_box)
                    new_center = self.center(detections[c])
                    velocity = new_center - old_center
                    smoothed_box = self.smooth_factor*detections[c] + (1-self.smooth_factor)*old_box

                    updated_tracks[tid] = {
                        "box": smoothed_box,
                        "age": 0,
                        "velocity": velocity,
                        "hist": det_hists[c],
                        "score": scores[c] if scores is not None else None
                    }
                    assigned_dets.add(c)

            # Add unmatched detections as new tracks
            for i, det in enumerate(detections):
                if i not in assigned_dets:
                    updated_tracks[self.next_id] = {
                        "box": det,
                        "age": 0,
                        "velocity": np.array([0,0]),
                        "hist": det_hists[i],
                        "score": scores[i] if scores is not None else None
                    }
                    self.next_id += 1
        else:
            # No existing tracks, initialize
            for i, det in enumerate(detections):
                updated_tracks[self.next_id] = {
                    "box": det,
                    "age": 0,
                    "velocity": np.array([0,0]),
                    "hist": det_hists[i]
                }
                self.next_id += 1

        # Age unmatched tracks
        for tid in self.tracks:
            if tid not in updated_tracks:
                age = self.tracks[tid]["age"] + 1
                if age < self.max_age:
                    box = self.tracks[tid]["box"]
                    vel = self.tracks[tid].get("velocity", np.array([0,0]))
                    pred_box = self.predict_box(box, vel)
                    updated_tracks[tid] = {
                        "box": pred_box,
                        "age": age,
                        "velocity": vel,
                        "hist": self.tracks[tid].get("hist", None)
                    }

        self.tracks = updated_tracks
        return {tid: {"box": data["box"], "score": data.get("score", None)}
            for tid, data in self.tracks.items()}

class Detector:
    def __init__(self):
        """
        Initializes the Object Detector using the Grounding DINO model.
        Loads the model and processor, and moves execution to GPU if available.
        """
        model_id = "IDEA-Research/grounding-dino-base"
        self.processor = AutoProcessor.from_pretrained(model_id)
        self.model = AutoModelForZeroShotObjectDetection.from_pretrained(model_id)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        self.prompt = "person ."

    def detect(self, image):
        """
        Performs zero-shot object detection on the provided image.
        Args:
            image (PIL.Image): The input image.
        Returns:
            tuple: A tuple containing:
                - boxes (np.array): Array of bounding boxes [x1, y1, x2, y2].
                - scores (np.array): Array of confidence scores for each detection.
        """
        inputs = self.processor(
            images=image,
            text=self.prompt,
            return_tensors="pt"
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)

        target_sizes = torch.tensor([image.size[::-1]]).to(self.device)
        results = self.processor.post_process_grounded_object_detection(
            outputs,
            inputs.input_ids,
            text_threshold=0.3,
            target_sizes=target_sizes
        )[0]

        boxes = results["boxes"].cpu().numpy()
        scores = results["scores"].cpu().numpy()
        # Filter low-confidence
        mask = scores > 0.45
        boxes = boxes[mask]
        return boxes, scores[mask]

class TrackingSystem:
    def __init__(self):
        """
        Initializes the complete Tracking System, including the Detector and Tracker modules,
        and sets up a timeline to store tracking results.
        """
        self.detector = Detector()
        self.tracker = Tracker()
        self.timeline = {}

    def process_frame(self, frame_path, timestep):
        """
        Processes a single video frame: detects objects, updates tracks, visualizes results,
        and records the state in the timeline.
        Args:
            frame_path (str): File path to the image frame.
            timestep (int/float): The time index associated with this frame.
        Returns:
            np.array: The processed frame with visualizations drawn on it (BGR format).
        """
        print(f"\nProcessing: {frame_path}")
        image = Image.open(frame_path).convert("RGB")
        frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        boxes, scores = self.detector.detect(image)
        tracks = self.tracker.update(boxes, scores=scores, frame=frame)

        self.timeline[timestep] = {}
        for track_id, data in tracks.items():
            box = data["box"]
            score = data["score"]

            x1, y1, x2, y2 = map(int, box)
            bottom = self.tracker.bottom_middle(box)
            self.timeline[timestep][track_id] = {
                "box": (x1, y1, x2, y2),
                "bottom_middle": bottom
            }
            cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0), 2)
            label = f"ID {track_id}"
            if score is not None:
                label += f" {score:.2f}"

            cv2.putText(frame, label, (x1, y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
            cv2.circle(frame, bottom, 4, (255,0,0), -1)

        cv2.imshow("Tracked", frame)
        cv2.waitKey(1)
        return frame

# --------------------------------
# Main Execution
# --------------------------------

# Global worker variables and functions for multiprocessing (must be top-level for pickling)
_worker_detector = None

def _init_detector_pool():
    """Initializes the Detector once per worker process."""
    global _worker_detector
    _worker_detector = Detector()

def _worker_detect(frame_path):
    """Worker task: Load image and perform AI detection."""
    image = Image.open(frame_path).convert("RGB")
    return _worker_detector.detect(image)

class multi_proccessor:
    def __init__(self, num_processes=None):
        """
        Initializes the Multi-Processor Tracking System.
        Parallelizes the detection phase (AI bottleneck) and runs tracking sequentially.
        
        Args:
            num_processes (int, optional): Number of parallel processes. 
                                         Defaults to CPU count. Note: Each process 
                                         loads its own model instance.
        """
        self.tracker = Tracker()
        self.timeline = {}
        self.num_processes = num_processes if num_processes else (os.cpu_count() or 1)

    def process_video(self, frame_folder):
        """
        Batch processes a folder of frames by parallelizing detection and then tracking.
        
        Args:
            frame_folder (str): Path to folder containing frames.
        """
        frame_names = sorted(os.listdir(frame_folder))
        frame_paths = [os.path.join(frame_folder, f) for f in frame_names]

        print(f"Starting parallel detection on {self.num_processes} processes...")
        
        # Step 1: Parallel Detection (AI inference is the bottleneck)
        # 'spawn' is used for thread-safety with CUDA and Windows compatibility
        ctx = multiprocessing.get_context('spawn')
        with ctx.Pool(processes=self.num_processes, initializer=_init_detector_pool) as pool:
            detection_results = pool.map(_worker_detect, frame_paths)

        print("Detection complete. Starting sequential tracking...")

        # Step 2: Sequential Tracking (Tracking depends on temporal state)
        for t, (frame_path, (boxes, scores)) in enumerate(zip(frame_paths, detection_results)):
            image = Image.open(frame_path).convert("RGB")
            frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            # Process tracking with pre-computed boxes/scores
            tracks = self.tracker.update(boxes, scores=scores, frame=frame)

            self.timeline[t] = {}
            for track_id, data in tracks.items():
                box = data["box"]
                score = data["score"]
                x1, y1, x2, y2 = map(int, box)
                bottom = self.tracker.bottom_middle(box)
                self.timeline[t][track_id] = {
                    "box": (x1, y1, x2, y2),
                    "bottom_middle": bottom
                }
                
                # Draw visualizations (mimicking sequential TrackingSystem)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                label = f"ID {track_id}"
                if score is not None:
                    label += f" {score:.2f}"
                cv2.putText(frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                cv2.circle(frame, bottom, 4, (255, 0, 0), -1)

            cv2.imshow("Multi-Processor Tracking", frame)
            cv2.waitKey(1)
            
            if t == len(frame_paths) - 1:
                cv2.imwrite("tracked_output_multi.png", frame)

        cv2.destroyAllWindows()
        return self.timeline

if __name__ == "__main__":
    import time
    # Initialize the multi-processor system
    # Suggestion: Use 2-4 processes to avoid exhausting GPU memory (VRAM)
    system = multi_proccessor(num_processes=2) 
    frame_folder = "frames"
    
    start_time = time.time()
    timeline = system.process_video(frame_folder)
    end_time = time.time()
    
    print(f"\nTotal Processing Time: {end_time - start_time:.2f}s")
    print("\nTimeline Example:")
    print(timeline)
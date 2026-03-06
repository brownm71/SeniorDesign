import torch
import cv2
from PIL import Image
from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection
import numpy as np

# 1. Load the Processor and the DINO Model
# This will download the model weights the first time you run it.
model_id = "IDEA-Research/grounding-dino-base"
processor = AutoProcessor.from_pretrained(model_id)
model = AutoModelForZeroShotObjectDetection.from_pretrained(model_id)

# Move model to GPU if available for faster offline processing
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

def detect_players_dino(image_path):
    # 2. Load image using PIL (Transformers standard)
    image = Image.open(image_path).convert("RGB")

    # 3. Define your text prompt
    # Grounding DINO requires periods after each concept
    text_prompt = "sports player ."

    # 4. Preprocess the inputs
    inputs = processor(images=image, text=text_prompt, return_tensors="pt").to(device)

    # 5. Run High-Accuracy Inference
    with torch.no_grad():
        outputs = model(**inputs)

    # 6. Post-process the outputs to get standard bounding boxes
    # box_threshold: How strict the model should be about the box placement
    # text_threshold: How strict the model should be that the object matches the text
    target_sizes = [image.size[::-1]] # (height, width)
    results = processor.post_process_grounded_object_detection(
        outputs,
        inputs.input_ids,
        # box_threshold=0.35, 
        text_threshold=0.3,
        target_sizes=target_sizes
    )[0]

    # 7. Draw the boxes using OpenCV
    cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    import random
    for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
        # Extract coordinates
        xmin, ymin, xmax, ymax = [int(i) for i in box.tolist()]
        
        # Draw the bounding box
        rgb = (random.randrange(0,255), random.randrange(0,255), random.randrange(0,255))
        cv2.rectangle(cv_image, (xmin, ymin), (xmax, ymax), rgb, 2)
        
        # Add label and confidence score
        label_text = f"{label}: {round(score.item(), 2)}"
        cv2.putText(cv_image, label_text, (xmin, ymin - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, rgb, 2)

    # Display the result
    cv2.imshow("DINO High-Accuracy Detection", cv_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Run the function on a test frame
# (You can extract a single frame from your video to test this first)
detect_players_dino(r"SeniorDesign\FrontEndPipeline\src\test2.jpg")
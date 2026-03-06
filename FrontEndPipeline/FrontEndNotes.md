# Building the Front End
## Flow
Data source (Video Assumed for automation) -> Split into Images -> Estimate Scale (For each frame) -> Object Detection -> Player Matching -> Into our library
### Data Source
Inject a known into the situation. Thinking QR code or other tracking marker.
### Object Detection
Considering use of DINO transformer model based object detection. Cascade-RCNN is the previous cutting edge using convolution neural networking for object detection. Gemini reported better performance from DINO. Can consider absolute cutting edge with current research in Cascade-DINO where multiple passes and image processing is input to the transformer model. Better at partial person detection through obstruction and bounding box accuracy.
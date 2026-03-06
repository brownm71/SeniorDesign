import os
import subprocess
from pathlib import Path
ffmpeg_path = r"C:\Users\crimj\OneDrive\Documents\ffmpeg-7.0.2-full_build\ffmpeg-7.0.2-full_build\bin\ffmpeg.exe"
def extract_frames_at_timesteps(video_path, timesteps, output_dir="frames", 
                                filename_prefix="frame", image_format="png"):
    """
    Extract frames from a video at specific timesteps using ffmpeg.

    Parameters:
        video_path (str): Path to input video file.
        timesteps (list of float): List of timestamps in seconds.
        output_dir (str): Directory to save extracted frames.
        filename_prefix (str): Prefix for output frame filenames.
        image_format (str): Image format (e.g., 'png', 'jpg').

    Example:
        extract_frames_at_timesteps("video.mp4", [0.5, 1.2, 3.7])
    """

    video_path = Path(video_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    for i, timestamp in enumerate(timesteps):
        output_file = output_dir / f"{filename_prefix}_{i:04d}.{image_format}"

        command = [
            ffmpeg_path,
            "-y",                     # overwrite output files
            "-ss", str(timestamp),    # seek to timestamp
            "-i", str(video_path),
            "-frames:v", "1",         # extract one frame
            "-q:v", "2",              # quality (for jpg)
            str(output_file)
        ]

        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"FFmpeg failed at timestamp {timestamp}:\n{result.stderr.decode()}"
            )

    print(f"Extracted {len(timesteps)} frames to '{output_dir}'")

e = extract_frames_at_timesteps(r"2026-03-02 19-55-35.mp4",[0,.5,1,1.5,2,2.5,3,3.5,5,5.5,6])
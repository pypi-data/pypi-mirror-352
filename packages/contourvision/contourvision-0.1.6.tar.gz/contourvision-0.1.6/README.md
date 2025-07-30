ContourVision: Video Contour Extraction Tool
ContourVision is a Python library designed for extracting and visualizing contours from video files. It allows users to process videos and obtain an output where object outlines are highlighted.

Features
Converts video frames to grayscale.

Applies Otsu's method for automatic thresholding.

Finds external contours of objects in frames.

Outputs video with:

White contours on a black background.

Black contours on a white background.

Simple and easy-to-use class interface.

(Future) Draw contours directly on the original color frames.

Installation
You can install ContourVision using pip.

From PyPI (Once Published)
pip install contourvision

From Source (for development)
Clone the repository:

git clone [https://github.com/viliusbankauskas/contourvision.git](https://github.com/viliusbankauskas/contourvision.git) 

cd contourvision

Install in editable mode:

pip install -e .

Dependencies
Python 3.8+

OpenCV (opencv-python >= 4.0)

NumPy (numpy >= 1.19)

These dependencies will be automatically installed if you install ContourVision via pip (as they are listed in setup.py).

Usage Example
Create a Python script (e.g., process_my_video.py):

from contourvision import VideoContourExtractor
import os

# Define paths for your input video and desired output
    input_video_file = "path/to/your/video.mp4" # REQUIRED: Change this to your video file
    output_dir = "processed_videos" # A directory to store output videos
    os.makedirs(output_dir, exist_ok=True) # Create the output directory if it doesn't exist

    output_video_wb = os.path.join(output_dir, "result_white_on_black.avi")
    output_video_bw = os.path.join(output_dir, "result_black_on_white.avi")

    if not os.path.exists(input_video_file):
        print(f"Error: Input video '{input_video_file}' not found.")
    else:
        try:
            # Initialize the extractor for white contours on a black background
            print(f"Processing for white on black: {input_video_file} -> {output_video_wb}")
            extractor_wb = VideoContourExtractor(contour_style='white_on_black')
            extractor_wb.process_video(input_video_file, output_video_wb)
            print(f"White on black processing finished. Output: {output_video_wb}")

            # Initialize the extractor for black contours on a white background
            print(f"Processing for black on white: {input_video_file} -> {output_video_bw}")
            extractor_bw = VideoContourExtractor(contour_style='black_on_white')
            extractor_bw.process_video(input_video_file, output_video_bw)
            print(f"Black on white processing finished. Output: {output_video_bw}")

            print(f"\nAll processing done. Check outputs in '{output_dir}'.")

        except Exception as e:
            print(f"An error occurred during processing: {e}")
            import traceback
            traceback.print_exc()

Remember to replace "path/to/your/video.mp4" with the actual path to your video file.

How to Run the Included Example
The project includes an example script to demonstrate its usage.

Locate a test video: Ensure you have a video file (e.g., .mp4, .avi) for testing. You can place it in the examples/input_videos/ directory for convenience, or note its absolute path.

Configure the example script:

Open examples/run_contour_detection.py.

Find the line input_path = "examples/input_videos/test.mp4" 

Change this string to the correct path of your test video file.

Navigate to the project root: Open your terminal or command prompt and navigate to the main directory of the ContourVision project (the one containing setup.py and the examples folder).

Run the script:

python examples/run_contour_detection.py

Output videos will be saved in the examples/output_videos/ directory by default.

Future Enhancements
Draw on Original Frame: Implement the on_original contour style to draw contours directly on the original color video frames.

More Thresholding Methods: Add support for other thresholding techniques beyond Otsu's method.

Contour Customization: Allow users to configure contour thickness, color (for on_original), and type (e.g., cv2.RETR_LIST, cv2.RETR_TREE).

Command-Line Interface (CLI): Develop a CLI using argparse or click for easier use without writing Python scripts.

Performance Optimization: Investigate potential performance improvements for processing long videos.

Error Handling: Enhance error handling and provide more informative messages.

Unit Tests: Write comprehensive unit tests for all functionalities.

Documentation: Expand documentation, possibly using tools like Sphinx or MkDocs for a dedicated documentation site.

Output Formats: Allow specifying different output video codecs and containers.

License
This project is licensed under the MIT License. Please see the LICENSE file in the repository for the full license text.

Contributing
Contributions are welcome!
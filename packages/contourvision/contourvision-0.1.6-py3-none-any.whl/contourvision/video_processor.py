import cv2
import numpy as np
import os

class VideoContourExtractor:
    """
    A class for extracting contours from video frames.
    """

    def __init__(self, threshold_type='otsu', contour_style='white_on_black'):
        """
        Initializes the VideoContourExtractor.

        Args:
            threshold_type (str): The thresholding method to use. Currently supports 'otsu'.
            contour_style (str): The style of the output contours.
                                 'white_on_black' - white contours on a black background.
                                 'black_on_white' - black contours on a white background.
                                 'on_original' - contours drawn on the original color frame (to be implemented).
        """
        if not isinstance(threshold_type, str) or threshold_type.lower() not in ['otsu']:
            raise ValueError("Unsupported 'threshold_type'. Supported value: 'otsu'.")
        
        supported_styles = ['white_on_black', 'black_on_white'] # 'on_original' will be added later
        if not isinstance(contour_style, str) or contour_style.lower() not in supported_styles:
            raise ValueError(f"Unsupported 'contour_style'. Supported values: {', '.join(supported_styles)}.")
        
        self.threshold_type = threshold_type.lower()
        self.contour_style = contour_style.lower()
        print(f"VideoContourExtractor initialized: threshold='{self.threshold_type}', style='{self.contour_style}'")

    def process_video(self, input_video_path: str, output_video_path: str):
        """
        Reads a video, finds contours in each frame according to the settings,
        and writes the result to a new video file.

        Args:
            input_video_path (str): Path to the input video file.
            output_video_path (str): Path where the processed video file will be saved.

        Raises:
            FileNotFoundError: If the input video file is not found.
            Exception: For other errors during video processing.
        """
        if not os.path.exists(input_video_path):
            raise FileNotFoundError(f"Error: Input video file not found at: {input_video_path}")

        try:
            cap = cv2.VideoCapture(input_video_path)
            if not cap.isOpened():
                print(f"Error: Could not open video file: {input_video_path}")
                return

            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            # Use 'XVID' codec for AVI format. Can be changed if needed.
            # isColor=False for black and white output, True if drawing on original.
            is_color_output = self.contour_style == 'on_original' # This will be False for now
            
            # Ensure the output directory exists
            output_dir = os.path.dirname(output_video_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                print(f"Created output directory: {output_dir}")

            fourcc = cv2.VideoWriter_fourcc(*'XVID') # Common codec for .avi
            # fourcc = cv2.VideoWriter_fourcc(*'MP4V') # For .mp4, might need ffmpeg
            out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height), isColor=is_color_output)

            print(f"Starting video processing: '{input_video_path}' -> '{output_video_path}'")
            frame_count = 0
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            print(f"Total frames to process: {total_frames if total_frames > 0 else 'N/A'}")

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break 

                processed_frame = self._process_frame(frame)
                out.write(processed_frame)
                frame_count += 1
                if frame_count % 100 == 0 and total_frames > 0: # Print progress every 100 frames
                    progress = (frame_count / total_frames) * 100
                    print(f"Processed frames: {frame_count}/{total_frames} ({progress:.2f}%)")
                elif frame_count % 100 == 0:
                    print(f"Processed frames: {frame_count}")


            cap.release()
            out.release()
            print(f"Video processing finished. Processed {frame_count} frames. Result saved to: {output_video_path}")

        except Exception as e:
            # Release resources in case of an error
            if 'cap' in locals() and cap.isOpened():
                cap.release()
            if 'out' in locals() and out.isOpened(): # Check if out was successfully initialized
                out.release()
            print(f"An error occurred during video processing: {e}")
            raise 

    def _process_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Processes a single video frame: converts to grayscale,
        applies thresholding, and finds contours.

        Args:
            frame (np.ndarray): The input frame (BGR format).

        Returns:
            np.ndarray: The processed frame with contours.
                        (single-channel, black and white, or 3-channel if 'on_original').
        """
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Thresholding
        if self.threshold_type == 'otsu':
            # THRESH_BINARY_INV gives white objects on a black background, good for contour finding.
            # THRESH_BINARY gives black objects on a white background.
            if self.contour_style == 'white_on_black':
                 thresh_mode = cv2.THRESH_BINARY_INV 
            elif self.contour_style == 'black_on_white':
                 thresh_mode = cv2.THRESH_BINARY
            else: # Default or for 'on_original' if we need binary image first
                 thresh_mode = cv2.THRESH_BINARY_INV
            
            _, binary_image = cv2.threshold(gray_frame, 0, 255, thresh_mode + cv2.THRESH_OTSU)
        else:
            # Fallback or placeholder for other threshold types
            # Currently, __init__ ensures only 'otsu' is used.
            binary_image = gray_frame # This should not be reached with current validation

        # Contour finding
        # cv2.RETR_EXTERNAL finds only external contours
        # cv2.CHAIN_APPROX_SIMPLE compresses contour segments
        contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Contour drawing
        frame_height, frame_width = frame.shape[:2]
        
        if self.contour_style == 'white_on_black':
            # Draw white contours on a black background
            output_contour_frame = np.zeros((frame_height, frame_width), dtype=np.uint8) # Black background
            cv2.drawContours(output_contour_frame, contours, -1, (255), 1) # (255) is white
        elif self.contour_style == 'black_on_white':
            # Draw black contours on a white background
            output_contour_frame = np.full((frame_height, frame_width), 255, dtype=np.uint8) # White background
            cv2.drawContours(output_contour_frame, contours, -1, (0), 1) # (0) is black
        # elif self.contour_style == 'on_original':
            # To be implemented: draw contours on the original color frame
            # output_contour_frame = frame.copy()
            # cv2.drawContours(output_contour_frame, contours, -1, (0, 255, 0), 1) # e.g., green contours
            # return output_contour_frame 
        else:
            # Should not happen due to __init__ validation
            output_contour_frame = np.zeros((frame_height, frame_width), dtype=np.uint8)


        return output_contour_frame
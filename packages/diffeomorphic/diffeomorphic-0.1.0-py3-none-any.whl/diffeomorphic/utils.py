"""
Utility functions for the diffeomorphic package.
"""
import os
import numpy as np
import logging
from PIL import Image
import cv2

logger = logging.getLogger(__name__)

def ensure_directory(directory):
    """
    Ensure the directory exists, create it if it doesn't.
    
    Parameters:
    -----------
    directory : str
        Path to the directory
        
    Returns:
    --------
    str
        Path to the directory
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Created directory: {directory}")
    return directory

def load_image(image_path):
    """
    Load an image from file and normalize.
    
    Parameters:
    -----------
    image_path : str
        Path to the image file
        
    Returns:
    --------
    tuple
        (image_array, image_size) where image_array is a numpy array and 
        image_size is a tuple of (height, width)
    """
    try:
        img = Image.open(image_path)
        img_array = np.array(img)
        
        # Ensure RGB format
        if len(img_array.shape) == 2:
            # Convert grayscale to RGB
            img_array = np.stack([img_array, img_array, img_array], axis=2)
        elif len(img_array.shape) == 3 and img_array.shape[2] > 3:
            # Take only RGB channels
            img_array = img_array[:, :, :3]
            
        return img_array, img_array.shape[:2]
    except Exception as e:
        logger.error(f"Error loading image {image_path}: {e}")
        return None, None

def extract_frames(video_path, output_dir=None, max_frames=None):
    """
    Extract frames from a video file.
    
    Parameters:
    -----------
    video_path : str
        Path to the video file
    output_dir : str, optional
        Directory to save extracted frames. If None, frames are not saved.
    max_frames : int, optional
        Maximum number of frames to extract. If None, extract all frames.
        
    Returns:
    --------
    list
        List of numpy arrays containing frames
    """
    frames = []
    
    try:
        # Open the video file
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error(f"Error opening video file {video_path}")
            return frames
        
        # Get video properties
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration = frame_count / fps if fps > 0 else 0
        
        logger.info(f"Video: {frame_count} frames, {fps:.2f} fps, {duration:.2f} seconds")
        
        # Limit frames if requested
        if max_frames is not None and max_frames > 0:
            frame_count = min(frame_count, max_frames)
        
        # Create output directory if needed
        if output_dir is not None:
            ensure_directory(output_dir)
        
        # Extract frames
        frame_idx = 0
        while frame_idx < frame_count:
            ret, frame = cap.read()
            if not ret:
                break
                
            # Convert from BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(frame_rgb)
            
            # Save frame if needed
            if output_dir is not None:
                frame_path = os.path.join(output_dir, f"frame_{frame_idx:04d}.png")
                cv2.imwrite(frame_path, frame)
                
            frame_idx += 1
            
        # Release the video capture
        cap.release()
        
        logger.info(f"Extracted {len(frames)} frames from {video_path}")
    except Exception as e:
        logger.error(f"Error extracting frames from {video_path}: {e}")
    
    return frames

def create_video_from_frames(frames, output_path, fps=30, codec='mp4v'):
    """
    Create a video from a list of frames.
    
    Parameters:
    -----------
    frames : list
        List of numpy arrays containing frames
    output_path : str
        Path to save the output video
    fps : int, optional
        Frames per second, default is 30
    codec : str, optional
        Codec to use, default is 'mp4v'
        
    Returns:
    --------
    str
        Path to the output video if successful, None otherwise
    """
    if not frames:
        logger.error("No frames provided to create video")
        return None
    
    try:
        # Get frame dimensions
        height, width = frames[0].shape[:2]
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*codec)
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        # Write frames
        for frame in frames:
            # Convert from RGB to BGR
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            out.write(frame_bgr)
        
        # Release the video writer
        out.release()
        
        logger.info(f"Created video: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Error creating video {output_path}: {e}")
        return None

def pad_image(image, target_size):
    """
    Pad an image to the target size by centering it.
    
    Parameters:
    -----------
    image : numpy.ndarray
        Input image array
    target_size : tuple
        Target size (height, width)
        
    Returns:
    --------
    numpy.ndarray
        Padded image
    """
    h, w = image.shape[:2]
    target_h, target_w = target_size
    
    # Calculate padding
    pad_h = max(0, target_h - h)
    pad_w = max(0, target_w - w)
    
    top = pad_h // 2
    bottom = pad_h - top
    left = pad_w // 2
    right = pad_w - left
    
    # Pad the image
    padded = np.pad(
        image,
        ((top, bottom), (left, right), (0, 0)),
        mode='constant',
        constant_values=255
    )
    
    return padded

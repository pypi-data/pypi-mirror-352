# diffeomorphic_movie.py
"""
Module for creating diffeomorphically transformed movies.

Please reference: Stojanoski, B., & Cusack, R. (2014). Time to wave good-bye to phase scrambling: Creating controlled scrambled images using
diffeomorphic transformations. Journal of Vision, 14(12), 6. doi:10.1167/14.12.6
"""
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import os
import cv2
from scipy.interpolate import griddata
import random
import string
import logging
from .utils import ensure_directory, load_image, extract_frames, create_video_from_frames

# Setup logging
logger = logging.getLogger(__name__)

def transform_movie(input_path, output_path=None, max_distortion=60, n_steps=20, n_comp=10, create_video=True):
    """
    Create diffewarped movies.
    
    Parameters:
    -----------
    input_path : str
        Path to the input image or video file
    output_path : str, optional
        Path to the output directory. If None, uses 'output_movie' in current directory
    max_distortion : int, optional
        Maximum amount of distortion, default is 60
    n_steps : int, optional
        Number of morphing steps, default is 20
    n_comp : int, optional
        Number of components for distortion field, default is 10
    create_video : bool, optional
        Whether to create a video from the processed frames, default is True
        
    Returns:
    --------
    dict
        Dictionary containing output paths for frames and video
        
    Notes:
    ------
    MTurk perceptual ratings of images are based on max_distortion = 80 and n_steps = 20
    """
    # Setup parameters
    maxdistortion = max_distortion
    nsteps = n_steps
    ncomp = n_comp
    
    picpath = input_path
    outpicpath = output_path if output_path else 'output_movie'
    frames_dir = os.path.join(outpicpath, 'frames')
    video_dir = os.path.join(outpicpath, 'video')
    
    # Create output directories
    ensure_directory(outpicpath)
    ensure_directory(frames_dir)
    if create_video:
        ensure_directory(video_dir)
    
    # Initialize results
    result = {
        'frames': [],
        'video': None,
    }
    
    # Process input file
    frames = []
    
    if os.path.isfile(picpath):
        # Check if it's a video file
        if picpath.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            # Process video file
            logger.info(f"Processing video file: {picpath}")
            frames = extract_frames(picpath)
        else:
            # Process single image file
            logger.info(f"Processing image file as a single frame: {picpath}")
            img, _ = load_image(picpath)
            if img is not None:
                frames = [img]
    else:
        logger.error(f"File {picpath} not found")
        return result
    
    if not frames:
        logger.error("No frames to process")
        return result
    
    # Process each frame
    processed_frames = []
    
    for i, frame in enumerate(frames):
        logger.info(f"Processing frame {i+1}/{len(frames)}")
        
        # Get frame dimensions
        Psz = frame.shape
        
        # Calculate image size with padding for distortion
        imsz = max(Psz[0], Psz[1]) + 4 * maxdistortion
        
        # Generate distortion field for all frames
        cx, cy = getdiffeo(imsz, maxdistortion, nsteps, ncomp)
        xi, yi = np.meshgrid(np.arange(1, imsz + 1), np.arange(1, imsz + 1))
        XI, YI = xi.T, yi.T
        
        cy = YI + cy
        cx = XI + cx
        mask = (cx < 1) | (cx > imsz) | (cy < 1) | (cy > imsz)
        cx[mask] = 1
        cy[mask] = 1
        
        # Create white background image
        Im = np.ones((imsz, imsz, 3), dtype=np.uint8) * 255
        
        # Pad image if necessary
        x1 = int(np.round((imsz - Psz[0]) / 2))
        y1 = int(np.round((imsz - Psz[1]) / 2))
        
        # Add fourth plane if necessary
        if Psz[2] == 4:
            Im = np.concatenate([Im, np.zeros((imsz, imsz, 1), dtype=np.uint8)], axis=2)
        
        # Place image in center
        Im[x1:x1+Psz[0], y1:y1+Psz[1], :Psz[2]] = frame
        
        # Pad with mirrored extensions of image
        if x1 > 0:
            Im[:x1, y1:y1+Psz[1], :] = frame[x1-1::-1, :, :]
            Im[x1+Psz[0]:, y1:y1+Psz[1], :] = frame[::-1, :, :][:imsz-x1-Psz[0], :, :]
        
        if y1 > 0:
            Im[:, :y1, :] = Im[:, y1+y1-1:y1-1:-1, :]
            Im[:, y1+Psz[1]:, :] = Im[:, y1+Psz[1]-1:y1+Psz[1]-1-(imsz-y1-Psz[1]):-1, :]
        
        # Start off with undistorted image
        interpIm = Im.copy()
        
        for j in range(nsteps):
            logger.debug(f"  Processing step {j+1}/{nsteps}")
            interpIm = interpolate_image(interpIm, cy, cx)
        
        # Trim down again
        interpIm = interpIm[x1:x1+Psz[0], y1:y1+Psz[1], :Psz[2]]
        
        # Save result
        output_filename = f'movie_warped_{i+1:04d}.png'
        output_path = os.path.join(frames_dir, output_filename)
        try:
            Image.fromarray(interpIm.astype(np.uint8)).save(output_path)
            logger.info(f"Saved frame: {output_filename}")
            result['frames'].append(output_path)
            processed_frames.append(interpIm)
        except Exception as e:
            logger.error(f"Error saving frame {output_filename}: {e}")
    
    # Create output video if requested
    if create_video and processed_frames:
        video_path = os.path.join(video_dir, 'output_movie.mp4')
        result['video'] = create_video_from_frames(processed_frames, video_path)
    
    return result

def interpolate_image(image, cy, cx):
    """
    Interpolate image using the coordinate transforms
    """
    result = np.zeros_like(image)
    
    # Create coordinate arrays for interpolation
    h, w = image.shape[:2]
    y_coords, x_coords = np.mgrid[0:h, 0:w]
    
    for channel in range(image.shape[2]):
        # Flatten arrays for griddata
        points = np.column_stack((y_coords.ravel(), x_coords.ravel()))
        values = image[:, :, channel].ravel()
        
        # New coordinates (subtract 1 to convert from MATLAB 1-based to Python 0-based)
        new_points = np.column_stack(((cy - 1).ravel(), (cx - 1).ravel()))
        
        # Interpolate
        interpolated = griddata(points, values, new_points, method='linear', fill_value=0)
        result[:, :, channel] = interpolated.reshape(h, w)
    
    return result.astype(np.uint8)

def getdiffeo(imsz, maxdistortion, nsteps, ncomp=6):
    """
    Generate diffeomorphic transformation fields
    
    Parameters:
    imsz: int - size of the image
    maxdistortion: float - maximum distortion amount
    nsteps: int - number of steps
    ncomp: int - number of components (default 6)
    
    Returns:
    XIn, YIn: displacement fields
    """
    # Create meshgrid
    xi, yi = np.meshgrid(np.arange(1, imsz + 1), np.arange(1, imsz + 1))
    XI, YI = xi.T, yi.T  # Transpose to match MATLAB's meshgrid behavior
    
    # Make diffeomorphic warp field by adding random DCTs
    ph = np.random.rand(ncomp, ncomp, 4) * 2 * np.pi
    a = np.random.rand(ncomp, ncomp) * 2 * np.pi
    b = np.random.rand(ncomp, ncomp) * 2 * np.pi  # different amplitudes for x and y DCT components
    
    Xn = np.zeros((imsz, imsz))
    Yn = np.zeros((imsz, imsz))
    
    for xc in range(1, ncomp + 1):
        for yc in range(1, ncomp + 1):
            Xn += a[xc-1, yc-1] * np.cos(xc * XI / imsz * 2 * np.pi + ph[xc-1, yc-1, 0]) * \
                  np.cos(yc * YI / imsz * 2 * np.pi + ph[xc-1, yc-1, 1])
            Yn += b[xc-1, yc-1] * np.cos(xc * XI / imsz * 2 * np.pi + ph[xc-1, yc-1, 2]) * \
                  np.cos(yc * YI / imsz * 2 * np.pi + ph[xc-1, yc-1, 3])
    
    # Normalize to RMS of warps in each direction
    Xn = Xn / np.sqrt(np.mean(Xn**2))
    Yn = Yn / np.sqrt(np.mean(Yn**2))
    
    YIn = maxdistortion * Yn / nsteps
    XIn = maxdistortion * Xn / nsteps
    
    return XIn, YIn

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Run the diffeomorphic movie transformation
    transform_movie('ah2.jpg')

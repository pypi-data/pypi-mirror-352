# diffeomorphic_movie_warpshift.py
"""
Module for creating diffeomorphically transformed movies with gradually drifting warp field.

Please reference: Stojanoski, B., & Cusack, R (2013). Time to wave goodbye to phase scrambling – 
creating unrecognizable control stimuli using a diffeomorphic transform.  Abstract Vision Science Society
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

def transform_warpshift(input_path, output_path=None, max_distortion=60, n_steps=20, 
                        n_comp=10, phase_drift=np.pi/8, num_frames=10, frame_rate=30,
                        create_video=True):
    """
    Create diffewarped movies with gradually drifting warp field.
    
    Parameters:
    -----------
    input_path : str
        Path to the input image or video file
    output_path : str, optional
        Path to the output directory. If None, uses 'output_warpshift' in current directory
    max_distortion : int, optional
        Maximum amount of distortion, default is 60
    n_steps : int, optional
        Number of morphing steps, default is 20
    n_comp : int, optional
        Number of components for distortion field, default is 10
    phase_drift : float, optional
        Amount of phase drift for the warp field, default is pi/8
    num_frames : int, optional
        Number of frames to generate, default is 10
    frame_rate : int, optional
        Simulated frame rate, default is 30
    create_video : bool, optional
        Whether to create a video from the processed frames, default is True
        
    Returns:
    --------
    dict
        Dictionary containing output paths for frames and video
        
    Notes:
    ------
    The phase of the components takes a random walk to create a drifting warp field.
    """
    # Setup parameters
    maxdistortion = max_distortion
    nsteps = n_steps
    ncomp = n_comp
    phasedrift = phase_drift
    
    picpath = input_path
    outvidpath = output_path if output_path else 'output_warpshift'
    frames_dir = os.path.join(outvidpath, 'frames')
    video_dir = os.path.join(outvidpath, 'video')
    
    # Create output directories
    ensure_directory(outvidpath)
    ensure_directory(frames_dir)
    if create_video:
        ensure_directory(video_dir)
    
    # Initialize results
    result = {
        'frames': [],
        'video': None,
    }
    
    # Process input file
    if os.path.isfile(picpath):
        # Check if it's a video file
        if picpath.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            # Process video file - for warpshift we only need one frame
            logger.info(f"Processing video file (first frame only): {picpath}")
            frames = extract_frames(picpath, max_frames=1)
            if frames:
                source_img = frames[0]
            else:
                logger.error("Could not extract frames from video")
                return result
        else:
            # Process single image file
            logger.info(f"Processing image file: {picpath}")
            source_img, _ = load_image(picpath)
            if source_img is None:
                logger.error(f"Could not load image {picpath}")
                return result
    else:
        logger.error(f"File {picpath} not found")
        return result
    
    # Get image dimensions
    Psz = source_img.shape
    
    # Calculate image size with padding for distortion
    imsz = max(Psz[0], Psz[1]) + 4 * maxdistortion
    
    logger.info("Generating initial distortion fields...")
    # Generate distortion field for all frames
    cx, cy, a, b, ph = getdiffeo_with_params(imsz, maxdistortion, nsteps, ncomp)
    cx, cy = postprocess_diffeo(imsz, cx, cy)
    
    # Create next distortion field (simulate 1 second later)
    ph_next = ph + phasedrift * np.random.randn(*ph.shape)
    nextcx, nextcy, a, b, ph_next = getdiffeo_with_params(imsz, maxdistortion, nsteps, ncomp, a, b, ph_next)
    nextcx, nextcy = postprocess_diffeo(imsz, nextcx, nextcy)
    
    # Create white background image
    Im = np.ones((imsz, imsz, 3), dtype=np.uint8) * 255
    
    # Pad image if necessary
    x1 = int(np.round((imsz - Psz[0]) / 2))
    y1 = int(np.round((imsz - Psz[1]) / 2))
    
    # Add fourth plane if necessary
    if Psz[2] == 4:
        Im = np.concatenate([Im, np.zeros((imsz, imsz, 1), dtype=np.uint8)], axis=2)
    
    # Place image in center
    Im[x1:x1+Psz[0], y1:y1+Psz[1], :Psz[2]] = source_img
    
    # Pad with mirrored extensions of image
    if x1 > 0:
        Im[:x1, y1:y1+Psz[1], :] = source_img[x1-1::-1, :, :]
        Im[x1+Psz[0]:, y1:y1+Psz[1], :] = source_img[::-1, :, :][:imsz-x1-Psz[0], :, :]
    
    if y1 > 0:
        Im[:, :y1, :] = Im[:, y1+y1-1:y1-1:-1, :]
        Im[:, y1+Psz[1]:, :] = Im[:, y1+Psz[1]-1:y1+Psz[1]-1-(imsz-y1-Psz[1]):-1, :]
    
    # Process each frame with drifting warp field
    processed_frames = []
    
    for frame in range(num_frames):
        logger.info(f"Processing frame {frame+1}/{num_frames}")
        
        # Simulate time progression
        z = frame + 1
        
        # Check if we need to update the warp field (every second)
        if phasedrift > 0:
            newsecs = int(np.floor(z / frame_rate))
            if frame > 0 and newsecs != int(np.floor((z-1) / frame_rate)):
                logger.info(f"Updating warp field at second {newsecs}")
                # Update phase
                ph = ph_next + phasedrift * np.random.randn(*ph.shape)
                
                # Create new distortion field
                cx = nextcx.copy()
                cy = nextcy.copy()
                nextcx, nextcy, a, b, ph = getdiffeo_with_params(imsz, maxdistortion, nsteps, ncomp, a, b, ph)
                nextcx, nextcy = postprocess_diffeo(imsz, nextcx, nextcy)
        
        # Interpolate between current and next distortion field
        f = (z / frame_rate) - np.floor(z / frame_rate)
        cyi = (1 - f) * cy + f * nextcy
        cxi = (1 - f) * cx + f * nextcx
        
        # Start off with undistorted image
        interpIm = Im.copy()
        
        for j in range(nsteps):
            interpIm = interpolate_image(interpIm, cyi, cxi)
        
        # Trim down again
        interpIm = interpIm[x1:x1+Psz[0], y1:y1+Psz[1], :Psz[2]]
        
        # Save frame
        output_filename = f'warpshift_frame_{frame+1:03d}.png'
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
        video_path = os.path.join(video_dir, 'output_warpshift.mp4')
        result['video'] = create_video_from_frames(processed_frames, video_path, fps=frame_rate)
    
    logger.info("Completed warpshift processing")
    return result

def postprocess_diffeo(imsz, cx, cy):
    """Post process diffeomorphic fields"""
    xi, yi = np.meshgrid(np.arange(1, imsz + 1), np.arange(1, imsz + 1))
    XI, YI = xi.T, yi.T
    
    cy = YI + cy
    cx = XI + cx
    mask = (cx < 1) | (cx > imsz) | (cy < 1) | (cy > imsz)
    cx[mask] = 1
    cy[mask] = 1
    
    return cx, cy

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

def getdiffeo_with_params(imsz, maxdistortion, nsteps, ncomp=6, a=None, b=None, ph=None):
    """
    Generate diffeomorphic transformation fields with optional existing parameters
    
    Parameters:
    imsz: int - size of the image
    maxdistortion: float - maximum distortion amount
    nsteps: int - number of steps
    ncomp: int - number of components (default 6)
    a, b, ph: optional existing parameters
    
    Returns:
    XIn, YIn: displacement fields
    a, b, ph: parameters for reuse
    """
    # Create meshgrid
    xi, yi = np.meshgrid(np.arange(1, imsz + 1), np.arange(1, imsz + 1))
    XI, YI = xi.T, yi.T  # Transpose to match MATLAB's meshgrid behavior
    
    # Make diffeomorphic warp field by adding random DCTs
    if ph is None:
        ph = np.random.rand(ncomp, ncomp, 4) * 2 * np.pi
    if a is None:
        a = np.random.rand(ncomp, ncomp) * 2 * np.pi
    if b is None:
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
    
    return XIn, YIn, a, b, ph

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Run the diffeomorphic movie warpshift transformation
    transform_warpshift('d5.jpg')

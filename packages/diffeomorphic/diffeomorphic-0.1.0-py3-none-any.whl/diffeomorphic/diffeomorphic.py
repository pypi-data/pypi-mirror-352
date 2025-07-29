# diffeomorphic.py
"""
Module for creating diffeomorphically transformed images.

Please reference: Stojanoski, B., & Cusack, R. (2014). Time to wave good-bye to phase scrambling: Creating controlled scrambled images using
diffeomorphic transformations. Journal of Vision, 14(12), 6. doi:10.1167/14.12.6
"""
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import os
import glob
import tempfile
import scipy.io
from scipy.interpolate import griddata
import random
import string
import logging
from .utils import ensure_directory, load_image, pad_image

# Setup logging
logger = logging.getLogger(__name__)

def transform_image(input_path, output_path=None, max_distortion=80, n_steps=20, image_size=500, show_plots=True):
    """
    Create diffeomorphically warped images.
    
    Parameters:
    -----------
    input_path : str
        Path to the input image file
    output_path : str, optional
        Path to the output directory. If None, uses 'output' in current directory
    max_distortion : int, optional
        Maximum amount of distortion, default is 80
    n_steps : int, optional
        Number of morphing steps (images), default is 20
    image_size : int, optional
        Size of output images, default is 500
    show_plots : bool, optional
        Whether to display visualization plots, default is True
        
    Returns:
    --------
    dict
        Dictionary containing filenames of transformed images
        
    Notes:
    ------
    MTurk perceptual ratings of images are based on max_distortion = 80 and n_steps = 20
    """
    # Setup parameters
    maxdistortion = max_distortion
    nsteps = n_steps
    imsz = image_size
    
    picpath = input_path
    outpicpath = output_path if output_path else 'output'
    
    # Create output directory
    ensure_directory(outpicpath)
    
    imgtype = 'jpg'  # file type
    
    # Handle single file
    if os.path.exists(picpath):
        fns = [picpath]
        logger.info(f"Processing image file: {picpath}")
    else:
        logger.error(f"Error: Image file '{picpath}' not found!")
        return {}
    
    # Create meshgrid
    xi, yi = np.meshgrid(np.arange(1, imsz + 1), np.arange(1, imsz + 1))
    XI, YI = xi.T, yi.T  # Transpose to match MATLAB's meshgrid behavior
    
    # Random phase offset
    phaseoffset = int(np.floor(np.random.rand() * 40))
    
    # Initialize storage for filenames
    filenames = {}
    origfn = {}
    
    if show_plots:
        plt.figure(10)
    
    for i, filename in enumerate(fns):  # This is the number of objects in the directory
        logger.info(f"Processing image {i+1}/{len(fns)}: {filename}")
        
        # Create white background image (255 for white, 128 for grey)
        Im = np.ones((imsz, imsz, 3), dtype=np.uint8) * 255
        
        # Read image
        try:
            img, _ = load_image(filename)
            if img is None:
                logger.error(f"Failed to load image {filename}")
                continue
                
            P = img
            Psz = P.shape
        except Exception as e:
            logger.error(f"Error reading image {filename}: {e}")
            continue
        
        # Upsample by factor of 2 in two dimensions
        P2 = np.zeros((2 * Psz[0], 2 * Psz[1], Psz[2]), dtype=P.dtype)
        P2[::2, ::2, :] = P
        P2[1::2, ::2, :] = P
        P2[1::2, 1::2, :] = P
        P2[::2, 1::2, :] = P
        P = P2
        Psz = P.shape
        
        # Resize image if it's larger than the target size
        if Psz[0] > imsz or Psz[1] > imsz:
            # Calculate scaling factor to fit within imsz
            scale = min(imsz / Psz[0], imsz / Psz[1])
            new_height = int(Psz[0] * scale)
            new_width = int(Psz[1] * scale)
            P_img = Image.fromarray(P)
            P_img = P_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            P = np.array(P_img)
            Psz = P.shape
        
        # Pad image if necessary
        x1 = int(np.round((imsz - Psz[0]) / 2))
        y1 = int(np.round((imsz - Psz[1]) / 2))
        
        # Add fourth plane if necessary
        if Psz[2] == 4:
            Im = np.concatenate([Im, np.zeros((imsz, imsz, 1), dtype=np.uint8)], axis=2)
        
        # Place image in center
        x_end = min(x1 + Psz[0], imsz)
        y_end = min(y1 + Psz[1], imsz)
        p_x_end = x_end - x1
        p_y_end = y_end - y1
        
        Im[x1:x_end, y1:y_end, :Psz[2]] = P[:p_x_end, :p_y_end, :]
        
        # Get diffeomorphic transformations
        cxA, cyA = getdiffeo(imsz, maxdistortion, nsteps)
        cxB, cyB = getdiffeo(imsz, maxdistortion, nsteps)
        cxF, cyF = getdiffeo(imsz, maxdistortion, nsteps)
        
        interpIm = Im.copy()
        if show_plots:
            plt.figure(11)
            plt.clf()
        
        for quadrant in range(1, 5):  # 1 to 4
            logger.info(f"  Processing quadrant {quadrant}/4")
            if quadrant == 1:
                cx = cxA.copy()
                cy = cyA.copy()
                ind = 1
                indstep = 1
            elif quadrant == 2:
                cx = cxF - cxA
                cy = cyF - cyA
            elif quadrant == 3:
                ind = 4 * nsteps
                indstep = -1
                interpIm = Im.copy()
                cx = cxB.copy()
                cy = cyB.copy()
            elif quadrant == 4:
                cx = cxF - cxB
                cy = cyF - cyB
            
            cy = YI + cy
            cx = XI + cx
            
            # Create mask for out-of-bounds values
            mask = (cx < 1) | (cx > imsz) | (cy < 1) | (cy > imsz)
            cx[mask] = 1
            cy[mask] = 1
            
            if show_plots:
                plt.figure(10)
                plt.subplot(4, 2, quadrant * 2 - 1)
                plt.imshow(cx, cmap='viridis')
                plt.colorbar()
                plt.title(f'cx Quadrant {quadrant}')
                
                plt.subplot(4, 2, quadrant * 2)
                plt.imshow(cy, cmap='viridis')
                plt.colorbar()
                plt.title(f'cy Quadrant {quadrant}')
            
            w = 0.1
            
            for j in range(nsteps):  # This is the number of steps - Total number of warps is nsteps * quadrant
                if j % 5 == 0:  # Log progress every 5 steps
                    logger.debug(f"    Step {j+1}/{nsteps}")
                
                centrex = 0.5 + (0.5 - w/2) * np.cos((phaseoffset + ind) * 2 * np.pi / (4 * nsteps))
                centrey = 0.5 + (0.5 - w/2) * np.sin((phaseoffset + ind) * 2 * np.pi / (4 * nsteps))
                
                if show_plots:
                    plt.figure(11)
                    if ind % 2 == 0:
                        ax = plt.axes([centrex - w/2, centrey - w/2, w, w])
                        plt.imshow(interpIm[:, :, :3])
                        plt.axis('off')
                
                # Generate random string for filename
                randstr = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
                
                # Save image
                try:
                    output_filename = f'Im_{i+1:02d}_{ind:02d}.{imgtype}'
                    Image.fromarray(interpIm[:, :, :3]).save(os.path.join(outpicpath, output_filename))
                    logger.info(f"    Saved image: {output_filename}")
                except Exception as e:
                    logger.warning(f"    Could not save image {output_filename}: {e}")
                
                randfn = f'W_{i+1:02d}_{ind:02d}_{randstr}.{imgtype}'
                
                # Interpolate image
                try:
                    interpIm = interpolate_image(interpIm, cy, cx)
                except Exception as e:
                    logger.warning(f"    Interpolation failed at step {j+1}: {e}")
                    # Skip this step and continue
                    ind += indstep
                    continue
                
                # Store filenames
                if i not in filenames:
                    filenames[i] = {}
                filenames[i][ind] = randfn
                origfn[i] = os.path.basename(filename)
                
                # Save filename mapping
                try:
                    scipy.io.savemat(os.path.join(outpicpath, 'filename_mapping.mat'), 
                                     {'filenames': filenames, 'origfn': origfn})
                except Exception as e:
                    logger.warning(f"Could not save filename mapping: {e}")
                
                ind += indstep
    
    if show_plots:
        plt.show()
    logger.info("Processing completed!")
    return filenames

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

def getdiffeo(imsz, maxdistortion, nsteps):
    """
    Generate diffeomorphic transformation fields
    
    Parameters:
    imsz: int - size of the image
    maxdistortion: float - maximum distortion amount
    nsteps: int - number of steps
    
    Returns:
    XIn, YIn: displacement fields
    """
    ncomp = 6
    
    # Create meshgrid
    xi, yi = np.meshgrid(np.arange(1, imsz + 1), np.arange(1, imsz + 1))
    XI, YI = xi.T, yi.T  # Transpose to match MATLAB's meshgrid behavior
    
    # Make diffeomorphic warp field by adding random DCTs
    ph = np.random.rand(ncomp, ncomp, 4) * 2 * np.pi
    a = np.random.rand(ncomp, ncomp) * 2 * np.pi
    
    Xn = np.zeros((imsz, imsz))
    Yn = np.zeros((imsz, imsz))
    
    for xc in range(1, ncomp + 1):
        for yc in range(1, ncomp + 1):
            Xn += a[xc-1, yc-1] * np.cos(xc * XI / imsz * 2 * np.pi + ph[xc-1, yc-1, 0]) * \
                  np.cos(yc * YI / imsz * 2 * np.pi + ph[xc-1, yc-1, 1])
            Yn += a[xc-1, yc-1] * np.cos(xc * XI / imsz * 2 * np.pi + ph[xc-1, yc-1, 2]) * \
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
    
    # Run the diffeomorphic transformation on ah2.jpg
    transform_image('ah2.jpg')

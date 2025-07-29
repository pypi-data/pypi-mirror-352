# Diffeomorphic API Documentation

## Main Functions

### transform_image

```python
diffeomorphic.transform_image(input_path, output_path=None, max_distortion=80, n_steps=20, image_size=500, show_plots=True)
```

Create diffeomorphically warped images.

**Parameters:**
- `input_path` (str): Path to the input image file
- `output_path` (str, optional): Path to the output directory. If None, uses 'output' in current directory
- `max_distortion` (int, optional): Maximum amount of distortion, default is 80
- `n_steps` (int, optional): Number of morphing steps (images), default is 20
- `image_size` (int, optional): Size of output images, default is 500
- `show_plots` (bool, optional): Whether to display visualization plots, default is True

**Returns:**
- dict: Dictionary containing filenames of transformed images

**Notes:**
MTurk perceptual ratings of images are based on max_distortion = 80 and n_steps = 20

### transform_movie

```python
diffeomorphic.transform_movie(input_path, output_path=None, max_distortion=60, n_steps=20, n_comp=10)
```

Create diffewarped movies.

**Parameters:**
- `input_path` (str): Path to the input image or video file
- `output_path` (str, optional): Path to the output directory. If None, uses 'output_movie' in current directory
- `max_distortion` (int, optional): Maximum amount of distortion, default is 60
- `n_steps` (int, optional): Number of morphing steps, default is 20
- `n_comp` (int, optional): Number of components for distortion field, default is 10

**Returns:**
- list: List of output filenames

### transform_warpshift

```python
diffeomorphic.transform_warpshift(input_path, output_path=None, max_distortion=60, n_steps=20, n_comp=10, phase_drift=np.pi/8, num_frames=10, frame_rate=30)
```

Create diffewarped movies with gradually drifting warp field.

**Parameters:**
- `input_path` (str): Path to the input image or video file
- `output_path` (str, optional): Path to the output directory. If None, uses 'output_warpshift' in current directory
- `max_distortion` (int, optional): Maximum amount of distortion, default is 60
- `n_steps` (int, optional): Number of morphing steps, default is 20
- `n_comp` (int, optional): Number of components for distortion field, default is 10
- `phase_drift` (float, optional): Amount of phase drift for the warp field, default is pi/8
- `num_frames` (int, optional): Number of frames to generate, default is 10
- `frame_rate` (int, optional): Simulated frame rate, default is 30

**Returns:**
- list: List of output filenames

**Notes:**
The phase of the components takes a random walk to create a drifting warp field.

## Command Line Interface

Diffeomorphic provides three command-line tools:

### Image Transformation

```
diffeomorphic-image --input IMAGE_PATH --output OUTPUT_DIR [options]
```

Options:
- `--max-distortion`, `-d`: Maximum distortion (default: 80)
- `--steps`, `-s`: Number of morphing steps (default: 20)
- `--size`: Size of output images (default: 500)
- `--verbose`, `-v`: Verbose output

### Movie Transformation

```
diffeomorphic-movie --input IMAGE_PATH --output OUTPUT_DIR [options]
```

Options:
- `--max-distortion`, `-d`: Maximum distortion (default: 60)
- `--steps`, `-s`: Number of morphing steps (default: 20)
- `--components`, `-c`: Number of components (default: 10)
- `--verbose`, `-v`: Verbose output

### Warpshift Transformation

```
diffeomorphic-warpshift --input IMAGE_PATH --output OUTPUT_DIR [options]
```

Options:
- `--max-distortion`, `-d`: Maximum distortion (default: 60)
- `--steps`, `-s`: Number of morphing steps (default: 20)
- `--components`, `-c`: Number of components (default: 10)
- `--phase-drift`, `-p`: Phase drift amount (default: 0.39)
- `--frames`, `-f`: Number of frames to generate (default: 10)
- `--frame-rate`, `-r`: Simulated frame rate (default: 30)
- `--verbose`, `-v`: Verbose output

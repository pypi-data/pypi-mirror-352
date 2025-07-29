# Diffeomorphic User Guide

## Introduction

Diffeomorphic is a Python package that implements diffeomorphic transformations for image and video morphing in psychological experiments. It provides tools to create controlled scrambled images that maintain local structure while making them unrecognizable.

This guide walks you through the installation, basic usage, and advanced features of the Diffeomorphic package.

## Installation

### Requirements

- Python 3.6 or higher
- NumPy
- Matplotlib
- PIL (Pillow)
- SciPy
- OpenCV

### Install via pip

```bash
pip install diffeomorphic
```

### Install from source

```bash
git clone https://github.com/AhsanKhodami/diffeomorphic.git
cd diffeomorphic
pip install -e .
```

## Basic Usage

### Command Line Interface

Diffeomorphic provides three command-line tools for different types of transformations:

#### Image Transformation

Transform a single image with diffeomorphic warping:

```bash
diffeomorphic-image --input path/to/image.jpg --output output_dir
```

Options:
- `--input`, `-i`: Input image file (required)
- `--output`, `-o`: Output directory (default: 'output')
- `--max-distortion`, `-d`: Maximum distortion (default: 80)
- `--steps`, `-s`: Number of morphing steps (default: 20)
- `--size`: Size of output images (default: 500)
- `--no-plots`: Disable visualization plots
- `--verbose`, `-v`: Verbose output

#### Movie Transformation

Transform an image or video into a morphed movie:

```bash
diffeomorphic-movie --input path/to/video.mp4 --output output_dir
```

Options:
- `--input`, `-i`: Input image or video file (required)
- `--output`, `-o`: Output directory (default: 'output_movie')
- `--max-distortion`, `-d`: Maximum distortion (default: 60)
- `--steps`, `-s`: Number of morphing steps (default: 20)
- `--components`, `-c`: Number of components (default: 10)
- `--no-video`: Do not create a video from frames
- `--verbose`, `-v`: Verbose output

#### Warpshift Transformation

Transform an image or video with a gradually drifting warp field:

```bash
diffeomorphic-warpshift --input path/to/image.jpg --output output_dir
```

Options:
- `--input`, `-i`: Input image or video file (required)
- `--output`, `-o`: Output directory (default: 'output_warpshift')
- `--max-distortion`, `-d`: Maximum distortion (default: 60)
- `--steps`, `-s`: Number of morphing steps (default: 20)
- `--components`, `-c`: Number of components (default: 10)
- `--phase-drift`, `-p`: Phase drift amount (default: 0.39)
- `--frames`, `-f`: Number of frames to generate (default: 10)
- `--frame-rate`, `-r`: Simulated frame rate (default: 30)
- `--no-video`: Do not create a video from frames
- `--verbose`, `-v`: Verbose output

### Python API

#### Transform a Single Image

```python
import diffeomorphic

result = diffeomorphic.transform_image(
    input_path="path/to/image.jpg",
    output_path="output_dir",
    max_distortion=80,
    n_steps=20,
    image_size=500,
    show_plots=True
)

# result contains a dictionary of output filenames
```

#### Transform a Video

```python
import diffeomorphic

result = diffeomorphic.transform_movie(
    input_path="path/to/video.mp4",
    output_path="output_dir",
    max_distortion=60,
    n_steps=20,
    n_comp=10,
    create_video=True
)

# result contains paths to output frames and video
print(f"Video created: {result['video']}")
print(f"Number of frames: {len(result['frames'])}")
```

#### Transform with Warpshift

```python
import diffeomorphic

result = diffeomorphic.transform_warpshift(
    input_path="path/to/image.jpg",
    output_path="output_dir",
    max_distortion=60,
    n_steps=20,
    n_comp=10,
    phase_drift=0.39,
    num_frames=10,
    frame_rate=30,
    create_video=True
)

# result contains paths to output frames and video
print(f"Video created: {result['video']}")
```

## Advanced Usage

### Customizing Distortion Fields

The diffeomorphic transformations in Diffeomorphic are controlled by several parameters:

- **max_distortion**: Controls the amount of distortion applied. Higher values result in more distorted images.
- **n_steps**: Controls the number of morphing steps. More steps result in smoother transitions but slower processing.
- **n_comp**: Controls the number of components in the distortion field. Higher values result in more complex distortions.

### Processing Multiple Images

You can process multiple images by iterating through them:

```python
import os
import diffeomorphic

input_dir = "input_images"
output_dir = "output_images"

for filename in os.listdir(input_dir):
    if filename.endswith(('.jpg', '.png', '.jpeg')):
        input_path = os.path.join(input_dir, filename)
        diffeomorphic.transform_image(
            input_path=input_path,
            output_path=output_dir,
            max_distortion=80,
            n_steps=10
        )
```

### Creating Animations

You can create animations with gradually increasing distortion:

```python
import os
import diffeomorphic
import numpy as np

input_path = "input.jpg"
output_dir = "animation_frames"

# Create frames with increasing distortion
for i in range(1, 11):
    distortion = i * 10  # 10, 20, 30, ..., 100
    
    diffeomorphic.transform_image(
        input_path=input_path,
        output_path=os.path.join(output_dir, f"distortion_{distortion}"),
        max_distortion=distortion,
        n_steps=5,
        show_plots=False
    )
```

## Troubleshooting

### Common Issues

1. **Memory Issues**: Processing large images or videos can consume a lot of memory. Try reducing the image size or using fewer morphing steps.

2. **Slow Processing**: Diffeomorphic transformations can be computationally intensive. To speed up processing:
   - Reduce the number of morphing steps
   - Use smaller images
   - Disable visualization plots

3. **Video Creation Failures**: If video creation fails, ensure that OpenCV is correctly installed with video writing capabilities.

### Logging

Diffeomorphic uses Python's logging system. You can enable verbose logging to get more information:

```python
import logging
import diffeomorphic

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Now run your transformation
diffeomorphic.transform_image(...)
```

## References

Stojanoski, B., & Cusack, R. (2014). Time to wave good-bye to phase scrambling: Creating controlled scrambled images using diffeomorphic transformations. Journal of Vision, 14(12), 6. doi:10.1167/14.12.6

# Diffeomorphic

A Python package for creating diffeomorphically transformed images and videos for psychological experiments.

## Overview

Diffeomorphic implements diffeomorphic transformations for image and video morphing, as described in:

Stojanoski, B., & Cusack, R. (2014). Time to wave good-bye to phase scrambling: Creating controlled scrambled images using diffeomorphic transformations. Journal of Vision, 14(12), 6. doi:10.1167/14.12.6

This Python package was developed by Mohammad Ahsan Khodami, based on the original algorithms described in the paper by Stojanoski & Cusack.

## Installation

```bash
pip install diffeomorphic
```

## Usage

### As a command-line tool

```bash
# Transform a single image
diffeomorphic-image --input image.jpg --output output_dir --maxdistortion 80 --nsteps 20

# Transform a video
diffeomorphic-movie --input video.mp4 --output output_dir --maxdistortion 60 --nsteps 20

# Transform with warpshift
diffeomorphic-warpshift --input image.jpg --output output_dir --maxdistortion 60 --nsteps 20 --phasedrift 0.39
```

### As a Python library

```python
import diffeomorphic

# Transform a single image
diffeomorphic.transform_image(
    input_path="image.jpg", 
    output_path="output_dir",
    max_distortion=80,
    n_steps=20
)

# Transform a video
diffeomorphic.transform_movie(
    input_path="video.mp4", 
    output_path="output_dir",
    max_distortion=60,    n_steps=20
)

# Transform with warpshift
diffeomorphic.transform_warpshift(
    input_path="image.jpg", 
    output_path="output_dir",
    max_distortion=60,
    n_steps=20,
    phase_drift=0.39
)
```

## License

MIT License

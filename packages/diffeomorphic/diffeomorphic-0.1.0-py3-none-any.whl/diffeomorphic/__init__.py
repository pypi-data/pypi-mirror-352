"""
Diffeomorphic - Diffeomorphic transformations for image and video morphing in psychological experiments

Diffeomorphic implements diffeomorphic transformations that can be used to create distorted/morphed 
versions of images and videos for psychological experiments. The transformations maintain the 
local structure and global arrangement of the visual content while making it unrecognizable.

Main Functions:
--------------
transform_image
    Apply diffeomorphic transformations to a single image
transform_movie
    Apply diffeomorphic transformations to create a morphed movie
transform_warpshift
    Apply diffeomorphic transformations with a gradually drifting warp field

Please reference: 
Stojanoski, B., & Cusack, R. (2014). Time to wave good-bye to phase scrambling: Creating controlled scrambled images using
diffeomorphic transformations. Journal of Vision, 14(12), 6. doi:10.1167/14.12.6

Originally by Rhodri Cusack and Bobby Stojanoski, July 2013
Converted to Python package by Mohammad Ahsan Khodami, 2025
"""

from .diffeomorphic import transform_image
from .diffeomorphic_movie import transform_movie
from .diffeomorphic_movie_warpshift import transform_warpshift

# Dynamically retrieve version from git tags
try:
    from ._version import __version__
except ImportError:
    __version__ = "0.1.0"  # Default version if not in a proper install

__all__ = ['transform_image', 'transform_movie', 'transform_warpshift']

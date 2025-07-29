"""
Command-line interface for the diffeomorphic package.
"""
import argparse
import logging
import sys
import os
from . import transform_image, transform_movie, transform_warpshift
from .utils import ensure_directory

def setup_logging(verbose=False):
    """Set up logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Diffeomorphic - Diffeomorphic transformations for images and videos')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Image transformation command
    image_parser = subparsers.add_parser('image', help='Apply diffeomorphic transformations to images')
    image_parser.add_argument('--input', '-i', required=True, help='Input image file')
    image_parser.add_argument('--output', '-o', default='output', help='Output directory')
    image_parser.add_argument('--max-distortion', '-d', type=int, default=80, 
                             help='Maximum distortion (default: 80)')
    image_parser.add_argument('--steps', '-s', type=int, default=20, 
                             help='Number of morphing steps (default: 20)')
    image_parser.add_argument('--size', type=int, default=500, 
                             help='Size of output images (default: 500)')
    image_parser.add_argument('--no-plots', action='store_true', 
                             help='Disable visualization plots')
    image_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    # Movie transformation command
    movie_parser = subparsers.add_parser('movie', help='Apply diffeomorphic transformations to movies')
    movie_parser.add_argument('--input', '-i', required=True, help='Input image or video file')
    movie_parser.add_argument('--output', '-o', default='output_movie', help='Output directory')
    movie_parser.add_argument('--max-distortion', '-d', type=int, default=60, 
                             help='Maximum distortion (default: 60)')
    movie_parser.add_argument('--steps', '-s', type=int, default=20, 
                             help='Number of morphing steps (default: 20)')
    movie_parser.add_argument('--components', '-c', type=int, default=10, 
                             help='Number of components (default: 10)')
    movie_parser.add_argument('--no-video', action='store_true', 
                             help='Do not create a video from frames')
    movie_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    # Warpshift transformation command
    warpshift_parser = subparsers.add_parser('warpshift', 
                                           help='Apply diffeomorphic transformations with drifting warp field')
    warpshift_parser.add_argument('--input', '-i', required=True, help='Input image or video file')
    warpshift_parser.add_argument('--output', '-o', default='output_warpshift', help='Output directory')
    warpshift_parser.add_argument('--max-distortion', '-d', type=int, default=60, 
                                help='Maximum distortion (default: 60)')
    warpshift_parser.add_argument('--steps', '-s', type=int, default=20, 
                                help='Number of morphing steps (default: 20)')
    warpshift_parser.add_argument('--components', '-c', type=int, default=10, 
                                help='Number of components (default: 10)')
    warpshift_parser.add_argument('--phase-drift', '-p', type=float, default=0.39,
                                help='Phase drift amount (default: 0.39)')
    warpshift_parser.add_argument('--frames', '-f', type=int, default=10,
                                help='Number of frames to generate (default: 10)')
    warpshift_parser.add_argument('--frame-rate', '-r', type=int, default=30,
                                help='Simulated frame rate (default: 30)')
    warpshift_parser.add_argument('--no-video', action='store_true', 
                                help='Do not create a video from frames')
    warpshift_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    return parser.parse_args()

def run_diffeomorphic():
    """Run the diffeomorphic image transformation CLI"""
    args = parse_args()
    if args.command == 'image':
        logger = setup_logging(args.verbose)
        logger.info(f"Running image transformation on {args.input}")
        
        # Ensure output directory exists
        ensure_directory(args.output)
        
        # Run transformation
        result = transform_image(
            input_path=args.input,
            output_path=args.output,
            max_distortion=args.max_distortion,
            n_steps=args.steps,
            image_size=args.size,
            show_plots=not args.no_plots
        )
        
        logger.info(f"Transformation complete. {len(result)} images created.")
    else:
        print("Please specify a command: 'image'")
        sys.exit(1)

def run_diffeomorphic_movie():
    """Run the diffeomorphic movie transformation CLI"""
    args = parse_args()
    if args.command == 'movie':
        logger = setup_logging(args.verbose)
        logger.info(f"Running movie transformation on {args.input}")
        
        # Ensure output directory exists
        ensure_directory(args.output)
        
        # Run transformation
        result = transform_movie(
            input_path=args.input,
            output_path=args.output,
            max_distortion=args.max_distortion,
            n_steps=args.steps,
            n_comp=args.components,
            create_video=not args.no_video
        )
        
        if result['video']:
            logger.info(f"Video created: {result['video']}")
        logger.info(f"Transformation complete. {len(result['frames'])} frames created.")
    else:
        print("Please specify a command: 'movie'")
        sys.exit(1)

def run_diffeomorphic_movie_warpshift():
    """Run the diffeomorphic movie warpshift transformation CLI"""
    args = parse_args()
    if args.command == 'warpshift':
        logger = setup_logging(args.verbose)
        logger.info(f"Running warpshift transformation on {args.input}")
        
        # Ensure output directory exists
        ensure_directory(args.output)
        
        # Run transformation
        result = transform_warpshift(
            input_path=args.input,
            output_path=args.output,
            max_distortion=args.max_distortion,
            n_steps=args.steps,
            n_comp=args.components,
            phase_drift=args.phase_drift,
            num_frames=args.frames,
            frame_rate=args.frame_rate,
            create_video=not args.no_video
        )
        
        if result['video']:
            logger.info(f"Video created: {result['video']}")
        logger.info(f"Transformation complete. {len(result['frames'])} frames created.")
    else:
        print("Please specify a command: 'warpshift'")
        sys.exit(1)

if __name__ == "__main__":
    args = parse_args()
    if args.command == 'image':
        run_diffeomorphic()
    elif args.command == 'movie':
        run_diffeomorphic_movie()
    elif args.command == 'warpshift':
        run_diffeomorphic_movie_warpshift()
    else:
        print("Please specify a command: 'image', 'movie', or 'warpshift'")
        sys.exit(1)

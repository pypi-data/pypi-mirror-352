"""
Example script for using diffeomorphic to create warped videos.
"""
import os
import argparse
import diffeomorphic

def main():
    parser = argparse.ArgumentParser(description='Example of using diffeomorphic to create warped videos')
    parser.add_argument('--input', '-i', required=True, help='Input image or video file')
    parser.add_argument('--output', '-o', default='output_warpshift', help='Output directory')
    args = parser.parse_args()
    
    print(f"Creating warped video from {args.input} with diffeomorphic...")
    
    # Ensure output directory exists
    if not os.path.exists(args.output):
        os.makedirs(args.output)
    
    # Apply warpshift transformation
    diffeomorphic.transform_warpshift(
        input_path=args.input,
        output_path=args.output,
        max_distortion=60,
        n_steps=10,  # Using fewer steps for a quicker example
        num_frames=5  # Using fewer frames for a quicker example
    )
    
    print(f"Transformation complete. Results saved to {args.output}")

if __name__ == "__main__":
    main()

"""
Example script for using diffeomorphic to transform images.
"""
import os
import argparse
import diffeomorphic

def main():
    parser = argparse.ArgumentParser(description='Example of using diffeomorphic to transform an image')
    parser.add_argument('--input', '-i', required=True, help='Input image file')
    parser.add_argument('--output', '-o', default='output', help='Output directory')
    args = parser.parse_args()
    
    print(f"Transforming image {args.input} with diffeomorphic...")
    
    # Ensure output directory exists
    if not os.path.exists(args.output):
        os.makedirs(args.output)
    
    # Apply transformation
    diffeomorphic.transform_image(
        input_path=args.input,
        output_path=args.output,
        max_distortion=80,
        n_steps=10  # Using fewer steps for a quicker example
    )
    
    print(f"Transformation complete. Results saved to {args.output}")

if __name__ == "__main__":
    main()

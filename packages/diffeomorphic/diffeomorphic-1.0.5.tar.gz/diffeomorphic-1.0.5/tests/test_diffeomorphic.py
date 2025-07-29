"""
Unit tests for the diffeomorphic package.
"""
import unittest
import os
import shutil
import tempfile
import numpy as np
from PIL import Image

import diffeomorphic

class TestDiffeomorphic(unittest.TestCase):
    
    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        
        # Create a test image
        self.test_image_path = os.path.join(self.test_dir, 'test_image.jpg')
        img = Image.new('RGB', (100, 100), color=(255, 0, 0))
        img.save(self.test_image_path)
        
        # Create output directories
        self.output_dir = os.path.join(self.test_dir, 'output')
        os.makedirs(self.output_dir, exist_ok=True)
    
    def tearDown(self):
        # Remove the test directory
        shutil.rmtree(self.test_dir)
    
    def test_transform_image(self):
        """Test basic image transformation functionality"""
        # Run transformation with minimal settings for speed
        result = diffeomorphic.transform_image(
            input_path=self.test_image_path,
            output_path=self.output_dir,
            max_distortion=20,
            n_steps=2,
            show_plots=False
        )
        
        # Check that files were created
        files = os.listdir(self.output_dir)
        self.assertTrue(len(files) > 0, "No output files were created")
        
        # Check that at least one image file was created
        image_files = [f for f in files if f.endswith('.jpg')]
        self.assertTrue(len(image_files) > 0, "No image files were created")
        
        # Check that the result contains filenames
        self.assertTrue(isinstance(result, dict), "Result should be a dictionary")
    
    def test_transform_movie(self):
        """Test basic movie transformation functionality"""
        # Run transformation with minimal settings for speed
        result = diffeomorphic.transform_movie(
            input_path=self.test_image_path,
            output_path=self.output_dir,
            max_distortion=20,
            n_steps=2,
            n_comp=3
        )
        
        # Check that files were created
        files = os.listdir(self.output_dir)
        self.assertTrue(len(files) > 0, "No output files were created")
        
        # Check that the result contains filenames
        self.assertTrue(isinstance(result, list), "Result should be a list")
    
    def test_transform_warpshift(self):
        """Test basic warpshift transformation functionality"""
        # Run transformation with minimal settings for speed
        result = diffeomorphic.transform_warpshift(
            input_path=self.test_image_path,
            output_path=self.output_dir,
            max_distortion=20,
            n_steps=2,
            n_comp=3,
            num_frames=2
        )
        
        # Check that files were created
        files = os.listdir(self.output_dir)
        self.assertTrue(len(files) > 0, "No output files were created")
        
        # Check that the result contains filenames
        self.assertTrue(isinstance(result, list), "Result should be a list")

if __name__ == '__main__':
    unittest.main()

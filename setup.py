#!/usr/bin/env python3
"""
Setup script for Image Transformer

This script helps set up the environment and test the installation.
"""

import os
import sys
import subprocess
from pathlib import Path


def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install requirements: {e}")
        return False


def create_directories():
    """Create necessary directories"""
    print("Creating directories...")
    
    directories = ["input_images", "output_images"]
    
    for dir_name in directories:
        dir_path = Path(dir_name)
        dir_path.mkdir(exist_ok=True)
        print(f"✓ Created directory: {dir_name}")


def check_api_key():
    """Check if API key is configured"""
    print("Checking API key configuration...")
    
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        print("✓ GEMINI_API_KEY environment variable is set")
        return True
    else:
        print("⚠ GEMINI_API_KEY environment variable is not set")
        print("Please set your API key:")
        print("  export GEMINI_API_KEY='your_api_key_here'")
        print("Or provide it as a command line argument when running the script")
        return False


def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        from google import genai
        print("✓ google-genai imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import google-genai: {e}")
        return False
    
    try:
        from PIL import Image
        print("✓ Pillow imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Pillow: {e}")
        return False
    
    return True


def create_sample_images():
    """Create sample images for testing"""
    print("Creating sample images...")
    
    try:
        from PIL import Image, ImageDraw
        
        # Create a simple test image
        img = Image.new('RGB', (400, 300), color='lightblue')
        draw = ImageDraw.Draw(img)
        
        # Draw some shapes
        draw.rectangle([50, 50, 150, 150], fill='red', outline='black')
        draw.ellipse([200, 100, 350, 200], fill='yellow', outline='black')
        draw.text((160, 250), "Test Image", fill='black')
        
        # Save the test image
        sample_path = Path("input_images/sample_test.png")
        img.save(sample_path)
        print(f"✓ Created sample image: {sample_path}")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to create sample images: {e}")
        return False


def main():
    """Main setup function"""
    print("=" * 50)
    print("Image Transformer Setup")
    print("=" * 50)
    
    success = True
    
    # Install requirements
    if not install_requirements():
        success = False
    
    print()
    
    # Test imports
    if not test_imports():
        success = False
    
    print()
    
    # Create directories
    create_directories()
    
    print()
    
    # Create sample images
    create_sample_images()
    
    print()
    
    # Check API key
    api_key_set = check_api_key()
    
    print()
    print("=" * 50)
    
    if success and api_key_set:
        print("✓ Setup completed successfully!")
        print("\nYou can now run the image transformer:")
        print("  python src/image_transformer.py input_images/ output_images/")
    elif success:
        print("⚠ Setup completed with warnings")
        print("Please set your GEMINI_API_KEY before running the transformer")
    else:
        print("✗ Setup failed")
        print("Please fix the errors above and run setup again")
    
    print("=" * 50)


if __name__ == "__main__":
    main()

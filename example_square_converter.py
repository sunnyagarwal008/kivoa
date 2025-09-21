#!/usr/bin/env python3
"""
Example script demonstrating the convert_to_square function
Run this script to see how to convert images to square format
"""

import sys
from pathlib import Path
from PIL import Image

# Add src directory to path to import our modules
sys.path.append('src')

from image_helper import load_image, convert_to_square


def main():
    """
    Interactive example for converting images to square format
    """
    print("=== Image to Square Converter Example ===\n")
    
    # Get input image path from user or use default
    if len(sys.argv) > 1:
        input_path = Path(sys.argv[1])
    else:
        # Prompt user for image path
        input_str = input("Enter the path to your image file (or press Enter for 'sample.jpg'): ").strip()
        input_path = Path(input_str) if input_str else Path("sample.jpg")
    
    # Check if file exists
    if not input_path.exists():
        print(f"❌ Error: File '{input_path}' not found.")
        print("\nTo use this script:")
        print("1. Place an image file in the current directory and name it 'sample.jpg'")
        print("2. Or run: python example_square_converter.py path/to/your/image.jpg")
        return
    
    try:
        # Load the image
        print(f"📁 Loading image: {input_path}")
        image = load_image(input_path)
        
        if image is None:
            print("❌ Failed to load image")
            return
        
        width, height = image.size
        print(f"📏 Original image size: {width}x{height}")
        
        # Check if already square
        if width == height:
            print("✅ Image is already square!")
        else:
            aspect_ratio = width / height
            print(f"📐 Current aspect ratio: {aspect_ratio:.2f}:1")
        
        print("\n" + "="*50)
        print("Converting image using different methods...")
        print("="*50)
        
        # Create output directory
        output_dir = input_path.parent / "square_outputs"
        output_dir.mkdir(exist_ok=True)
        
        methods = [
            {
                'name': 'Padding (White Background)',
                'method': 'pad',
                'background_color': (255, 255, 255),
                'suffix': 'padded_white'
            },
            {
                'name': 'Padding (Black Background)',
                'method': 'pad',
                'background_color': (0, 0, 0),
                'suffix': 'padded_black'
            },
            {
                'name': 'Center Crop',
                'method': 'crop',
                'background_color': None,
                'suffix': 'cropped'
            },
            {
                'name': 'Stretch/Distort',
                'method': 'stretch',
                'background_color': None,
                'suffix': 'stretched'
            }
        ]
        
        results = []
        
        for i, config in enumerate(methods, 1):
            print(f"\n{i}. {config['name']}:")
            print(f"   Method: {config['method']}")
            
            # Convert image
            if config['background_color']:
                square_image = convert_to_square(
                    image, 
                    method=config['method'], 
                    background_color=config['background_color']
                )
            else:
                square_image = convert_to_square(image, method=config['method'])
            
            # Save result
            output_path = output_dir / f"{input_path.stem}_{config['suffix']}.jpg"
            square_image.save(output_path, quality=95)
            
            new_width, new_height = square_image.size
            print(f"   ✅ Saved: {output_path}")
            print(f"   📏 New size: {new_width}x{new_height}")
            
            results.append({
                'name': config['name'],
                'path': output_path,
                'size': (new_width, new_height)
            })
        
        # Summary
        print("\n" + "="*50)
        print("🎉 CONVERSION COMPLETE!")
        print("="*50)
        print(f"📁 Output directory: {output_dir}")
        print("\nGenerated files:")
        
        for result in results:
            print(f"  • {result['name']}: {result['path'].name}")
            print(f"    Size: {result['size'][0]}x{result['size'][1]}")
        
        print(f"\n💡 Tips:")
        print(f"   • Use 'pad' to preserve all image content")
        print(f"   • Use 'crop' for best quality but may lose edges")
        print(f"   • Use 'stretch' to keep all content but may distort")
        
    except Exception as e:
        print(f"❌ Error processing image: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

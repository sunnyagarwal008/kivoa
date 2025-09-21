from pathlib import Path
import logging
from pathlib import Path
from typing import Optional

from PIL import Image

from config import (
    SUPPORTED_FORMATS, LOG_LEVEL, LOG_FORMAT
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT
)
logger = logging.getLogger(__name__)


def is_valid_image(file_path: Path) -> bool:
    """
    Check if file is a valid image

    Args:
        file_path: Path to the file

    Returns:
        True if valid image, False otherwise
    """
    return file_path.suffix.lower() in SUPPORTED_FORMATS


def load_image(image_path: Path) -> Optional[Image.Image]:
    """
    Load and validate an image

    Args:
        image_path: Path to the image file

    Returns:
        PIL Image object or None if failed
    """
    try:
        image = Image.open(image_path)
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        logger.info(f"Successfully loaded image: {image_path.name}")
        return image
    except Exception as e:
        logger.error(f"Failed to load image {image_path}: {e}")
        raise e


def convert_to_square(image: Image.Image, method: str = 'pad', background_color: tuple = (255, 255, 255)) -> Image.Image:
    """
    Convert an image to a square format with aspect ratio 1:1

    Args:
        image: PIL Image object to convert
        method: Method to use for conversion ('pad', 'crop', 'stretch')
            - 'pad': Add padding to make square (preserves aspect ratio)
            - 'crop': Crop to square from center (may lose content)
            - 'stretch': Stretch to square (distorts image)
        background_color: RGB tuple for padding color (default: white)

    Returns:
        PIL Image object with 1:1 aspect ratio
    """
    if not isinstance(image, Image.Image):
        raise ValueError("Input must be a PIL Image object")

    width, height = image.size

    # If already square, return copy
    if width == height:
        logger.info("Image is already square")
        return image.copy()

    if method == 'pad':
        # Add padding to make square
        max_dimension = max(width, height)

        # Create new square image with background color
        square_image = Image.new('RGB', (max_dimension, max_dimension), background_color)

        # Calculate position to center the original image
        x_offset = (max_dimension - width) // 2
        y_offset = (max_dimension - height) // 2

        # Paste original image onto square background
        square_image.paste(image, (x_offset, y_offset))

        logger.info(f"Converted image to square using padding: {width}x{height} -> {max_dimension}x{max_dimension}")
        return square_image

    elif method == 'crop':
        # Crop to square from center
        min_dimension = min(width, height)

        # Calculate crop box to center the crop
        left = (width - min_dimension) // 2
        top = (height - min_dimension) // 2
        right = left + min_dimension
        bottom = top + min_dimension

        square_image = image.crop((left, top, right, bottom))

        logger.info(f"Converted image to square using cropping: {width}x{height} -> {min_dimension}x{min_dimension}")
        return square_image

    elif method == 'stretch':
        # Stretch to square (may distort)
        target_size = max(width, height)  # Use larger dimension to avoid quality loss
        square_image = image.resize((target_size, target_size), Image.Resampling.LANCZOS)

        logger.info(f"Converted image to square using stretching: {width}x{height} -> {target_size}x{target_size}")
        return square_image

    else:
        raise ValueError(f"Invalid method '{method}'. Must be 'pad', 'crop', or 'stretch'")


def main():
    """
    Sample main method demonstrating the convert_to_square function
    """
    import sys

    # Sample usage - you can modify these paths
    input_image_path = Path("sample_input.jpg")  # Change this to your input image path

    # Check if input image exists
    if not input_image_path.exists():
        print(f"Error: Input image '{input_image_path}' not found.")
        print("Please update the input_image_path variable with a valid image path.")
        return

    try:
        # Load the image
        print(f"Loading image: {input_image_path}")
        image = load_image(input_image_path)

        if image is None:
            print("Failed to load image")
            return

        print(f"Original image size: {image.size[0]}x{image.size[1]}")

        # Method 1: Convert using padding (default)
        print("\n1. Converting using padding method...")
        square_padded = convert_to_square(image, method='pad')
        output_path_pad = input_image_path.parent / f"{input_image_path.stem}_square_padded.jpg"
        square_padded.save(output_path_pad)
        print(f"Saved padded square image: {output_path_pad}")
        print(f"New size: {square_padded.size[0]}x{square_padded.size[1]}")

        # Method 2: Convert using cropping
        print("\n2. Converting using cropping method...")
        square_cropped = convert_to_square(image, method='crop')
        output_path_crop = input_image_path.parent / f"{input_image_path.stem}_square_cropped.jpg"
        square_cropped.save(output_path_crop)
        print(f"Saved cropped square image: {output_path_crop}")
        print(f"New size: {square_cropped.size[0]}x{square_cropped.size[1]}")

        # Method 3: Convert using stretching
        print("\n3. Converting using stretching method...")
        square_stretched = convert_to_square(image, method='stretch')
        output_path_stretch = input_image_path.parent / f"{input_image_path.stem}_square_stretched.jpg"
        square_stretched.save(output_path_stretch)
        print(f"Saved stretched square image: {output_path_stretch}")
        print(f"New size: {square_stretched.size[0]}x{square_stretched.size[1]}")

        # Method 4: Convert using padding with custom background color (black)
        print("\n4. Converting using padding with black background...")
        square_black_bg = convert_to_square(image, method='pad', background_color=(0, 0, 0))
        output_path_black = input_image_path.parent / f"{input_image_path.stem}_square_black_bg.jpg"
        square_black_bg.save(output_path_black)
        print(f"Saved square image with black background: {output_path_black}")
        print(f"New size: {square_black_bg.size[0]}x{square_black_bg.size[1]}")

        print(f"\nAll conversions completed successfully!")
        print("Output files created:")
        print(f"  - {output_path_pad}")
        print(f"  - {output_path_crop}")
        print(f"  - {output_path_stretch}")
        print(f"  - {output_path_black}")

    except Exception as e:
        print(f"Error processing image: {e}")
        logger.error(f"Error in main: {e}")


if __name__ == "__main__":
    main()


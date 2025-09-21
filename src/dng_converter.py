"""
DNG to PNG Converter

This module provides functionality to convert DNG (Digital Negative) files
to compressed PNG format using rawpy and PIL libraries.
"""

import os
from pathlib import Path

import rawpy
from PIL import Image
from typing import Optional, Tuple

from image_helper import load_image, convert_to_square


def convert_dng_to_png(
    dng_path: str,
    output_path: Optional[str] = None,
    compression_level: int = 8,
    resize: Optional[Tuple[int, int]] = None,
    gamma: float = 2.2
) -> str:
    """
    Convert a DNG file to a compressed PNG file.

    Args:
        dng_path (str): Path to the input DNG file
        output_path (str, optional): Path for the output PNG file.
                                   If None, uses the same name as input with .png extension
        compression_level (int): PNG compression level (0-9, where 9 is maximum compression)
        quality (int): Image quality for processing (0-100)
        resize (tuple, optional): Target size as (width, height) for resizing
        gamma (float): Gamma correction value

    Returns:
        str: Path to the created PNG file

    Raises:
        FileNotFoundError: If the input DNG file doesn't exist
        ValueError: If compression_level is not between 0-9
        Exception: For other processing errors
    """
    
    # Validate inputs
    if not os.path.exists(dng_path):
        raise FileNotFoundError(f"DNG file not found: {dng_path}")
    
    if not (0 <= compression_level <= 9):
        raise ValueError("Compression level must be between 0 and 9")

    
    # Generate output path if not provided
    if output_path is None:
        base_name = os.path.splitext(os.path.basename(dng_path))[0]
        output_dir = os.path.dirname(dng_path)
        output_path = os.path.join(output_dir, f"{base_name}.png")
    
    try:
        # Read and process the DNG file
        with rawpy.imread(dng_path) as raw:
            # Process the raw image with specified parameters
            rgb_array = raw.postprocess(
                gamma=(gamma, 1.0),
                use_camera_wb=True,
                half_size=False,
                no_auto_bright=False,
                output_color=rawpy.ColorSpace.sRGB,
                output_bps=8
            )
        
        # Convert numpy array to PIL Image
        image = Image.fromarray(rgb_array)
        
        # Resize if requested
        if resize:
            image = image.resize(resize, Image.Resampling.LANCZOS)
        
        # Save as compressed PNG
        image.save(
            output_path,
            format='PNG',
            compress_level=compression_level,
            optimize=True
        )
        
        print(f"Successfully converted {dng_path} to {output_path}")
        return output_path
        
    except Exception as e:
        raise Exception(f"Error converting DNG to PNG: {str(e)}")


def batch_convert_dng_to_png(
    input_directory: str,
    output_directory: Optional[str] = None,
    **kwargs
) -> list:
    """
    Convert all DNG files in a directory to PNG format.
    
    Args:
        input_directory (str): Directory containing DNG files
        output_directory (str, optional): Directory for output PNG files.
                                        If None, uses the same as input directory
        **kwargs: Additional arguments passed to convert_dng_to_png
    
    Returns:
        list: List of paths to created PNG files
        
    Raises:
        FileNotFoundError: If input directory doesn't exist
    """
    
    if not os.path.exists(input_directory):
        raise FileNotFoundError(f"Input directory not found: {input_directory}")
    
    if output_directory is None:
        output_directory = input_directory
    
    # Create output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)
    
    converted_files = []
    dng_files = [f for f in os.listdir(input_directory) if f.lower().endswith('.dng')]
    
    if not dng_files:
        print(f"No DNG files found in {input_directory}")
        return converted_files
    
    print(f"Found {len(dng_files)} DNG files to convert...")
    
    for dng_file in dng_files:
        try:
            input_path = os.path.join(input_directory, dng_file)
            base_name = os.path.splitext(dng_file)[0]
            output_path = os.path.join(output_directory, f"{base_name}_raw.png")
            convert_dng_to_png(input_path, output_path, **kwargs)

            output_image = load_image(Path(output_path))
            output_image_square = convert_to_square(output_image, method='crop')
            final_output_path = os.path.join(output_directory, f"{base_name}.png")
            output_image_square.save(final_output_path)

            converted_files.append(final_output_path)
            
        except Exception as ex:
            print(f"Failed to convert {dng_file}: {str(ex)}")
            raise ex
    
    print(f"Successfully converted {len(converted_files)} out of {len(dng_files)} files")
    return converted_files


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python dng_converter.py <input_path> [output_path]")
        sys.exit(1)
    
    input_directory = sys.argv[1]
    output_directory = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        result = batch_convert_dng_to_png(input_directory, output_directory)
        print(f"Conversion completed: {result}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

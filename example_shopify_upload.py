#!/usr/bin/env python3
"""
Example script showing how to use the Shopify Media Uploader

This script demonstrates different ways to use the ShopifyImageUploader class
to upload product images and videos to your Shopify store.
"""

import os
from pathlib import Path
from src.shopify_image_uploader import ShopifyImageUploader
from src.config import SHOPIFY_API_KEY, SHOPIFY_SECRET_KEY, SHOPIFY_STORE_URL

def example_basic_upload():
    """Basic example of uploading media files (images and videos) from a folder"""
    
    # Initialize the uploader
    uploader = ShopifyImageUploader(
        shop_url=SHOPIFY_STORE_URL,
        api_key=SHOPIFY_API_KEY,
        access_token=SHOPIFY_SECRET_KEY
    )
    
    # Specify the folder containing your product media files
    media_folder = Path("./product_media")  # Change this to your actual folder

    # Create sample folder structure for demonstration
    if not media_folder.exists():
        media_folder.mkdir()
        print(f"Created sample folder: {media_folder}")
        print("Add your product media files to this folder with filenames like:")
        print("  Images:")
        print("    - product_123_main.jpg")
        print("    - 456_variant_01.png")
        print("    - SKU_789_photo.jpeg")
        print("  Videos:")
        print("    - product_123_demo.mp4")
        print("    - 456_showcase.mp4")
        print("    - SKU_789_video.mp4")
        return
    
    # Process all media files in the folder
    print(f"Processing media files in: {media_folder}")
    results = uploader.process_folder(media_folder, dry_run=True)  # Set dry_run=False to actually upload
    
    # Print results
    print(f"\nResults:")
    print(f"  Total files: {results['total_files']}")
    print(f"  Valid images: {results['valid_images']}")
    print(f"  Successful uploads: {results['successful_uploads']}")
    print(f"  Failed uploads: {results['failed_uploads']}")
    print(f"  Skipped files: {results['skipped_files']}")

def example_single_media_upload():
    """Example of uploading a single media file to a specific product"""
    
    uploader = ShopifyImageUploader(
        shop_url=SHOPIFY_STORE_URL,
        api_key=SHOPIFY_API_KEY,
        access_token=SHOPIFY_SECRET_KEY
    )
    
    # Upload a single media file to a specific product
    product_id = "123456789"  # Replace with actual product ID

    # Example with image
    image_path = Path("./product_media/sample_image.jpg")  # Replace with actual image path
    if image_path.exists():
        success = uploader.upload_media_to_product(
            product_id=product_id,
            media_path=image_path,
            alt_text="Product main image"
        )

        if success:
            print(f"Successfully uploaded image {image_path.name} to product {product_id}")
        else:
            print(f"Failed to upload image {image_path.name}")
    else:
        print(f"Image file not found: {image_path}")

    # Example with video
    video_path = Path("./product_media/sample_video.mp4")  # Replace with actual video path
    if video_path.exists():
        success = uploader.upload_media_to_product(
            product_id=product_id,
            media_path=video_path,
            alt_text="Product demo video"
        )

        if success:
            print(f"Successfully uploaded video {video_path.name} to product {product_id}")
        else:
            print(f"Failed to upload video {video_path.name}")
    else:
        print(f"Video file not found: {video_path}")

def example_filename_patterns():
    """Example showing different filename patterns that work"""
    
    uploader = ShopifyImageUploader(
        shop_url=SHOPIFY_STORE_URL,
        api_key=SHOPIFY_API_KEY,
        access_token=SHOPIFY_SECRET_KEY
    )
    
    # Test different filename patterns for both images and videos
    test_filenames = [
        "product_123_main.jpg",      # Pattern: product_ID (image)
        "456_variant_01.png",        # Pattern: ID_ (image)
        "SKU_789_photo.jpeg",        # Pattern: SKU_ID (image)
        "ID_999_image.jpg",          # Pattern: ID_ID (image)
        "1234567890.png",            # Pattern: long number (image)
        "item-555-front.jpg",        # Pattern: -ID- (image)
        "photo_product_888.jpg",     # Pattern: _ID (image)
        "product_123_demo.mp4",      # Pattern: product_ID (video)
        "456_showcase.mp4",          # Pattern: ID_ (video)
        "SKU_789_video.mp4",         # Pattern: SKU_ID (video)
        "ID_999_promo.mp4",          # Pattern: ID_ID (video)
    ]
    
    print("Testing filename patterns:")
    for filename in test_filenames:
        product_id = uploader.extract_product_id_from_filename(filename)
        print(f"  {filename:<25} -> Product ID: {product_id}")

def main():
    """Run examples"""
    print("Shopify Image Uploader Examples")
    print("=" * 40)
    
    try:
        print("\n1. Testing filename patterns:")
        example_filename_patterns()
        
        print("\n2. Basic folder upload (dry run):")
        example_basic_upload()
        
        print("\n3. Single media upload example:")
        example_single_media_upload()
        
    except Exception as e:
        print(f"Error running examples: {e}")
        print("\nMake sure to:")
        print("1. Update SHOPIFY_STORE_URL in src/config.py")
        print("2. Verify your API credentials")
        print("3. Install required packages: pip install -r requirements.txt")

if __name__ == "__main__":
    main()

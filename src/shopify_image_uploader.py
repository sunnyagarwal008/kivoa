#!/usr/bin/env python3
"""
Shopify Product Media Uploader

This script scans a folder for media files (images and videos) and uploads them as product media to Shopify.
The product ID is extracted from the filename using configurable patterns.

Supported formats:
    - Images: JPG, JPEG, PNG, BMP, GIF, TIFF, WebP
    - Videos: MP4

Usage:
    python src/shopify_image_uploader.py /path/to/media/folder

Filename patterns supported:
    - product_123_image.jpg -> Product ID: 123
    - 456-variant-01.mp4 -> Product ID: 456
    - SKU_789_photo.jpeg -> Product ID: 789
    - Custom patterns can be configured in the script
"""

import os
import re
import sys
import logging
import argparse
from pathlib import Path
from typing import List, Optional, Dict, Any
import mimetypes

import shopify
import requests
from PIL import Image

from config import SHOPIFY_API_KEY, SHOPIFY_SECRET_KEY, SUPPORTED_FORMATS

# Supported video formats
SUPPORTED_VIDEO_FORMATS = {'.mp4'}
ALL_SUPPORTED_FORMATS = SUPPORTED_FORMATS | SUPPORTED_VIDEO_FORMATS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ShopifyImageUploader:
    """Handles uploading images and videos to Shopify products"""

    def __init__(self, shop_url: str, api_key: str, secret_key: str):
        """
        Initialize Shopify connection

        Args:
            shop_url: Your Shopify store URL (e.g., 'your-store.myshopify.com')
            api_key: Shopify API key
            secret_key: Shopify secret key
        """
        self.shop_url = shop_url
        self.api_key = api_key
        self.secret_key = secret_key

        # Configure Shopify session
        shopify.ShopifyResource.set_site(f"https://{api_key}:{secret_key}@{shop_url}/admin/api/2023-10")

        # Test connection
        try:
            shop = shopify.Shop.current()
            logger.info(f"Connected to Shopify store: {shop.name}")
        except Exception as e:
            logger.error(f"Failed to connect to Shopify: {e}")
            raise

    def extract_product_id_from_filename(self, filename: str) -> Optional[str]:
        """
        Extract product ID from filename using various patterns

        Args:
            filename: The image filename

        Returns:
            Product ID as string, or None if not found
        """
        # Define patterns to match product IDs in filenames
        patterns = [
            r'product[_-](\d+)',           # product_123 or product-123
            r'(\d+)[_-]',                  # 123_ or 123-
            r'[_-](\d+)[_-]',             # _123_ or -123-
            r'SKU[_-](\d+)',              # SKU_123 or SKU-123
            r'ID[_-](\d+)',               # ID_123 or ID-123
            r'^(\d+)',                     # Starting with digits
            r'(\d{6,})',                   # 6 or more consecutive digits
        ]

        filename_lower = filename.lower()

        for pattern in patterns:
            match = re.search(pattern, filename_lower)
            if match:
                product_id = match.group(1)
                logger.debug(f"Extracted product ID '{product_id}' from '{filename}' using pattern '{pattern}'")
                return product_id

        logger.warning(f"Could not extract product ID from filename: {filename}")
        return None

    def get_product(self, product_id: str) -> Optional[shopify.Product]:
        """
        Get product by ID from Shopify

        Args:
            product_id: The product ID

        Returns:
            Shopify Product object or None if not found
        """
        try:
            product = shopify.Product.find(product_id)
            logger.info(f"Found product: {product.title} (ID: {product_id})")
            return product
        except Exception as e:
            logger.error(f"Product with ID {product_id} not found: {e}")
            return None

    def upload_media_to_product(self, product_id: str, media_path: Path, alt_text: str = None) -> bool:
        """
        Upload an image or video to a Shopify product

        Args:
            product_id: The product ID
            media_path: Path to the media file (image or video)
            alt_text: Alternative text for the media

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get the product
            product = self.get_product(product_id)
            if not product:
                return False

            # Validate media file
            if not self.is_valid_media(media_path):
                logger.error(f"Invalid media file: {media_path}")
                return False

            # Check if it's a video or image
            is_video = media_path.suffix.lower() in SUPPORTED_VIDEO_FORMATS

            if is_video:
                return self._upload_video_to_product(product, media_path, alt_text)
            else:
                return self._upload_image_to_product(product, media_path, alt_text)

        except Exception as e:
            logger.error(f"Error uploading media {media_path} to product {product_id}: {e}")
            return False

    def _upload_image_to_product(self, product: shopify.Product, image_path: Path, alt_text: str = None) -> bool:
        """
        Upload an image to a Shopify product using the Image API

        Args:
            product: Shopify Product object
            image_path: Path to the image file
            alt_text: Alternative text for the image

        Returns:
            True if successful, False otherwise
        """
        try:
            # Read image data
            with open(image_path, 'rb') as f:
                image_data = f.read()

            # Create image object
            image = shopify.Image()
            image.product_id = product.id
            image.attachment = image_data
            image.filename = image_path.name

            if alt_text:
                image.alt = alt_text
            else:
                image.alt = f"Product image for {product.title}"

            # Upload the image
            if image.save():
                logger.info(f"Successfully uploaded image {image_path.name} to product {product.id}")
                return True
            else:
                logger.error(f"Failed to upload image {image_path.name}: {image.errors.full_messages()}")
                return False

        except Exception as e:
            logger.error(f"Error uploading image {image_path}: {e}")
            return False

    def upload_image_to_product(self, product_id: str, image_path: Path, alt_text: str = None) -> bool:
        """
        Backward compatibility method for uploading images

        Args:
            product_id: The product ID
            image_path: Path to the image file
            alt_text: Alternative text for the image

        Returns:
            True if successful, False otherwise
        """
        return self.upload_media_to_product(product_id, image_path, alt_text)

    def _upload_video_to_product(self, product: shopify.Product, video_path: Path, alt_text: str = None) -> bool:
        """
        Upload a video to a Shopify product using the GraphQL API

        Args:
            product: Shopify Product object
            video_path: Path to the video file
            alt_text: Alternative text for the video

        Returns:
            True if successful, False otherwise
        """
        try:
            # For videos, we need to use Shopify's GraphQL API
            # First, we need to create a staged upload
            staged_upload_mutation = """
            mutation stagedUploadsCreate($input: [StagedUploadInput!]!) {
                stagedUploadsCreate(input: $input) {
                    stagedTargets {
                        url
                        resourceUrl
                        parameters {
                            name
                            value
                        }
                    }
                    userErrors {
                        field
                        message
                    }
                }
            }
            """

            # Get file size
            file_size = video_path.stat().st_size

            # Create staged upload
            variables = {
                "input": [{
                    "resource": "VIDEO",
                    "filename": video_path.name,
                    "mimeType": "video/mp4",
                    "httpMethod": "POST",
                    "fileSize": str(file_size)
                }]
            }

            # Execute GraphQL mutation to create staged upload
            response = self._execute_graphql_query(staged_upload_mutation, variables)

            if not response or 'data' not in response:
                logger.error(f"Failed to create staged upload for video {video_path.name}")
                return False

            staged_targets = response['data']['stagedUploadsCreate']['stagedTargets']
            if not staged_targets:
                logger.error(f"No staged targets returned for video {video_path.name}")
                return False

            staged_target = staged_targets[0]
            upload_url = staged_target['url']
            resource_url = staged_target['resourceUrl']

            # Upload the video file to the staged URL
            if not self._upload_file_to_staged_url(video_path, upload_url, staged_target['parameters']):
                return False

            # Create the product media using the uploaded file
            create_media_mutation = """
            mutation productCreateMedia($media: [CreateMediaInput!]!, $productId: ID!) {
                productCreateMedia(media: $media, productId: $productId) {
                    media {
                        id
                        mediaContentType
                        status
                    }
                    mediaUserErrors {
                        field
                        message
                    }
                    product {
                        id
                    }
                }
            }
            """

            media_variables = {
                "productId": f"gid://shopify/Product/{product.id}",
                "media": [{
                    "originalSource": resource_url,
                    "mediaContentType": "VIDEO",
                    "alt": alt_text or f"Product video for {product.title}"
                }]
            }

            # Execute GraphQL mutation to create media
            media_response = self._execute_graphql_query(create_media_mutation, media_variables)

            if media_response and 'data' in media_response:
                media_errors = media_response['data']['productCreateMedia']['mediaUserErrors']
                if not media_errors:
                    logger.info(f"Successfully uploaded video {video_path.name} to product {product.id}")
                    return True
                else:
                    logger.error(f"Failed to create media for video {video_path.name}: {media_errors}")
                    return False
            else:
                logger.error(f"Failed to create media for video {video_path.name}")
                return False

        except Exception as e:
            logger.error(f"Error uploading video {video_path}: {e}")
            return False

    def is_valid_media(self, media_path: Path) -> bool:
        """
        Check if file is a valid image or video

        Args:
            media_path: Path to the media file

        Returns:
            True if valid media file, False otherwise
        """
        # Check file extension
        if media_path.suffix.lower() not in ALL_SUPPORTED_FORMATS:
            return False

        # Check if file exists and is readable
        if not media_path.exists() or not media_path.is_file():
            return False

        # For images, try to open with PIL to validate
        if media_path.suffix.lower() in SUPPORTED_FORMATS:
            try:
                with Image.open(media_path) as img:
                    img.verify()
                return True
            except Exception as e:
                logger.error(f"Invalid image file {media_path}: {e}")
                return False

        # For videos, just check if it's a readable file
        elif media_path.suffix.lower() in SUPPORTED_VIDEO_FORMATS:
            try:
                # Basic validation - check if file is readable and has content
                if media_path.stat().st_size > 0:
                    return True
                else:
                    logger.error(f"Video file is empty: {media_path}")
                    return False
            except Exception as e:
                logger.error(f"Invalid video file {media_path}: {e}")
                return False

        return False

    def _execute_graphql_query(self, query: str, variables: dict = None) -> dict:
        """
        Execute a GraphQL query against Shopify's API

        Args:
            query: GraphQL query string
            variables: Query variables

        Returns:
            Response dictionary
        """
        try:
            url = f"https://{self.shop_url}/admin/api/2023-10/graphql.json"
            headers = {
                'Content-Type': 'application/json',
                'X-Shopify-Access-Token': self.secret_key
            }

            payload = {
                'query': query,
                'variables': variables or {}
            }

            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()

            return response.json()

        except Exception as e:
            logger.error(f"GraphQL query failed: {e}")
            return {}

    def _upload_file_to_staged_url(self, file_path: Path, upload_url: str, parameters: list) -> bool:
        """
        Upload a file to Shopify's staged upload URL

        Args:
            file_path: Path to the file to upload
            upload_url: Staged upload URL
            parameters: Upload parameters from Shopify

        Returns:
            True if successful, False otherwise
        """
        try:
            # Prepare form data
            form_data = {}
            for param in parameters:
                form_data[param['name']] = param['value']

            # Add the file
            with open(file_path, 'rb') as f:
                files = {'file': (file_path.name, f, 'video/mp4')}

                response = requests.post(upload_url, data=form_data, files=files)
                response.raise_for_status()

                logger.info(f"Successfully uploaded {file_path.name} to staged URL")
                return True

        except Exception as e:
            logger.error(f"Failed to upload {file_path.name} to staged URL: {e}")
            return False

    def process_folder(self, folder_path: Path, dry_run: bool = False) -> Dict[str, Any]:
        """
        Process all media files (images and videos) in a folder and upload them to Shopify

        Args:
            folder_path: Path to the folder containing media files
            dry_run: If True, only simulate the process without uploading

        Returns:
            Dictionary with processing results
        """
        results = {
            'total_files': 0,
            'valid_images': 0,
            'successful_uploads': 0,
            'failed_uploads': 0,
            'skipped_files': 0,
            'errors': []
        }

        if not folder_path.exists() or not folder_path.is_dir():
            error_msg = f"Folder does not exist or is not a directory: {folder_path}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
            return results

        # Get all media files in the folder
        media_files = []
        for file_path in folder_path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in ALL_SUPPORTED_FORMATS:
                media_files.append(file_path)

        results['total_files'] = len(media_files)
        logger.info(f"Found {len(media_files)} media files in {folder_path}")

        # Process each media file
        for media_path in media_files:
            try:
                logger.info(f"Processing: {media_path.name}")

                # Extract product ID from filename
                product_id = self.extract_product_id_from_filename(media_path.name)
                if not product_id:
                    results['skipped_files'] += 1
                    continue

                # Validate media file
                if not self.is_valid_media(media_path):
                    results['skipped_files'] += 1
                    continue

                results['valid_images'] += 1

                # Determine media type
                media_type = "video" if media_path.suffix.lower() in SUPPORTED_VIDEO_FORMATS else "image"

                if dry_run:
                    logger.info(f"DRY RUN: Would upload {media_type} {media_path.name} to product {product_id}")
                    results['successful_uploads'] += 1
                else:
                    # Upload media to Shopify
                    if self.upload_media_to_product(product_id, media_path):
                        results['successful_uploads'] += 1
                    else:
                        results['failed_uploads'] += 1

            except Exception as e:
                error_msg = f"Error processing {media_path.name}: {e}"
                logger.error(error_msg)
                results['errors'].append(error_msg)
                results['failed_uploads'] += 1

        return results


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Upload media files (images and videos) as product media to Shopify",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python src/shopify_image_uploader.py /path/to/media --shop your-store.myshopify.com
    python src/shopify_image_uploader.py ./product_media --dry-run
    python src/shopify_image_uploader.py ./media --shop store.myshopify.com --verbose

Supported formats:
    Images: JPG, JPEG, PNG, BMP, GIF, TIFF, WebP
    Videos: MP4
        """
    )

    parser.add_argument(
        'folder_path',
        type=str,
        help='Path to folder containing product media files (images and videos)'
    )

    parser.add_argument(
        '--shop',
        type=str,
        help='Shopify store URL (e.g., your-store.myshopify.com)'
    )

    parser.add_argument(
        '--api-key',
        type=str,
        help='Shopify API key (overrides config.py)'
    )

    parser.add_argument(
        '--secret-key',
        type=str,
        help='Shopify secret key (overrides config.py)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulate the process without actually uploading media files'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Get configuration
    api_key = args.api_key or SHOPIFY_API_KEY
    secret_key = args.secret_key or SHOPIFY_SECRET_KEY

    if not api_key or not secret_key:
        logger.error("Shopify API key and secret key are required")
        logger.error("Provide them via --api-key and --secret-key arguments or set them in config.py")
        sys.exit(1)

    if not args.shop:
        logger.error("Shopify store URL is required (--shop argument)")
        logger.error("Example: --shop your-store.myshopify.com")
        sys.exit(1)

    # Initialize uploader
    try:
        uploader = ShopifyImageUploader(args.shop, api_key, secret_key)
    except Exception as e:
        logger.error(f"Failed to initialize Shopify connection: {e}")
        sys.exit(1)

    # Process folder
    folder_path = Path(args.folder_path)

    if args.dry_run:
        logger.info("DRY RUN MODE - No media files will be uploaded")

    results = uploader.process_folder(folder_path, dry_run=args.dry_run)

    # Print results
    print("\n" + "="*50)
    print("UPLOAD RESULTS")
    print("="*50)
    print(f"Total files found: {results['total_files']}")
    print(f"Valid images: {results['valid_images']}")
    print(f"Successful uploads: {results['successful_uploads']}")
    print(f"Failed uploads: {results['failed_uploads']}")
    print(f"Skipped files: {results['skipped_files']}")

    if results['errors']:
        print(f"\nErrors ({len(results['errors'])}):")
        for error in results['errors']:
            print(f"  - {error}")

    print("="*50)

    if results['failed_uploads'] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
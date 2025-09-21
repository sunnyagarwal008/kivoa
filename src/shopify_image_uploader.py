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

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any

import requests
import shopify
from PIL import Image

from config import ADMIN_API_ACCESS_TOKEN, SHOPIFY_STORE_URL, SUPPORTED_FORMATS

# Supported video formats
SUPPORTED_VIDEO_FORMATS = {'.mp4'}
ALL_SUPPORTED_FORMATS = SUPPORTED_FORMATS | SUPPORTED_VIDEO_FORMATS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def is_valid_media(media_path: Path) -> bool:
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


class ShopifyImageUploader:
    """Handles uploading images and videos to Shopify products"""

    def __init__(self, shop_url: str, access_token: str):
        """
        Initialize Shopify connection

        Args:
            shop_url: Your Shopify store URL (e.g., 'your-store.myshopify.com')
            api_key: Shopify API key
            access_token: Shopify secret key
        """
        self.shop_url = shop_url
        self.access_token = access_token

        # Configure Shopify session
        self.session = shopify.Session(shop_url, "2024-07", access_token)
        shopify.ShopifyResource.activate_session(self.session)

        # Test connection
        try:
            shop = shopify.Shop.current()
            logger.info(f"Connected to Shopify store: {shop.name}")
        except Exception as e:
            logger.error(f"Failed to connect to Shopify: {e}")
            raise e

    def extract_product_id_from_filename(self, filename: str) -> Optional[str]:
        """
        Extract product ID from filename by extracting SKU and looking it up in Shopify

        Args:
            filename: The image filename (e.g., "NK-00001-0825-02.jpg")

        Returns:
            Product ID as string, or None if not found
        """
        try:
            # Extract SKU from filename
            # Example: "NK-00001-0825-02.jpg" -> "NK-00001-0825"
            name_without_ext = filename.rsplit('.', 1)[0]  # NK-00001-0825-02

            # Split on dashes
            parts = name_without_ext.split('-')  # ['NK', '00001', '0825', '02']

            # Join the first three parts to get the SKU
            if len(parts) >= 3:
                sku = '-'.join(parts[:3])  # NK-00001-0825
            else:
                logger.warning(f"Filename {filename} doesn't match expected SKU pattern")
                return None

            logger.info(f"Extracted SKU '{sku}' from filename '{filename}'")

            # Look up product by SKU using Shopify API
            return self.search_product_by_sku_graphql(sku)

        except Exception as e:
            logger.error(f"Error extracting product ID from filename {filename}: {e}")
            raise e


    def search_product_by_sku_graphql(self, sku: str) -> Optional[str]:
        """
        Search for product by SKU using GraphQL API (more efficient for large catalogs)

        Args:
            sku: The product SKU to search for

        Returns:
            Product ID as string, or None if not found
        """
        try:
            # GraphQL query to search for products by SKU
            query = """
            query getProductBySku($query: String!) {
                products(first: 10, query: $query) {
                    edges {
                        node {
                            id
                            title
                            variants(first: 50) {
                                edges {
                                    node {
                                        id
                                        sku
                                    }
                                }
                            }
                        }
                    }
                }
            }
            """

            variables = {
                "query": f"sku:{sku}"
            }

            response = self._execute_graphql_query(query, variables)

            if response and 'data' in response and 'products' in response['data']:
                products = response['data']['products']['edges']

                for product_edge in products:
                    product = product_edge['node']
                    variants = product['variants']['edges']

                    for variant_edge in variants:
                        variant = variant_edge['node']
                        if variant.get('sku') == sku:
                            # Extract numeric ID from GraphQL ID (e.g., "gid://shopify/Product/123" -> "123")
                            product_gid = product['id']
                            product_id = product_gid.split('/')[-1]
                            logger.info(f"Found product {product_id} with title '{product['title']}' for SKU '{sku}' via GraphQL")
                            return product_id

            logger.warning(f"No product found for SKU '{sku}' via GraphQL search")
            return None

        except Exception as e:
            logger.error(f"Error searching for product with SKU {sku} via GraphQL: {e}")
            raise e


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
            if not is_valid_media(media_path):
                logger.error(f"Invalid media file: {media_path}")
                return False

            # Check if it's a video or image
            is_video = media_path.suffix.lower() in SUPPORTED_VIDEO_FORMATS

            if is_video:
                return False
            else:
                return self._upload_image_to_product(product, media_path, alt_text)

        except Exception as e:
            raise e

    def _upload_image_to_product(self, product: shopify.Product, image_path: Path, alt_text: str = None) -> bool:
        import base64
        with open(image_path, "rb") as f:
            image_data = f.read()
        encoded_image = base64.b64encode(image_data).decode("utf-8")

        # Create new image
        new_image = shopify.Image()
        new_image.product_id = product.id
        new_image.alt = alt_text or image_path.stem
        new_image.attachment = encoded_image
        success = new_image.save()

        if success:
            print(f"Image uploaded successfully: {new_image.src}")
        else:
            print("Image upload failed:", new_image.errors.full_messages())
        return success


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
                'X-Shopify-Access-Token': self.access_token
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
                if not is_valid_media(media_path):
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

    # Initialize uploader
    try:
        uploader = ShopifyImageUploader(SHOPIFY_STORE_URL, ADMIN_API_ACCESS_TOKEN)
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
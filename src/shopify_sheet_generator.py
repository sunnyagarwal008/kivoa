#!/usr/bin/env python3
"""
Jewelry CSV Processor for Shopify

This script processes a CSV file containing jewelry items with Google Drive image URLs,
downloads the images, uses Gemini AI to extract product information, and generates
a Shopify-compatible CSV file.

Usage:
    python shopify_sheet_generator.py input.csv output.csv

Input CSV format:
    Image URL, SNo, SKU, Price Code, Buy Price, GST, MRP, Discount, Selling Price, Quantity
    (may have additional columns)

Output CSV format:
    Shopify-compatible format with AI-generated titles, descriptions, tags, and categories
"""

import argparse
import logging
import re
from pathlib import Path
from typing import Dict, Optional
from urllib.parse import urlparse, parse_qs

import gdown
import pandas as pd
from google import genai
from google.genai import types

# Try to import from src directory, fallback to current directory
try:
    from src.config import GEMINI_API_KEY, GEMINI_MODEL
except ImportError:
    # If running from root directory
    import sys

    sys.path.append('')
    from config import GEMINI_API_KEY, GEMINI_MODEL

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class JewelryCSVProcessor:
    """Process jewelry CSV files and generate Shopify-compatible output"""

    def __init__(self, gemini_api_key: str):
        """Initialize the processor with Gemini API key"""
        self.gemini_api_key = gemini_api_key
        self.client = genai.Client(api_key=gemini_api_key)
        self.temp_images_dir = Path("temp_images")
        self.temp_images_dir.mkdir(exist_ok=True)

        # Shopify CSV headers
        self.shopify_headers = [
            'Handle', 'Title', 'Body (HTML)', 'Vendor', 'Product Category', 'Type',
            'Tags', 'Published', 'Option1 Name', 'Option1 Value', 'Option2 Name',
            'Option2 Value', 'Option3 Name', 'Option3 Value', 'Variant SKU',
            'Variant Grams', 'Variant Inventory Tracker', 'Variant Inventory Qty',
            'Variant Inventory Policy', 'Variant Fulfillment Service',
            'Variant Price', 'Variant Compare At Price', 'Variant Requires Shipping',
            'Variant Taxable', 'Variant Barcode', 'Image Src', 'Image Position',
            'Image Alt Text', 'Gift Card', 'SEO Title', 'SEO Description',
            'Google Shopping / Google Product Category', 'Google Shopping / Gender',
            'Google Shopping / Age Group', 'Google Shopping / MPN',
            'Google Shopping / AdWords Grouping', 'Google Shopping / AdWords Labels',
            'Google Shopping / Condition', 'Google Shopping / Custom Product',
            'Google Shopping / Custom Label 0', 'Google Shopping / Custom Label 1',
            'Google Shopping / Custom Label 2', 'Google Shopping / Custom Label 3',
            'Google Shopping / Custom Label 4', 'Variant Image', 'Variant Weight Unit',
            'Variant Tax Code', 'Cost per item', 'Status'
        ]

    def extract_google_drive_id(self, url: str) -> Optional[str]:
        """Extract file ID from Google Drive URL"""
        try:
            # Handle different Google Drive URL formats
            if 'drive.google.com' in url:
                if '/open?id=' in url:
                    return url.split('/open?id=')[1].split('&')[0]
                elif '/file/d/' in url:
                    return url.split('/file/d/')[1].split('/')[0]
                elif 'id=' in url:
                    parsed = urlparse(url)
                    query_params = parse_qs(parsed.query)
                    return query_params.get('id', [None])[0]
            return None
        except Exception as e:
            logger.error(f"Error extracting Google Drive ID from {url}: {e}")
            return None

    def download_image(self, drive_url: str, sku: str) -> Optional[Path]:
        """Download image from Google Drive URL"""
        try:
            file_id = self.extract_google_drive_id(drive_url)
            if not file_id:
                logger.error(f"Could not extract file ID from URL: {drive_url}")
                return None

            # Create download URL
            download_url = f"https://drive.google.com/uc?id={file_id}"

            # Create filename based on SKU
            image_path = self.temp_images_dir / f"{sku}.jpg"

            # Download the file
            logger.info(f"Downloading image for SKU {sku}...")
            gdown.download(download_url, str(image_path), quiet=True)

            if image_path.exists() and image_path.stat().st_size > 0:
                logger.info(f"Successfully downloaded image for SKU {sku}")
                return image_path
            else:
                logger.error(f"Failed to download image for SKU {sku}")
                return None

        except Exception as e:
            logger.error(f"Error downloading image for SKU {sku}: {e}")
            return None

    def get_mime_type(self, file_path: Path) -> str:
        """Get MIME type for image file"""
        import mimetypes
        mime_type, _ = mimetypes.guess_type(str(file_path))
        return mime_type or 'image/jpeg'

    def analyze_jewelry_with_gemini(self, image_path: Path, sku: str, price: float) -> Dict[str, str]:
        """Use Gemini to analyze jewelry image and extract product information"""
        try:
            logger.info(f"Analyzing jewelry image for SKU {sku} with Gemini...")

            # Prepare the prompt
            prompt = f"""
            Analyze this jewelry image and provide the following information in a structured format:

            1. TITLE: Generate a 4-5 word catchy product title that would appeal to customers
            2. DESCRIPTION: Write a 5-6 line SEO-friendly product description that highlights the jewelry's features, materials, and appeal
            3. CATEGORY: Identify the jewelry category (e.g., Necklace, Earrings, Ring, Bracelet, Pendant, Chain, etc.)
            4. TAGS: Generate 8-10 relevant tags separated by commas (include style, material, occasion, color, etc.)

            Please format your response exactly like this:
            TITLE: [your title here]
            DESCRIPTION: [your description here]
            CATEGORY: [category here]
            TAGS: [tag1, tag2, tag3, etc.]

            The jewelry item has SKU: {sku} and price: ${price:.2f}
            """

            # Read image data
            with open(image_path, "rb") as f:
                image_data = f.read()

            mime_type = self.get_mime_type(image_path)

            # Prepare content for Gemini
            contents = [
                types.Part(inline_data=types.Blob(data=image_data, mime_type=mime_type)),
                genai.types.Part.from_text(text=prompt)
            ]

            # Generate content
            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=contents
            )

            # Parse response
            response_text = response.text
            logger.info(f"Gemini response for SKU {sku}: {response_text[:200]}...")

            return self.parse_gemini_response(response_text)

        except Exception as e:
            logger.error(f"Error analyzing image with Gemini for SKU {sku}: {e}")
            return self.get_fallback_product_info(sku, price)

    def parse_gemini_response(self, response_text: str) -> Dict[str, str]:
        """Parse Gemini response to extract structured information"""
        try:
            result = {
                'title': '',
                'description': '',
                'category': '',
                'tags': ''
            }

            lines = response_text.strip().split('\n')
            current_field = None

            for line in lines:
                line = line.strip()
                if line.startswith('TITLE:'):
                    result['title'] = line.replace('TITLE:', '').strip()
                elif line.startswith('DESCRIPTION:'):
                    result['description'] = line.replace('DESCRIPTION:', '').strip()
                    current_field = 'description'
                elif line.startswith('CATEGORY:'):
                    result['category'] = line.replace('CATEGORY:', '').strip()
                    current_field = None
                elif line.startswith('TAGS:'):
                    result['tags'] = line.replace('TAGS:', '').strip()
                    current_field = None
                elif current_field == 'description' and line and not line.startswith(('CATEGORY:', 'TAGS:')):
                    # Continue description on next lines
                    result['description'] += ' ' + line

            # Clean up description
            result['description'] = ' '.join(result['description'].split())

            return result

        except Exception as e:
            logger.error(f"Error parsing Gemini response: {e}")
            return {
                'title': 'Beautiful Jewelry Piece',
                'description': 'Elegant and stylish jewelry piece perfect for any occasion.',
                'category': 'Jewelry',
                'tags': 'jewelry, elegant, stylish, fashion, accessory'
            }

    def get_fallback_product_info(self, sku: str, price: float) -> Dict[str, str]:
        """Generate fallback product information when Gemini analysis fails"""
        return {
            'title': f'Jewelry Item {sku}',
            'description': f'Beautiful jewelry piece with SKU {sku}. Crafted with attention to detail and perfect for any occasion. High-quality materials and elegant design make this a must-have accessory.',
            'category': 'Jewelry',
            'tags': 'jewelry, elegant, fashion, accessory, handcrafted'
        }

    def create_shopify_handle(self, title: str, sku: str) -> str:
        """Create a Shopify handle from title and SKU"""
        # Combine title and SKU, convert to lowercase, replace spaces and special chars with hyphens
        handle = f"{title} {sku}".lower()
        handle = re.sub(r'[^a-z0-9\s-]', '', handle)
        handle = re.sub(r'\s+', '-', handle)
        handle = re.sub(r'-+', '-', handle)
        return handle.strip('-')

    def process_csv_row(self, row: Dict) -> Optional[Dict]:
        """Process a single CSV row and return Shopify-compatible data"""
        try:
            # Extract required fields
            image_url = row.get('Image URL', '').strip()
            sku = row.get('SKU', '').strip()
            selling_price = float(row.get('Selling Price', 0))
            mrp = float(row.get('MRP', 0))
            quantity = int(row.get('Quantity', 0))

            if not image_url or not sku:
                logger.warning(f"Skipping row with missing image URL or SKU: {row}")
                return None

            # Download image
            image_path = self.download_image(image_url, sku)
            if not image_path:
                logger.error(f"Failed to download image for SKU {sku}")
                return None

            # Analyze with Gemini
            product_info = self.analyze_jewelry_with_gemini(image_path, sku, selling_price)

            # Create Shopify handle
            handle = self.create_shopify_handle(product_info['title'], sku)

            # Prepare Shopify row data
            shopify_row = {
                'Handle': handle,
                'Title': product_info['title'],
                'Body (HTML)': f"<p>{product_info['description']}</p>",
                'Vendor': 'Your Store',  # You can customize this
                'Product Category': product_info['category'],
                'Type': product_info['category'],
                'Tags': product_info['tags'],
                'Published': 'TRUE',
                'Option1 Name': 'Title',
                'Option1 Value': 'Default Title',
                'Option2 Name': '',
                'Option2 Value': '',
                'Option3 Name': '',
                'Option3 Value': '',
                'Variant SKU': sku,
                'Variant Grams': '',
                'Variant Inventory Tracker': 'shopify',
                'Variant Inventory Qty': str(quantity),
                'Variant Inventory Policy': 'deny',
                'Variant Fulfillment Service': 'manual',
                'Variant Price': str(selling_price),
                'Variant Compare At Price': str(mrp) if mrp > selling_price else '',
                'Variant Requires Shipping': 'TRUE',
                'Variant Taxable': 'TRUE',
                'Variant Barcode': '',
                'Image Src': '',  # Will be filled after uploading to Shopify
                'Image Position': '1',
                'Image Alt Text': product_info['title'],
                'Gift Card': 'FALSE',
                'SEO Title': product_info['title'],
                'SEO Description': product_info['description'][:160],  # SEO description limit
                'Google Shopping / Google Product Category': 'Apparel & Accessories > Jewelry',
                'Google Shopping / Gender': 'Unisex',
                'Google Shopping / Age Group': 'Adult',
                'Google Shopping / MPN': sku,
                'Google Shopping / AdWords Grouping': product_info['category'],
                'Google Shopping / AdWords Labels': product_info['tags'],
                'Google Shopping / Condition': 'New',
                'Google Shopping / Custom Product': 'FALSE',
                'Google Shopping / Custom Label 0': '',
                'Google Shopping / Custom Label 1': '',
                'Google Shopping / Custom Label 2': '',
                'Google Shopping / Custom Label 3': '',
                'Google Shopping / Custom Label 4': '',
                'Variant Image': '',
                'Variant Weight Unit': 'g',
                'Variant Tax Code': '',
                'Cost per item': row.get('Buy Price', ''),
                'Status': 'active'
            }

            # Clean up temporary image
            try:
                image_path.unlink()
            except:
                pass

            return shopify_row

        except Exception as e:
            logger.error(f"Error processing row {row}: {e}")
            return None

    def process_csv_file(self, input_file: str, output_file: str) -> None:
        """Process the entire CSV file"""
        try:
            logger.info(f"Reading input CSV file: {input_file}")

            # Read input CSV
            df = pd.read_csv(input_file)
            logger.info(f"Found {len(df)} rows in input file")

            # Process each row
            shopify_rows = []
            for index, row in df.iterrows():
                logger.info(f"Processing row {index + 1}/{len(df)}")
                shopify_row = self.process_csv_row(row.to_dict())
                if shopify_row:
                    shopify_rows.append(shopify_row)
                else:
                    logger.warning(f"Skipped row {index + 1}")

            # Write output CSV
            if shopify_rows:
                logger.info(f"Writing {len(shopify_rows)} products to output file: {output_file}")
                output_df = pd.DataFrame(shopify_rows)
                output_df.to_csv(output_file, index=False)
                logger.info(f"Successfully created Shopify CSV: {output_file}")
            else:
                logger.error("No valid products to write to output file")

        except Exception as e:
            logger.error(f"Error processing CSV file: {e}")
            raise

    def cleanup(self):
        """Clean up temporary files"""
        try:
            if self.temp_images_dir.exists():
                for file in self.temp_images_dir.glob("*"):
                    file.unlink()
                self.temp_images_dir.rmdir()
                logger.info("Cleaned up temporary files")
        except Exception as e:
            logger.warning(f"Error cleaning up temporary files: {e}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Process jewelry CSV for Shopify upload')
    parser.add_argument('input_csv', help='Input CSV file path')
    parser.add_argument('output_csv', help='Output Shopify CSV file path')
    parser.add_argument('--api-key', help='Gemini API key (optional, uses config if not provided)')

    args = parser.parse_args()

    # Get API key
    api_key = args.api_key or GEMINI_API_KEY
    if not api_key:
        logger.error("Gemini API key not provided. Set it in config.py or use --api-key argument")
        sys.exit(1)

    # Initialize processor
    processor = JewelryCSVProcessor(api_key)

    try:
        # Process the CSV file
        processor.process_csv_file(args.input_csv, args.output_csv)
        logger.info("Processing completed successfully!")

    except Exception as e:
        logger.error(f"Processing failed: {e}")
        sys.exit(1)

    finally:
        # Clean up
        processor.cleanup()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Test script for the extract_product_id_from_filename function
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / 'src'))

from shopify_image_uploader import ShopifyImageUploader
from config import ADMIN_API_ACCESS_TOKEN, SHOPIFY_STORE_URL

def test_sku_extraction():
    """Test SKU extraction and product lookup"""
    
    # Initialize uploader
    try:
        uploader = ShopifyImageUploader(
            shop_url=SHOPIFY_STORE_URL,
            access_token=ADMIN_API_ACCESS_TOKEN
        )
        print("✅ Successfully connected to Shopify")
    except Exception as e:
        raise e

    # Test filenames
    test_filenames = [
        "ER-00003-0825-01"
    ]

    print("\n" + "="*60)
    print("TESTING SKU EXTRACTION AND PRODUCT LOOKUP")
    print("="*60)

    for filename in test_filenames:
        print(f"\nTesting filename: {filename}")
        print("-" * 40)
        
        try:
            product_id = uploader.extract_product_id_from_filename(filename)
            if product_id:
                print(f"✅ Found product ID: {product_id}")
                
                # Try to get the actual product to verify
                product = uploader.get_product(product_id)
                if product:
                    print(f"✅ Product verified: {product.title}")
                else:
                    print(f"⚠️  Product ID {product_id} found but product not accessible")
            else:
                print(f"❌ No product found for filename: {filename}")
                
        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")

    print("\n" + "="*60)
    print("TEST COMPLETED")
    print("="*60)

if __name__ == "__main__":
    test_sku_extraction()

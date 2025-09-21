#!/usr/bin/env python3
"""
Example usage of the updated extract_product_id_from_filename function
that fetches product_id from SKU using Shopify API
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / 'src'))

from shopify_image_uploader import ShopifyImageUploader
from config import SHOPIFY_API_KEY, SHOPIFY_SECRET_KEY, SHOPIFY_STORE_URL

def example_sku_to_product_id():
    """Example of how the updated function works"""
    
    print("Shopify SKU to Product ID Lookup Example")
    print("=" * 50)
    
    # Initialize the uploader
    try:
        uploader = ShopifyImageUploader(
            shop_url=SHOPIFY_STORE_URL,
            api_key=SHOPIFY_API_KEY,
            secret_key=SHOPIFY_SECRET_KEY
        )
        print("✅ Connected to Shopify store")
    except Exception as e:
        print(f"❌ Failed to connect to Shopify: {e}")
        return

    # Example filename with SKU pattern
    filename = "NK-00001-0825-02.jpg"
    
    print(f"\n📁 Processing filename: {filename}")
    print("-" * 30)
    
    # The function now:
    # 1. Extracts SKU from filename (NK-00001-0825)
    # 2. Searches Shopify for a product with that SKU
    # 3. Returns the product ID if found
    
    product_id = uploader.extract_product_id_from_filename(filename)
    
    if product_id:
        print(f"✅ Successfully found product ID: {product_id}")
        
        # You can now use this product_id to upload images
        print(f"\n📤 You can now upload images to product {product_id}")
        print("Example:")
        print(f"uploader.upload_media_to_product('{product_id}', Path('{filename}'))")
        
    else:
        print(f"❌ No product found for filename: {filename}")
        print("This could mean:")
        print("- No product exists with the extracted SKU")
        print("- The filename doesn't match the expected pattern")
        print("- There was an API error")

def example_batch_processing():
    """Example of processing multiple files"""
    
    print("\n" + "=" * 50)
    print("BATCH PROCESSING EXAMPLE")
    print("=" * 50)
    
    # Initialize the uploader
    try:
        uploader = ShopifyImageUploader(
            shop_url=SHOPIFY_STORE_URL,
            api_key=SHOPIFY_API_KEY,
            secret_key=SHOPIFY_SECRET_KEY
        )
    except Exception as e:
        print(f"❌ Failed to connect to Shopify: {e}")
        return

    # Example filenames
    filenames = [
        "NK-00001-0825-01.jpg",
        "NK-00001-0825-02.png", 
        "ER-12345-0825-01.jpeg",
        "BR-99999-0825-03.jpg"
    ]
    
    print(f"📁 Processing {len(filenames)} files...")
    
    results = {
        'found': [],
        'not_found': []
    }
    
    for filename in filenames:
        print(f"\n🔍 Processing: {filename}")
        
        product_id = uploader.extract_product_id_from_filename(filename)
        
        if product_id:
            print(f"  ✅ Found product ID: {product_id}")
            results['found'].append((filename, product_id))
        else:
            print(f"  ❌ No product found")
            results['not_found'].append(filename)
    
    # Summary
    print(f"\n📊 SUMMARY:")
    print(f"  ✅ Found products: {len(results['found'])}")
    print(f"  ❌ Not found: {len(results['not_found'])}")
    
    if results['found']:
        print(f"\n✅ Successfully mapped files:")
        for filename, product_id in results['found']:
            print(f"  {filename} → Product ID: {product_id}")
    
    if results['not_found']:
        print(f"\n❌ Files without matching products:")
        for filename in results['not_found']:
            print(f"  {filename}")

if __name__ == "__main__":
    example_sku_to_product_id()
    example_batch_processing()

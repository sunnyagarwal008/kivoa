#!/usr/bin/env python3
"""
Test script for the Jewelry CSV Processor

This script tests the processor with the sample inventory data.
"""

import os
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from src.shopify_sheet_generator import JewelryCSVProcessor
from src.config import GEMINI_API_KEY

def test_google_drive_url_extraction():
    """Test Google Drive URL parsing"""
    print("Testing Google Drive URL extraction...")
    
    processor = JewelryCSVProcessor(GEMINI_API_KEY or "test-key")
    
    test_urls = [
        "https://drive.google.com/open?id=18GwXB7fpana6JAP4tigi8zfcqPvd6w8B&usp=drive_fs",
        "https://drive.google.com/file/d/1iMfJVjh-m5eCzAf18ClXqpJLfTvg9Hw4/view",
        "https://drive.google.com/uc?id=1tCMjs7-VtvPvQ6JUs_LMSamkSkn7T0nx"
    ]
    
    for url in test_urls:
        file_id = processor.extract_google_drive_id(url)
        print(f"URL: {url[:50]}...")
        print(f"Extracted ID: {file_id}")
        print()

def test_shopify_handle_creation():
    """Test Shopify handle creation"""
    print("Testing Shopify handle creation...")
    
    processor = JewelryCSVProcessor(GEMINI_API_KEY or "test-key")
    
    test_cases = [
        ("Beautiful Gold Necklace", "NK-001", "beautiful-gold-necklace-nk-001"),
        ("Elegant Diamond Ring!", "RG-123", "elegant-diamond-ring-rg-123"),
        ("Silver Earrings & Pendant Set", "SET-456", "silver-earrings-pendant-set-set-456")
    ]
    
    for title, sku, expected in test_cases:
        handle = processor.create_shopify_handle(title, sku)
        print(f"Title: {title}")
        print(f"SKU: {sku}")
        print(f"Handle: {handle}")
        print(f"Expected: {expected}")
        print(f"Match: {'✅' if handle == expected else '❌'}")
        print()

def test_fallback_info():
    """Test fallback product information generation"""
    print("Testing fallback product information...")
    
    processor = JewelryCSVProcessor(GEMINI_API_KEY or "test-key")
    
    info = processor.get_fallback_product_info("TEST-001", 99.99)
    
    print("Fallback Product Info:")
    print(f"Title: {info['title']}")
    print(f"Description: {info['description']}")
    print(f"Category: {info['category']}")
    print(f"Tags: {info['tags']}")
    print()

def test_with_sample_data():
    """Test with actual sample data (without API calls)"""
    print("Testing with sample inventory data...")
    
    if not os.path.exists("sample_inventory.csv"):
        print("❌ sample_inventory.csv not found")
        return
    
    import pandas as pd
    
    # Read sample data
    df = pd.read_csv("sample_inventory.csv")
    print(f"Found {len(df)} rows in sample_inventory.csv")
    
    # Test processing first row (without actual API calls)
    if len(df) > 0:
        first_row = df.iloc[0].to_dict()
        print("\nFirst row data:")
        for key, value in first_row.items():
            print(f"  {key}: {value}")
        
        # Test URL extraction
        processor = JewelryCSVProcessor(GEMINI_API_KEY or "test-key")
        image_url = first_row.get('Image URL', '')
        if image_url:
            file_id = processor.extract_google_drive_id(image_url)
            print(f"\nExtracted Google Drive ID: {file_id}")

def main():
    """Run all tests"""
    print("="*60)
    print("JEWELRY CSV PROCESSOR - TEST SUITE")
    print("="*60)
    print()
    
    try:
        test_google_drive_url_extraction()
        print("-" * 40)
        
        test_shopify_handle_creation()
        print("-" * 40)
        
        test_fallback_info()
        print("-" * 40)
        
        test_with_sample_data()
        print("-" * 40)
        
        print("✅ All tests completed!")
        print()
        print("To run the full processor with API calls:")
        print("python example_jewelry_processor.py")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

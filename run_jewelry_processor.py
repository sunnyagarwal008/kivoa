#!/usr/bin/env python3
"""
Simple runner script for the Jewelry CSV Processor

This script provides an easy way to run the jewelry processor with
interactive prompts for file paths.
"""

import os
import sys


def main():
    """Interactive runner for jewelry processor"""
    
    print("="*60)
    print("JEWELRY CSV PROCESSOR FOR SHOPIFY")
    print("="*60)
    print()
    
    # Check if sample file exists
    if os.path.exists("sample_inventory.csv"):
        print("📁 Found sample_inventory.csv in current directory")
        use_sample = input("Use sample_inventory.csv as input? (y/n): ").lower().strip()
        if use_sample == 'y':
            input_file = "sample_inventory.csv"
        else:
            input_file = input("Enter path to your CSV file: ").strip()
    else:
        input_file = input("Enter path to your CSV file: ").strip()
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"❌ Error: File '{input_file}' not found!")
        return
    
    # Get output file name
    default_output = "shopify_jewelry_upload.csv"
    output_file = input(f"Enter output file name (default: {default_output}): ").strip()
    if not output_file:
        output_file = default_output
    
    print()
    print("Configuration:")
    print(f"  Input file: {input_file}")
    print(f"  Output file: {output_file}")
    print()
    
    # Confirm before processing
    confirm = input("Start processing? (y/n): ").lower().strip()
    if confirm != 'y':
        print("Processing cancelled.")
        return
    
    print()
    print("Starting processing...")
    print("-" * 40)
    
    try:
        # Import and run the processor
        from src.shopify_sheet_generator import JewelryCSVProcessor
        try:
            from src.config import GEMINI_API_KEY
        except ImportError:
            sys.path.append('src')
            from config import GEMINI_API_KEY
        
        if not GEMINI_API_KEY:
            print("❌ Error: Gemini API key not found!")
            print("Please set GEMINI_API_KEY in src/config.py")
            return
        
        # Initialize and run processor
        processor = JewelryCSVProcessor(GEMINI_API_KEY)
        processor.process_csv_file(input_file, output_file)
        
        print()
        print("="*60)
        print("✅ PROCESSING COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"Output file created: {output_file}")
        print()
        print("Next steps:")
        print("1. Review the generated CSV file")
        print("2. Upload images to Shopify")
        print("3. Import the CSV to your Shopify store")
        
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        print()
        print("Troubleshooting tips:")
        print("1. Check your Gemini API key in src/config.py")
        print("2. Ensure your CSV has the required columns")
        print("3. Verify Google Drive links are publicly accessible")
        print("4. Run: pip install -r requirements.txt")
    
    finally:
        # Cleanup
        try:
            if 'processor' in locals():
                processor.cleanup()
        except:
            pass

if __name__ == "__main__":
    main()

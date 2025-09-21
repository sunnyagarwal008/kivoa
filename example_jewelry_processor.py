#!/usr/bin/env python3
"""
Example script for using the Jewelry CSV Processor

This script demonstrates how to use the JewelryCSVProcessor to convert
a jewelry inventory CSV into a Shopify-compatible format.
"""

import os
import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / 'src'))

from src.shopify_sheet_generator import JewelryCSVProcessor
from src.config import GEMINI_API_KEY

def main():
    """Example usage of the Jewelry CSV Processor"""
    
    # Input and output file paths
    input_csv = "sample_inventory.csv"  # Your input CSV file
    output_csv = "shopify_jewelry_upload.csv"  # Output Shopify CSV
    
    # Check if input file exists
    if not os.path.exists(input_csv):
        print(f"Error: Input file '{input_csv}' not found.")
        print("Please make sure your CSV file exists and has the correct path.")
        return
    
    # Check API key
    if not GEMINI_API_KEY:
        print("Error: Gemini API key not found in config.py")
        print("Please set your GEMINI_API_KEY in src/config.py")
        return
    
    print("="*60)
    print("JEWELRY CSV PROCESSOR FOR SHOPIFY")
    print("="*60)
    print(f"Input file: {input_csv}")
    print(f"Output file: {output_csv}")
    print(f"Using Gemini API for product analysis...")
    print()
    
    try:
        # Initialize the processor
        processor = JewelryCSVProcessor(GEMINI_API_KEY)
        
        # Process the CSV file
        print("Starting processing...")
        processor.process_csv_file(input_csv, output_csv)
        
        print()
        print("="*60)
        print("PROCESSING COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"✅ Shopify CSV created: {output_csv}")
        print()
        print("Next steps:")
        print("1. Review the generated CSV file")
        print("2. Upload product images to your Shopify store")
        print("3. Import the CSV file to Shopify")
        print("4. Update image URLs in Shopify after upload")
        
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        print("Please check the logs above for more details.")
        
    finally:
        # Clean up temporary files
        try:
            processor.cleanup()
        except:
            pass

if __name__ == "__main__":
    main()

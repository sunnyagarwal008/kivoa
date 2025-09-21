# Jewelry CSV Processor for Shopify

This script processes a CSV file containing jewelry items with Google Drive image URLs, downloads the images, uses Google's Gemini AI to extract product information, and generates a Shopify-compatible CSV file.

## Features

- ✅ Downloads images from Google Drive URLs automatically
- ✅ Uses Gemini AI to generate product titles, descriptions, categories, and tags
- ✅ Creates SEO-friendly product descriptions
- ✅ Generates Shopify-compatible CSV format
- ✅ Handles various Google Drive URL formats
- ✅ Includes error handling and logging
- ✅ Supports batch processing of multiple products

## Requirements

### Dependencies
Install the required packages:
```bash
pip install -r requirements.txt
```

### API Key Setup
1. Get a Gemini API key from [Google AI Studio](https://aistudio.google.com/)
2. Update your API key in `src/config.py`:
```python
GEMINI_API_KEY = "your-api-key-here"
```

## Input CSV Format

Your input CSV should have these headers (additional columns are allowed):

| Column | Description | Required |
|--------|-------------|----------|
| Image URL | Google Drive link to jewelry image | ✅ Yes |
| SNo | Serial number | No |
| SKU | Product SKU/identifier | ✅ Yes |
| Price Code | Internal price code | No |
| Buy Price | Cost price | No |
| GST | Tax amount | No |
| MRP | Maximum retail price | No |
| Discount | Discount percentage | No |
| Selling Price | Final selling price | ✅ Yes |
| Quantity | Available quantity | ✅ Yes |

### Example Input CSV:
```csv
Image URL,SNo,SKU,Price Code,Buy Price,GST,MRP,Discount,Selling Price,Quantity
https://drive.google.com/open?id=18GwXB7fpana6JAP4tigi8zfcqPvd6w8B,00001,ER-00001-0825,TZZ,300,9,1236,20,988.8,1
```

## Usage

### Method 1: Using the Example Script
```bash
python example_jewelry_processor.py
```

### Method 2: Using the Main Script Directly
```bash
python shopify_sheet_generator.py input.csv output.csv
```

### Method 3: With Custom API Key
```bash
python shopify_sheet_generator.py input.csv output.csv --api-key YOUR_API_KEY
```

## Output

The script generates a Shopify-compatible CSV with the following information:

### AI-Generated Content:
- **Title**: 4-5 word catchy product title
- **Description**: 5-6 line SEO-friendly description
- **Category**: Jewelry category (Necklace, Ring, Earrings, etc.)
- **Tags**: 8-10 relevant tags for better discoverability

### Shopify Fields:
- Handle, Title, Body (HTML), Vendor, Product Category
- Tags, SEO Title, SEO Description
- Variant SKU, Price, Compare At Price, Inventory
- Google Shopping integration fields
- And many more Shopify-specific fields

## Google Drive URL Support

The script supports various Google Drive URL formats:
- `https://drive.google.com/open?id=FILE_ID`
- `https://drive.google.com/file/d/FILE_ID/view`
- `https://drive.google.com/uc?id=FILE_ID`

## Process Flow

1. **Read CSV**: Loads your jewelry inventory CSV
2. **Download Images**: Downloads each image from Google Drive
3. **AI Analysis**: Uses Gemini to analyze each image and generate:
   - Product title
   - SEO description
   - Category classification
   - Relevant tags
4. **Generate Shopify CSV**: Creates a complete Shopify import file
5. **Cleanup**: Removes temporary image files

## Error Handling

- **Missing Images**: Skips products with invalid/missing image URLs
- **Download Failures**: Logs errors and continues with next product
- **AI Analysis Failures**: Uses fallback product information
- **Invalid Data**: Skips rows with missing required fields

## Customization

### Modify AI Prompts
Edit the prompt in `jewelry_csv_processor.py` around line 120 to customize how Gemini analyzes your products.

### Adjust Shopify Fields
Modify the `shopify_row` dictionary in the `process_csv_row` method to customize output fields.

### Change Vendor Name
Update the `Vendor` field in the Shopify row data (currently set to "Your Store").

## Troubleshooting

### Common Issues:

1. **"Gemini API key not found"**
   - Solution: Set your API key in `src/config.py`

2. **"Failed to download image"**
   - Check if Google Drive links are publicly accessible
   - Ensure the file IDs are correct in the URLs

3. **"No valid products to write"**
   - Check your CSV format matches the expected headers
   - Ensure required fields (Image URL, SKU, Selling Price) are present

4. **Import errors**
   - Run: `pip install -r requirements.txt`
   - Make sure you're using Python 3.7+

### Logs
The script provides detailed logging to help identify issues:
- INFO: Normal processing steps
- WARNING: Non-critical issues (skipped rows)
- ERROR: Critical errors that prevent processing

## Next Steps After Processing

1. **Review Output**: Check the generated Shopify CSV file
2. **Upload Images**: Upload your jewelry images to Shopify
3. **Import Products**: Import the CSV file to your Shopify store
4. **Update Image URLs**: Link the uploaded images to products in Shopify
5. **Review Products**: Check and adjust product information as needed

## Example Output

The generated CSV will have entries like:
```csv
Handle,Title,Body (HTML),Vendor,Product Category,Type,Tags,Published,Variant SKU,Variant Price,...
elegant-gold-earrings-er-00001,Elegant Gold Earrings,"<p>Beautiful handcrafted gold earrings featuring intricate design...</p>",Your Store,Earrings,Earrings,"gold, earrings, elegant, handcrafted, jewelry",TRUE,ER-00001-0825,988.8,...
```

## Support

For issues or questions:
1. Check the logs for detailed error messages
2. Verify your CSV format matches the requirements
3. Ensure your Gemini API key is valid and has sufficient quota
4. Make sure Google Drive images are publicly accessible

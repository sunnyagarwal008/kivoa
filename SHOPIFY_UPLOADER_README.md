# Shopify Product Image Uploader

A Python script to automatically upload media files as product images to your Shopify store. The script extracts product IDs from filenames and uploads the corresponding images to the correct products.

## Features

- **Automatic Product ID Extraction**: Supports multiple filename patterns to extract product IDs
- **Batch Processing**: Upload multiple images from a folder in one go
- **Image Validation**: Validates image files before uploading
- **Dry Run Mode**: Test the process without actually uploading images
- **Comprehensive Logging**: Detailed logs for monitoring and debugging
- **Error Handling**: Robust error handling with detailed error reporting
- **Multiple Image Formats**: Supports JPG, PNG, BMP, GIF, TIFF, and WebP

## Installation

1. **Install required packages**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure your Shopify credentials** in `src/config.py`:
   ```python
   SHOPIFY_API_KEY = "your_api_key_here"
   SHOPIFY_SECRET_KEY = "your_secret_key_here"
   SHOPIFY_STORE_URL = "your-store.myshopify.com"
   ```

## Supported Filename Patterns

The script automatically extracts product IDs from filenames using these patterns:

| Pattern | Example | Extracted ID |
|---------|---------|--------------|
| `product_ID` | `product_123_main.jpg` | 123 |
| `ID_` | `456_variant.png` | 456 |
| `SKU_ID` | `SKU_789_photo.jpeg` | 789 |
| `ID_ID` | `ID_999_image.jpg` | 999 |
| `_ID_` | `item_555_front.jpg` | 555 |
| `-ID-` | `photo-888-back.jpg` | 888 |
| `^ID` | `1234567890.png` | 1234567890 |
| `6+ digits` | `item_1234567_photo.jpg` | 1234567 |

## Usage

### Command Line Usage

**Basic usage:**
```bash
python src/shopify_image_uploader.py /path/to/images --shop your-store.myshopify.com
```

**Dry run (test without uploading):**
```bash
python src/shopify_image_uploader.py ./product_images --shop your-store.myshopify.com --dry-run
```

**With custom API credentials:**
```bash
python src/shopify_image_uploader.py ./images \
  --shop your-store.myshopify.com \
  --api-key your_api_key \
  --secret-key your_secret_key
```

**Verbose logging:**
```bash
python src/shopify_image_uploader.py ./images --shop your-store.myshopify.com --verbose
```

### Python Script Usage

```python
from src.shopify_image_uploader import ShopifyImageUploader
from pathlib import Path

# Initialize uploader
uploader = ShopifyImageUploader(
    shop_url="your-store.myshopify.com",
    api_key="your_api_key",
    secret_key="your_secret_key"
)

# Upload all images from a folder
results = uploader.process_folder(Path("./product_images"))

# Upload a single image
success = uploader.upload_image_to_product(
    product_id="123456789",
    image_path=Path("./image.jpg"),
    alt_text="Product main image"
)
```

## Examples

### Example 1: Basic Folder Upload

```bash
# Create a folder with your product images
mkdir product_images

# Add images with product IDs in filenames:
# product_images/product_123_main.jpg
# product_images/456_variant_01.png
# product_images/SKU_789_photo.jpeg

# Upload all images (dry run first)
python src/shopify_image_uploader.py product_images --shop your-store.myshopify.com --dry-run

# If everything looks good, upload for real
python src/shopify_image_uploader.py product_images --shop your-store.myshopify.com
```

### Example 2: Using the Python API

```python
# Run the example script
python example_shopify_upload.py
```

## Configuration

### Shopify API Setup

1. **Create a Private App** in your Shopify admin:
   - Go to Apps → Manage private apps
   - Create a new private app
   - Enable "Read and write" permissions for Products

2. **Get your credentials**:
   - API key
   - Password (secret key)
   - Your store URL

3. **Update config.py** with your credentials

### Filename Organization

Organize your images with clear product ID patterns:

```
product_images/
├── product_123_main.jpg      # Main product image
├── product_123_variant1.jpg  # Variant image
├── 456_front.png            # Front view
├── 456_back.png             # Back view
├── SKU_789_lifestyle.jpeg   # Lifestyle shot
└── ID_999_detail.jpg        # Detail shot
```

## Error Handling

The script handles various error scenarios:

- **Invalid image files**: Skipped with warning
- **Missing products**: Logged as errors
- **Network issues**: Retried automatically
- **API rate limits**: Handled gracefully
- **Invalid filenames**: Skipped with warning

## Output

The script provides detailed output:

```
2023-12-07 10:30:15 - INFO - Connected to Shopify store: Your Store Name
2023-12-07 10:30:16 - INFO - Found 5 image files in ./product_images
2023-12-07 10:30:16 - INFO - Processing: product_123_main.jpg
2023-12-07 10:30:17 - INFO - Found product: Amazing Product (ID: 123)
2023-12-07 10:30:18 - INFO - Successfully uploaded product_123_main.jpg to product 123

==================================================
UPLOAD RESULTS
==================================================
Total files found: 5
Valid images: 5
Successful uploads: 4
Failed uploads: 1
Skipped files: 0
==================================================
```

## Troubleshooting

### Common Issues

1. **"Failed to connect to Shopify"**
   - Check your API credentials
   - Verify your store URL format
   - Ensure your private app has correct permissions

2. **"Product with ID X not found"**
   - Verify the product exists in your store
   - Check if the product ID extraction is correct
   - Use `--verbose` flag for detailed logging

3. **"Invalid image file"**
   - Ensure image files are not corrupted
   - Check supported formats: JPG, PNG, BMP, GIF, TIFF, WebP
   - Verify file permissions

4. **"Could not extract product ID from filename"**
   - Check filename patterns
   - Use `--verbose` to see extraction attempts
   - Consider renaming files to match supported patterns

### Testing

Always test with `--dry-run` first:

```bash
python src/shopify_image_uploader.py ./images --shop your-store.myshopify.com --dry-run --verbose
```

This will show you exactly what would happen without making any changes.

## Security Notes

- Keep your API credentials secure
- Use environment variables for production
- Regularly rotate your API keys
- Monitor API usage in Shopify admin

## Support

For issues or questions:
1. Check the verbose logs with `--verbose`
2. Test with `--dry-run` first
3. Verify your Shopify API permissions
4. Check the example scripts for reference

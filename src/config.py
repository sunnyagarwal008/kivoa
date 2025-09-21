"""
Configuration file for Image Transformer

Customize settings here. Prompts are now managed in prompts.py
"""

# Model configuration
GEMINI_MODEL = "gemini-2.5-flash-image-preview"
GEMINI_API_KEY = "AIzaSyAJJcmBEniJjDuLUi4WiG41ABK73axI2LQ"

# Supported image formats
SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}

# Output settings
OUTPUT_FORMAT = "PNG"
OUTPUT_QUALITY = 95

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# API settings
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds

# Processing settings
DEFAULT_MAX_IMAGES = None  # None means process all images
BATCH_SIZE = 1  # Process images one at a time

SHOPIFY_API_KEY = "3e6a0d39532f5dabbd0bd9bef6d39075"
SHOPIFY_SECRET_KEY = "4983ef3b5f91de44923e85d76e5210b7"
SHOPIFY_STORE_URL = "your-store.myshopify.com"  # Replace with your actual store URL

# Image Transformer using Google Gemini Nano Banana

This Python script transforms images using Google's Gemini 2.5 Flash Image model (also known as "Nano Banana"). It reads images from an input directory, applies random creative transformation prompts, and saves the transformed images to an output directory.

## Features

- **Batch Processing**: Process multiple images from a directory
- **Categorized Prompts**: 80+ creative transformation prompts organized in 9 categories
- **Multiple Formats**: Supports JPG, PNG, BMP, GIF, TIFF, and WebP input formats
- **Detailed Logging**: Comprehensive logging for monitoring progress and debugging
- **Prompt Tracking**: Saves the transformation prompt used for each image
- **Error Handling**: Robust error handling for failed transformations

## Installation

1. **Clone or download this repository**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Get a Google Gemini API key**:
   - Visit [Google AI Studio](https://aistudio.google.com/)
   - Create an account and generate an API key
   - Keep your API key secure

## Usage

### Basic Usage

```bash
python src/image_transformer.py input_images/ output_images/ --api-key YOUR_API_KEY
```

### Using Environment Variable

Set your API key as an environment variable:

```bash
export GEMINI_API_KEY="your_api_key_here"
python src/image_transformer.py input_images/ output_images/
```

### Limit Number of Images

Process only the first 5 images:

```bash
python src/image_transformer.py input_images/ output_images/ --max-images 5
```

### Use Specific Prompt Category

Use only fantasy-themed prompts:

```bash
python src/image_transformer.py input_images/ output_images/ --category fantasy
```

### Command Line Arguments

- `input_dir`: Directory containing input images (required)
- `output_dir`: Directory to save transformed images (required)
- `--api-key`: Your Google Gemini API key (optional if set as environment variable)
- `--max-images`: Maximum number of images to process (optional)
- `--category`: Prompt category to use (optional)

## Prompt Categories

The script includes 80+ transformation prompts organized in 9 categories:

- **Default**: Mixed styles (20 prompts)
- **Nature**: Landscapes, gardens, natural scenes (10 prompts)
- **Urban**: Cities, architecture, industrial (10 prompts)
- **Artistic**: Famous art styles and techniques (10 prompts)
- **Fantasy**: Magical, mythical, enchanted (10 prompts)
- **Sci-Fi**: Futuristic, space, technology (10 prompts)
- **Horror**: Dark, spooky, supernatural (10 prompts)
- **Seasonal**: Weather, seasons, atmosphere (10 prompts)
- **Abstract**: Experimental, geometric, artistic (10 prompts)


## Output

For each processed image, the script creates:

1. **Transformed Image**: `transformed_[original_name].png`
2. **Prompt File**: `prompt_[original_name].txt` containing:
   - Original image filename
   - Transformation prompt used

## Example Directory Structure

```
project/
├── src/
│   └── image_transformer.py
├── input_images/
│   ├── photo1.jpg
│   ├── photo2.png
│   └── photo3.jpeg
├── output_images/
│   ├── transformed_photo1.png
│   ├── prompt_photo1.txt
│   ├── transformed_photo2.png
│   ├── prompt_photo2.txt
│   ├── transformed_photo3.png
│   └── prompt_photo3.txt
├── requirements.txt
└── README.md
```

## Supported Image Formats

**Input formats**: JPG, JPEG, PNG, BMP, GIF, TIFF, WebP
**Output format**: PNG (for best quality and compatibility)

## Error Handling

The script includes comprehensive error handling:

- Invalid image files are skipped with warnings
- API failures are logged and processing continues
- Missing directories are created automatically
- Detailed logging helps with troubleshooting

## API Costs

Google Gemini image generation is token-based pricing:
- Approximately $30 USD per 1 million tokens
- Each image output uses ~1290 tokens (for images up to 1024x1024 pixels)
- Monitor your usage in the Google AI Studio console

## Limitations

- Requires active internet connection
- API rate limits may apply
- Generated images include SynthID watermarks
- Best performance with images under 1024x1024 pixels

## Troubleshooting

### Common Issues

1. **"Failed to initialize Gemini client"**
   - Check your API key is correct
   - Ensure you have internet connectivity
   - Verify your API key has proper permissions

2. **"No valid images found"**
   - Check input directory path
   - Ensure images are in supported formats
   - Verify file permissions

3. **"Failed to transform image"**
   - Check API quota and billing
   - Try with smaller images
   - Check for API service outages

### Logging

The script provides detailed logging. To see debug information:

```python
# Modify logging level in the script
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

Feel free to contribute by:
- Adding new transformation prompts
- Improving error handling
- Adding new features
- Optimizing performance

## License

This project is provided as-is for educational and creative purposes. Please respect Google's API terms of service and usage policies.

## Disclaimer

- Use responsibly and respect copyright laws
- Generated images may not always match expectations
- API costs apply - monitor your usage
- This tool is for creative and educational purposes

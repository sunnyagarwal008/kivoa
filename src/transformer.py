import argparse
import mimetypes
import os
import random
from pathlib import Path

from google import genai
from google.genai import types
from image_helper import convert_to_square, load_image

from config import (
    GEMINI_API_KEY,
)

from prompts import get_prompts_by_category

MODEL_NAME = "gemini-2.5-flash-image-preview"

prompt_category_to_prefix = {
    'necklace': 'nk-',
    'ring': 'rg-',
}

def generate_images(
        input_dir: str,
        prompt_category: str,
        output_dir: str,
        number_of_images: int = 3,
):
    api_key = GEMINI_API_KEY
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")

    client = genai.Client(api_key=api_key)

    file_prefix = prompt_category_to_prefix[prompt_category]
    input_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.png') and f.lower().startswith(file_prefix)]
    prompts = get_prompts_by_category(prompt_category)
    for image_name in input_files:
        for i in range(1, number_of_images + 1):
            prompt = random.choice(prompts[i-1])
            input_file = os.path.join(input_dir, image_name)
            input_image_parts = image_name.split(".")
            image_prefix = input_image_parts[0]

            sku = image_prefix[:image_prefix.rfind('-')]
            final_prompt = prompt + " Also add the text " + sku + " vertically top to down to the bottom right of the generated image, the font size should be 6 and font color should be contrasting with the background."
            output_image_name = f"{sku}-0{i}.{input_image_parts[1]}"
            output_file = os.path.join(output_dir, f"{output_image_name}")
            do_generate_image(client, sku, input_file, output_file, final_prompt)


def do_generate_image(client, sku, image_path, output_file, prompt):
    contents = []
    print(f"Processing {image_path}...")
    with open(image_path, "rb") as f:
        image_data = f.read()
    mime_type = _get_mime_type(image_path)
    contents.append(
        types.Part(inline_data=types.Blob(data=image_data, mime_type=mime_type))
    )
    contents.append(genai.types.Part.from_text(text=prompt))
    generate_content_config = types.GenerateContentConfig(response_modalities=["IMAGE", "TEXT"])
    print(f"Image {image_path}, prompt: {prompt}")
    stream = client.models.generate_content_stream(
        model=MODEL_NAME,
        contents=contents,
        config=generate_content_config,
    )

    _process_api_stream_response(stream, output_file)

def _load_image_parts(image_paths: list[str]) -> list[types.Part]:
    """Loads image files and converts them into GenAI Part objects."""
    parts = []
    for image_path in image_paths:
        with open(image_path, "rb") as f:
            image_data = f.read()
        mime_type = _get_mime_type(image_path)
        parts.append(
            types.Part(inline_data=types.Blob(data=image_data, mime_type=mime_type))
        )
    return parts


def _process_api_stream_response(stream, output_file: str):
    """Processes the streaming response from the GenAI API, saving images and printing text."""
    file_index = 0
    for chunk in stream:
        if (
                chunk.candidates is None
                or chunk.candidates[0].content is None
                or chunk.candidates[0].content.parts is None
        ):
            continue

        for part in chunk.candidates[0].content.parts:
            if part.inline_data and part.inline_data.data:
                _save_binary_file(output_file, part.inline_data.data)
                file_index += 1
            elif part.text:
                print(part.text)


def _save_binary_file(file_name: str, data: bytes):
    """Saves binary data to a specified file."""
    with open(file_name, "wb") as f:
        f.write(data)
    print(f"File saved to: {file_name}")


def _get_mime_type(file_path: str) -> str:
    """Guesses the MIME type of a file based on its extension."""
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        raise ValueError(f"Could not determine MIME type for {file_path}")
    return mime_type


def main():
    parser = argparse.ArgumentParser(
        description="Remix images using Google Generative AI."
    )
    parser.add_argument(
        "-i",
        "--input-dir",
        type=str,
        required=True,
        help="Paths to input images",
    )
    parser.add_argument(
        "-c",
        "--category",
        type=str,
        required=True,
        help="Category if image",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=str,
        required=True,
        help="Directory to save the remixed images.",
    )
    parser.add_argument(
        "-n",
        "--number-of-images",
        type=int,
        required=True,
        help="Number of images for each input image",
    )

    args = parser.parse_args()

    generate_images(
        input_dir=args.input_dir,
        prompt_category=args.category,
        output_dir=args.output_dir,
        number_of_images=args.number_of_images,
    )


if __name__ == "__main__":
    main()

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

SUPPORTED_MIME = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}

DEFAULT_PROMPT = """
Task: Reduce the saturation of the image to zero, do not modify any other details.
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image",  default="image_test.png")
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    parser.add_argument("--output", default="result_test.png")
    args = parser.parse_args()

    if not args.output.endswith(".png"):
        args.output += ".png"

    load_dotenv(".env.gemini")

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        sys.exit("GEMINI_API_KEY not set in .env")

    client = genai.Client(api_key=api_key)

    img = Path(args.image)
    if not img.exists():
        sys.exit(f"Image not found: {args.image}")
    mime = SUPPORTED_MIME.get(img.suffix.lower(), "image/png")

    contents = [
        types.Part.from_bytes(data=img.read_bytes(), mime_type=mime),
        types.Part.from_text(text=args.prompt),
    ]

    response = client.models.generate_content(
        model="gemini-3.1-flash-image-preview",
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
        ),
    )

    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            Path(args.output).write_bytes(part.inline_data.data)
            print(f"Saved: {args.output}")
            return

    sys.exit("Model did not return an image.")


if __name__ == "__main__":
    main()
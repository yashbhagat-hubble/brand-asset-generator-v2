import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from prompts import DEFAULT_PROMPT

SUPPORTED_MIME = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-logo",  default="input_logo.png")
    parser.add_argument("--input-image", default="input_image.png")
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    parser.add_argument("--output", default="output_aistudio.png")
    args = parser.parse_args()

    if not args.output.endswith(".png"):
        args.output += ".png"

    load_dotenv(".env.aistudio")

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        sys.exit("GEMINI_API_KEY not set in .env")

    client = genai.Client(api_key=api_key)

    logo = Path(args.input_logo)
    image = Path(args.input_image)
    for p in [logo, image]:
        if not p.exists():
            sys.exit(f"Image not found: {p}")

    contents = [
        types.Part.from_bytes(data=logo.read_bytes(), mime_type=SUPPORTED_MIME.get(logo.suffix.lower(), "image/png")),
        types.Part.from_bytes(data=image.read_bytes(), mime_type=SUPPORTED_MIME.get(image.suffix.lower(), "image/png")),
        types.Part.from_text(text=args.prompt),
    ]

    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",
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
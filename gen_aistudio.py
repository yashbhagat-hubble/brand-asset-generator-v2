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

DEFAULT_PROMPT = """Task: Create a high-resolution digital brand asset with size 208px * 232px dimensions, fixed aspect ratio (104x116).
Background: The background is a single, uniform, solid fill of [Pick from image]. There are no gradients, textures, soft blurs, or shadows on this layer; it is perfectly flat and consistent from top to bottom.

Logo Placement: Centered horizontally and vertically within the top 40 percent of the canvas. The logo must have a fully transparent background (no cards, panels, or bounding boxes). It should occupy approximately 60 percent of the frame width.

Logo Styling: Render the logo in a high-contrast color [pick intelligently] to ensure it is perfectly legible against the solid background—no subtext, taglines, or decorative elements.
Subject: The subject [Pick from image] is anchored to the bottom edge of the canvas.
Composition: The upper 20 percent of the image is intentionally left as "quiet" negative space (just the solid background color) to allow the logo to sit cleanly. The final output is premium, clean, and editorial with no visible dividers or borders."""


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
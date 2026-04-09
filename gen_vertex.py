import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
import google.oauth2.service_account
import google.auth
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
    parser.add_argument("--output", default="output_vertex.png")
    args = parser.parse_args()

    load_dotenv(".env.vertex")

    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project:
        sys.exit("GOOGLE_CLOUD_PROJECT not set")

    key_file = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if key_file:
        credentials = google.oauth2.service_account.Credentials.from_service_account_file(
            key_file, scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
    else:
        credentials, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )

    client = genai.Client(vertexai=True, project=project, location="us-central1", credentials=credentials)

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

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai.types import EditImageConfig, RawReferenceImage, Image as GenAIImage
import google.oauth2.service_account
import google.auth


SUPPORTED_MIME = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image",  default="image_test.png")
    parser.add_argument("--prompt", default="change saturation of the image to zero")
    parser.add_argument("--output", default="result_test.png")
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

    img = Path(args.image)
    if not img.exists():
        sys.exit(f"Image not found: {args.image}")
    mime = SUPPORTED_MIME.get(img.suffix.lower(), "image/png")

    response = client.models.edit_image(
        model="imagen-3.0-capability-001",
        prompt=args.prompt,
        reference_images=[
            RawReferenceImage(
                reference_id=0,
                reference_image=GenAIImage(image_bytes=img.read_bytes(), mime_type=mime),
            )
        ],
        config=EditImageConfig(
            edit_mode="EDIT_MODE_DEFAULT",
            number_of_images=1,
            output_mime_type="image/png",
        ),
    )

    response.generated_images[0].image.save(args.output)
    print(f"Saved: {args.output}")


if __name__ == "__main__":
    main()

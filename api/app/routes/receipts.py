import json
import os

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from google import genai
from google.genai import types

from app.middleware import get_current_user

router = APIRouter()

_MAX_BYTES = 5 * 1024 * 1024  # 5 MB

_PARSE_PROMPT = """
You are a receipt parsing assistant for a Philippine Peso (PHP) finance tracker.
Extract the fields below from this receipt image and return ONLY valid JSON — no markdown fences, no extra text.

{
  "merchant": "string or null",
  "total": "number in PHP or null",
  "date": "YYYY-MM-DD string or null",
  "items": [{"name": "string", "amount": "number in PHP"}],
  "currency": "PHP"
}

If a field cannot be determined, use null. All monetary values must be in Philippine Peso (PHP).
""".strip()


def _gemini_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gemini API key not configured",
        )
    return genai.Client(api_key=api_key)


@router.post("/parse")
async def parse_receipt(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
) -> dict:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must be an image (jpeg, png, webp, heic)",
        )

    raw_bytes: bytes = await file.read()

    if len(raw_bytes) > _MAX_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Image must be under 5 MB",
        )

    client = _gemini_client()
    image_part = types.Part.from_bytes(data=raw_bytes, mime_type=file.content_type)

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[_PARSE_PROMPT, image_part],
        )
        parsed: dict = json.loads(response.text.strip())
        return {"success": True, "data": parsed}
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Model returned non-JSON response: {exc}",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Receipt parsing failed: {exc}",
        )

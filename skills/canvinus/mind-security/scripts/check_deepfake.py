#!/usr/bin/env python3
"""
check_deepfake.py — Deepfake / AI-generated media detection via BitMind API.

Requires BITMIND_API_KEY environment variable.
Get your key at https://app.bitmind.ai/api/keys

Usage:
    python3 check_deepfake.py <image_path_or_url>
    python3 check_deepfake.py photo.jpg
    python3 check_deepfake.py https://example.com/image.png

No pip dependencies — uses Python stdlib only.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request


# ---------------------------------------------------------------------------
# BitMind API integration
# ---------------------------------------------------------------------------

BITMIND_API_BASE = "https://api.bitmind.ai"


def _detect_url(image_url: str, api_key: str) -> dict:
    """Send an image URL to BitMind for deepfake detection."""
    endpoint = f"{BITMIND_API_BASE}/detect-image"
    payload = json.dumps({"image": image_url}).encode()
    req = urllib.request.Request(
        endpoint,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode() if exc.fp else ""
        return {"error": f"HTTP {exc.code}", "detail": body}
    except urllib.error.URLError as exc:
        return {"error": "connection_failed", "detail": str(exc.reason)}


def _detect_file(file_path: str, api_key: str) -> dict:
    """Upload a local image file to BitMind for deepfake detection."""
    endpoint = f"{BITMIND_API_BASE}/detect-image"
    boundary = "----MindSecBoundary9876543210"

    filename = os.path.basename(file_path)
    ext = os.path.splitext(filename)[1].lower()
    mime_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".bmp": "image/bmp",
        ".tiff": "image/tiff",
        ".tif": "image/tiff",
        ".avif": "image/avif",
    }
    content_type = mime_types.get(ext, "application/octet-stream")

    with open(file_path, "rb") as f:
        file_data = f.read()

    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="image"; filename="{filename}"\r\n'
        f"Content-Type: {content_type}\r\n\r\n"
    ).encode() + file_data + f"\r\n--{boundary}--\r\n".encode()

    req = urllib.request.Request(
        endpoint,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        body_text = exc.read().decode() if exc.fp else ""
        return {"error": f"HTTP {exc.code}", "detail": body_text}
    except urllib.error.URLError as exc:
        return {"error": "connection_failed", "detail": str(exc.reason)}


def detect(target: str, api_key: str) -> dict:
    """Run deepfake detection via BitMind API."""
    is_url = target.startswith("http://") or target.startswith("https://")

    if is_url:
        raw = _detect_url(target, api_key)
    else:
        if not os.path.isfile(target):
            return {
                "result": "error",
                "confidence": 0.0,
                "error": f"File not found: {target}",
            }
        raw = _detect_file(target, api_key)

    if "error" in raw:
        return {
            "result": "error",
            "confidence": 0.0,
            "error": raw.get("error"),
            "detail": raw.get("detail", ""),
        }

    # API response: {isAI: bool, confidence: float, similarity: float, objectKey: str}
    is_ai = raw.get("isAI", False)
    confidence = raw.get("confidence", 0.0)
    similarity = raw.get("similarity")

    if is_ai:
        result = "ai_generated"
    elif confidence >= 0.4:
        result = "uncertain"
    else:
        result = "authentic"

    return {
        "result": result,
        "isAI": is_ai,
        "confidence": round(confidence, 4),
        "similarity": round(similarity, 4) if similarity is not None else None,
        "api_response": raw,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Detect AI-generated or deepfake images.",
        epilog="Requires BITMIND_API_KEY. Get yours at https://app.bitmind.ai/api/keys",
    )
    parser.add_argument(
        "target",
        help="Image file path or URL to analyze.",
    )
    args = parser.parse_args()

    api_key = os.environ.get("BITMIND_API_KEY", "").strip()

    if not api_key:
        print(
            "Error: BITMIND_API_KEY not set.\n\n"
            "Get your API key:\n"
            "  1. Create an account at https://app.bitmind.ai\n"
            "  2. Go to https://app.bitmind.ai/api/keys\n"
            "  3. Generate a new API key\n\n"
            "Then: export BITMIND_API_KEY=your_key_here",
            file=sys.stderr,
        )
        sys.exit(1)

    result = detect(args.target, api_key)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result.get("result") != "error" else 1)


if __name__ == "__main__":
    main()

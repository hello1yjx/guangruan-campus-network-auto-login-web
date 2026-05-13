from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytesseract
from PIL import Image, ImageFilter, ImageOps


def preprocess_image(image_path: str | Path) -> Image.Image:
    image = Image.open(image_path)
    image = image.convert("L")
    image = ImageOps.autocontrast(image)
    image = image.resize((image.width * 3, image.height * 3))
    image = image.filter(ImageFilter.MedianFilter(size=3))
    image = image.point(lambda pixel: 255 if pixel > 145 else 0)
    return image


def recognize_captcha(image_path: str | Path, ocr_config: dict[str, Any]) -> str:
    tesseract_cmd = ocr_config.get("tesseract_cmd", "").strip()
    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    image = preprocess_image(image_path)
    allowlist = ocr_config.get(
        "allowlist", "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    )
    expected_length = int(ocr_config.get("expected_length", 4))
    custom_config = (
        "--psm 8 "
        "--oem 3 "
        f"-c tessedit_char_whitelist={allowlist}"
    )

    text = pytesseract.image_to_string(image, config=custom_config)
    text = re.sub(r"[^0-9A-Za-z]", "", text)

    if expected_length > 0 and len(text) > expected_length:
        text = text[:expected_length]

    return text

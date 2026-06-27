"""Active Streamlit inference pipeline."""

from __future__ import annotations

import time
from functools import lru_cache
from typing import Any

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

from shared.data_utils import load_train_labels
from solution.streamlit_resolver import BrandProductResolver, clean_text
from team_config import DEFAULT_MIN_CONF


def preprocess(img: Image.Image, max_dim: int = 1440) -> Image.Image:
    img = img.convert("RGB")
    w, h = img.size
    if max(w, h) > max_dim:
        scale = max_dim / max(w, h)
        img = img.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS)
    img = ImageEnhance.Contrast(img).enhance(1.25)
    return img.filter(ImageFilter.SHARPEN)


def postprocess_ocr(text: str) -> str:
    tokens = clean_text(text).split()
    if not tokens:
        return ""
    out = [tokens[0]]
    for token in tokens[1:]:
        if token.lower() != out[-1].lower():
            out.append(token)
    return clean_text(" ".join(out))


@lru_cache(maxsize=1)
def get_ocr_reader():
    try:
        import easyocr
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("EasyOCR is missing. Install with `pip install -r requirements.txt`.") from exc
    return easyocr.Reader(["vi", "en"], gpu=False, verbose=False)


def run_ocr_on_image(img: Image.Image, reader, min_conf: float = DEFAULT_MIN_CONF) -> str:
    image = preprocess(img)
    try:
        rows = reader.readtext(np.array(image), detail=1, paragraph=False)
    except Exception:
        return ""

    def sort_key(row: Any) -> tuple[float, float]:
        box = row[0]
        return (min(point[1] for point in box), min(point[0] for point in box))

    texts: list[str] = []
    for _box, text, conf in sorted(rows, key=sort_key):
        if conf is not None and float(conf) >= min_conf:
            cleaned = clean_text(text)
            if cleaned:
                texts.append(cleaned)
    return postprocess_ocr(" ".join(texts))


@lru_cache(maxsize=1)
def _resolver() -> BrandProductResolver:
    return BrandProductResolver(load_train_labels())


def predict_from_text(ocr_text: str) -> tuple[str, str]:
    return _resolver().extract(ocr_text or "")


def predict_from_image(
    img: Image.Image,
    min_conf: float = DEFAULT_MIN_CONF,
    *,
    include_timing: bool = True,
) -> dict[str, Any]:
    t0 = time.perf_counter()
    t_ocr = time.perf_counter()
    ocr_text = run_ocr_on_image(img, get_ocr_reader(), min_conf)
    ocr_ms = (time.perf_counter() - t_ocr) * 1000

    t_extract = time.perf_counter()
    brand, product = predict_from_text(ocr_text)
    extract_ms = (time.perf_counter() - t_extract) * 1000

    result: dict[str, Any] = {
        "ocr_text": ocr_text,
        "brand_name": brand,
        "product_name": product,
    }
    if include_timing:
        result["timing_ms"] = {
            "ocr": round(ocr_ms, 1),
            "extract": round(extract_ms, 1),
            "total": round((time.perf_counter() - t0) * 1000, 1),
        }
    return result

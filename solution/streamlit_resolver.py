"""Category-neutral brand/product resolver for Streamlit inference."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Iterable

import pandas as pd

SPACE_RE = re.compile(r"\s+")
WORD_RE = re.compile(r"[0-9A-Za-zÀ-ỹ+&.'/-]+", re.UNICODE)

SOURCE_MEDIA = {
    "cafef",
    "vtv",
    "tap news",
    "tiktok",
    "thanh nien",
    "thanh niên",
    "antv",
    "breaking news",
    "music vinyl",
    "logo finance x",
    "ometv",
    "laptop",
    "dramatic",
    "epic dm production",
}

NOISE_WORDS = {
    "sale",
    "freeship",
    "flash",
    "combo",
    "mua",
    "tặng",
    "tang",
    "giảm",
    "giam",
    "giá",
    "gia",
    "chỉ",
    "chi",
    "còn",
    "con",
    "official",
    "news",
    "follow",
    "hashtag",
    "livestream",
    "video",
    "review",
}

UNIT_WORDS = {"ml", "l", "g", "kg", "hộp", "hop", "lon", "thùng", "thung", "chai", "bịch", "bich", "gói", "goi"}
GENERIC_WORDS = {"sản", "san", "phẩm", "pham", "hàng", "hang", "thương", "thuong", "hiệu", "hieu", "thiết", "thiet", "kế", "ke", "không", "khong", "gian"}
PRODUCT_CONTEXT_WORDS = {
    "baby", "bánh", "banh", "body", "bột", "bot", "cafe", "coffee", "cream", "da",
    "dầu", "dau", "gel", "grow", "kem", "kẹo", "keo", "milk", "mì", "mi",
    "nan", "nước", "nuoc", "organic", "pate", "patê", "plus", "serum", "skin",
    "smoothie", "sữa", "sua", "tắm", "tam", "tẩy", "tay", "tea", "trà",
    "tra", "vitamin", "wash",
}

DEFAULT_BRAND_ALIASES: dict[str, str] = {
    "abbott": "Abbott",
    "aptamil": "Aptamil",
    "arla": "ARLA",
    "ba vi": "Ba Vì",
    "ba vì": "Ba Vì",
    "bavi": "Ba Vì",
    "beba": "BEBA",
    "big hug": "BigHug",
    "bighug": "BigHug",
    "canfoco": "Ha Long Canfoco",
    "cerave": "CeraVe",
    "clear": "Clear",
    "cocoon": "Cocoon",
    "colgate": "Colgate",
    "comfort": "Comfort",
    "dove": "Dove",
    "downy": "Downy",
    "dutch lady": "Dutch Lady",
    "dutchlady": "Dutch Lady",
    "ensure": "Abbott Ensure",
    "fami": "Fami",
    "friso": "Friso",
    "ha long canfoco": "Ha Long Canfoco",
    "halong canfoco": "Ha Long Canfoco",
    "hada labo": "Hada Labo",
    "head and shoulders": "Head & Shoulders",
    "head shoulders": "Head & Shoulders",
    "hipp": "HiPP",
    "huggies": "Huggies",
    "johnson": "Johnson's",
    "kotex": "Kotex",
    "lifebuoy": "Lifebuoy",
    "loreal": "L'Oréal",
    "l'oréal": "L'Oréal",
    "milo": "Nestlé Milo",
    "nestle": "Nestlé",
    "nestlé": "Nestlé",
    "nivea": "Nivea",
    "nutifood": "Nutifood",
    "olay": "OLAY",
    "omo": "OMO",
    "pantene": "Pantene",
    "pediasure": "Abbott PediaSure",
    "pond's": "POND'S",
    "ponds": "POND'S",
    "p/s": "P/S",
    "ps": "P/S",
    "romano": "Romano",
    "senka": "Senka",
    "similac": "Abbott Similac",
    "simple": "Simple",
    "sunsilk": "Sunsilk",
    "th true": "TH True Milk",
    "th true milk": "TH True Milk",
    "vaseline": "Vaseline",
    "vinamilk": "Vinamilk",
    "vissan": "Vissan",
    "yomost": "Yomost",
}


@dataclass(frozen=True)
class CandidateLabel:
    brand: str
    product_line: str
    full_label: str
    norm_full: str
    norm_line: str


def strip_diacritics(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")


def clean_text(text: object) -> str:
    if text is None:
        return ""
    text = unicodedata.normalize("NFC", str(text))
    text = re.sub(r"[\r\n\t]+", " ", text)
    return SPACE_RE.sub(" ", text).strip()


def norm_text(text: object) -> str:
    text = strip_diacritics(clean_text(text)).lower()
    text = re.sub(r"[^0-9a-z+&.'/-]+", " ", text)
    return SPACE_RE.sub(" ", text).strip()


def _tokens(text: str) -> list[str]:
    return WORD_RE.findall(clean_text(text))


def _contains_source_media(norm: str) -> bool:
    return any(term in norm for term in SOURCE_MEDIA)


def _has_product_context(norm: str) -> bool:
    return bool(set(norm.split()) & {norm_text(t) for t in PRODUCT_CONTEXT_WORDS})


def _is_noise_token(token: str) -> bool:
    n = norm_text(token)
    if not n:
        return True
    if n in NOISE_WORDS or n in UNIT_WORDS or n in GENERIC_WORDS:
        return True
    if re.fullmatch(r"\d+[.,]?\d*", n):
        return True
    return "%" in token


def _dedupe(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        key = norm_text(item)
        if key and key not in seen:
            seen.add(key)
            out.append(clean_text(item))
    return out


def _brand_from_label(label: str, aliases: dict[str, str]) -> str:
    label_norm = norm_text(label)
    best_alias = ""
    best_brand = ""
    for alias, brand in aliases.items():
        alias_norm = norm_text(alias)
        if re.search(rf"\b{re.escape(alias_norm)}\b", label_norm) and len(alias_norm) > len(best_alias):
            best_alias = alias_norm
            best_brand = brand
    return best_brand


def _strip_brand(label: str, brand: str, aliases: dict[str, str]) -> str:
    label_tokens = _tokens(label)
    label_norm = norm_text(label)
    possible = [brand] + [alias for alias, mapped in aliases.items() if mapped == brand]
    best = ""
    for alias in possible:
        alias_norm = norm_text(alias)
        if label_norm.startswith(alias_norm) and len(alias_norm) > len(best):
            best = alias_norm
    if not best:
        return clean_text(label)
    return clean_text(" ".join(label_tokens[len(best.split()) :]))


class BrandProductResolver:
    def __init__(self, train_labels: pd.DataFrame | None = None):
        self.aliases = dict(DEFAULT_BRAND_ALIASES)
        self.candidates: list[CandidateLabel] = []
        if train_labels is not None and "product_name" in train_labels.columns:
            self._load_train_labels(train_labels)

    def _load_train_labels(self, train_labels: pd.DataFrame) -> None:
        labels = _dedupe(value for value in train_labels["product_name"].tolist() if clean_text(value))
        for label in labels:
            if _contains_source_media(norm_text(label)):
                continue
            brand = _brand_from_label(label, self.aliases)
            if not brand:
                continue
            line = _strip_brand(label, brand, self.aliases)
            if not line or norm_text(line) == norm_text(label) or len(norm_text(line).split()) > 8:
                continue
            self.candidates.append(CandidateLabel(brand, line, label, norm_text(label), norm_text(line)))

    def find_brand(self, text: str) -> tuple[str, str] | None:
        text_norm = norm_text(text)
        best: tuple[int, str, str] | None = None
        for alias, brand in self.aliases.items():
            alias_norm = norm_text(alias)
            if re.search(rf"\b{re.escape(alias_norm)}\b", text_norm):
                score = len(alias_norm.split()) * 10 + len(alias_norm)
                if best is None or score > best[0]:
                    best = (score, brand, alias_norm)
        return (best[1], best[2]) if best else None

    def _unknown_brand(self, text: str) -> tuple[str, str] | None:
        text_norm = norm_text(text)
        if _contains_source_media(text_norm) or not _has_product_context(text_norm):
            return None
        tokens = _tokens(text)
        for idx, token in enumerate(tokens[:12]):
            raw = token.strip(".,:;!()[]{}")
            n = norm_text(raw)
            if len(n) < 3 or _is_noise_token(raw) or n in PRODUCT_CONTEXT_WORDS:
                continue
            has_logo_shape = raw.isupper() or (raw[:1].isupper() and not raw.islower())
            nearby_context = any(norm_text(t) in PRODUCT_CONTEXT_WORDS for t in tokens[idx + 1 : idx + 5])
            if has_logo_shape and nearby_context:
                return raw, n
        return None

    def _product_from_train_candidates(self, text: str, brand: str) -> str:
        text_norm = norm_text(text)
        best: tuple[int, str] | None = None
        for cand in self.candidates:
            if cand.brand != brand:
                continue
            if re.search(rf"\b{re.escape(cand.norm_full)}\b", text_norm):
                score = 100 + len(cand.norm_full)
            elif re.search(rf"\b{re.escape(cand.norm_line)}\b", text_norm):
                score = 80 + len(cand.norm_line)
            else:
                continue
            if best is None or score > best[0]:
                best = (score, cand.product_line)
        return best[1] if best else ""

    def _product_after_brand(self, text: str, alias_norm: str) -> str:
        tokens = _tokens(text)
        norm_tokens = [norm_text(t) for t in tokens]
        alias_parts = alias_norm.split()
        start = -1
        for idx in range(0, max(0, len(norm_tokens) - len(alias_parts) + 1)):
            if norm_tokens[idx : idx + len(alias_parts)] == alias_parts:
                start = idx + len(alias_parts)
                break
        if start < 0:
            return ""
        picked: list[str] = []
        for token in tokens[start : start + 8]:
            if _is_noise_token(token):
                if picked:
                    break
                continue
            picked.append(token)
            if len(picked) >= 6:
                break
        line = clean_text(" ".join(picked))
        if not line or all(norm_text(tok) in GENERIC_WORDS for tok in picked):
            return ""
        return line

    def extract(self, ocr_text: str) -> tuple[str, str]:
        text = clean_text(ocr_text)
        if not text:
            return "", ""
        text_norm = norm_text(text)
        if _contains_source_media(text_norm) and not _has_product_context(text_norm):
            return "", ""
        brand_hit = self.find_brand(text) or self._unknown_brand(text)
        if brand_hit is None:
            return "", ""
        brand, alias_norm = brand_hit
        product = self._product_from_train_candidates(text, brand) or self._product_after_brand(text, alias_norm)
        return clean_text(brand), clean_text(product)


def extract_brand_product(ocr_text: str, train_labels: pd.DataFrame | None = None) -> tuple[str, str]:
    return BrandProductResolver(train_labels).extract(ocr_text)


def extract_product(ocr_text: str) -> str:
    return extract_brand_product(ocr_text)[1]

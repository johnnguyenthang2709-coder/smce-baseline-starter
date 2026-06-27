"""Clean Streamlit entrypoint for the SMCE OCR/product resolver."""

from __future__ import annotations

import io

import streamlit as st
from PIL import Image

import team_config as cfg
from shared.benchmark import get_deploy_smoke_benchmark, get_model_profile, run_predict_with_metrics


def _load_uploaded_image(uploaded) -> Image.Image:
    return Image.open(io.BytesIO(uploaded.getvalue())).convert("RGB")


def _render_header() -> None:
    st.set_page_config(page_title=cfg.BROWSER_TITLE, page_icon=str(cfg.FAVICON), layout="wide")
    if cfg.LOGO.exists():
        st.image(str(cfg.LOGO), width=cfg.LOGO_WIDTH)
    st.title(cfg.PAGE_TITLE)
    st.caption(cfg.SUBTITLE)
    st.markdown(
        f"**Team:** {cfg.TEAM_MEMBERS}  \n"
        f"**Repository:** [{cfg.GITHUB_REPO}]({cfg.GITHUB_REPO})"
    )


def _render_profile() -> None:
    profile = get_model_profile()
    smoke = get_deploy_smoke_benchmark()
    with st.expander("Runtime profile", expanded=False):
        st.write(f"**Pipeline:** {profile.get('pipeline', '-')}")
        st.write(f"**Runtime:** {profile.get('runtime_device', '-')}")
        st.write(f"**Product head:** {profile.get('product_head_mb', 0)} MB")
        st.write(profile.get("ocr_backend_note", ""))
        st.write(profile.get("lightweight_notes", ""))
        if smoke.get("latency_ms"):
            lat = smoke["latency_ms"]
            st.write(
                f"Smoke benchmark: total {lat.get('total_avg', '-')} ms, "
                f"OCR {lat.get('ocr_avg', '-')} ms, extract {lat.get('extract_avg', '-')} ms"
            )
        elif smoke.get("error"):
            st.warning(f"Smoke benchmark skipped: {smoke['error']}")


def _render_live_tab() -> None:
    st.subheader("Live image test")
    _render_profile()
    uploaded = st.file_uploader(
        "Upload a product or social-media image",
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=False,
    )
    if not uploaded:
        st.info("Upload an image to run OCR, brand extraction, and product-line extraction.")
        return

    image = _load_uploaded_image(uploaded)
    left, right = st.columns([1, 1])
    with left:
        st.image(image, use_container_width=True)
    with right:
        if st.button("Run inference", type="primary"):
            with st.spinner("Running local OCR and resolver..."):
                pred = run_predict_with_metrics(image)
            timing = pred.get("timing_ms", {})
            c1, c2, c3 = st.columns(3)
            c1.metric("Total ms", f"{timing.get('total', 0):.1f}")
            c2.metric("OCR ms", f"{timing.get('ocr', 0):.1f}")
            c3.metric("Extract ms", f"{timing.get('extract', 0):.1f}")
            st.text_area("ocr_text", value=pred.get("ocr_text", ""), height=160)
            st.text_input("brand_name", value=pred.get("brand_name", ""))
            st.text_input("product_name", value=pred.get("product_name", ""))


def _render_about_tab() -> None:
    st.subheader("Model summary")
    st.markdown(
        """
        This Streamlit version is built for the private live-testing round.

        - Runs local CPU OCR with EasyOCR (`vi` + `en`).
        - Extracts `brand_name` separately from `product_name`.
        - Uses train-label hints without forcing every image into the old public families.
        - Blocks common source/media/UI strings when there is no product evidence.
        - Uses a guarded unknown-brand fallback only when product-context words are visible.

        The batch entrypoint is:

        ```powershell
        python scripts/run_submission.py
        ```
        """
    )
    st.subheader("Output schema")
    st.code("image_id, ocr_text, brand_name, product_name", language="text")


def main() -> None:
    _render_header()
    tab_live, tab_about = st.tabs(["Live test", "About"])
    with tab_live:
        _render_live_tab()
    with tab_about:
        _render_about_tab()


if __name__ == "__main__":
    main()

# Streamlit-Ready Version

This folder has been patched so the main Streamlit entrypoint uses a cleaner
private-round inference pipeline.

Run locally:

```powershell
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Generate a batch submission:

```powershell
python scripts/run_submission.py
```

## Active Pipeline

The active code path is:

```text
streamlit_app.py
-> streamlit_app_clean.py
-> shared/benchmark.py
-> solution.pipeline.predict_from_image
-> solution.streamlit_pipeline
-> solution.streamlit_resolver
```

The old starter pipeline remains in `solution/pipeline.py` for reference, but
the public API is delegated to `solution.streamlit_pipeline`.

## Private-Round Behavior

- CPU-local EasyOCR (`vi` + `en`)
- Separate `brand_name` and `product_name`
- Train-label hints where available
- Source/media/UI blocking
- Guarded unknown-brand fallback
- No hardcoded image-id mappings
- No cached private-test answer table

## Notes

EasyOCR downloads model weights on first use. That can make the first Streamlit
run slower, but later runs reuse the local cache.

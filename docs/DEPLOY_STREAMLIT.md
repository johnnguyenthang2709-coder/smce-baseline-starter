# Deploy Streamlit Community Cloud

Hướng dẫn deploy demo **Live test + About** lên [Streamlit Community Cloud](https://share.streamlit.io) (miễn phí, gắn GitHub).

> **Lưu ý:** Deploy thực hiện trên website Streamlit (không có CLI `streamlit deploy`). Mỗi team fork repo → chỉnh `team_config.py` → push GitHub → tạo app trên Cloud.

---

## 0. Checklist trước khi deploy

| Mục | File / hành động |
|-----|------------------|
| Team name, links, logo | [`team_config.py`](../team_config.py) |
| Solution chạy được local | `streamlit run streamlit_app.py` |
| Dependencies Python | [`requirements.txt`](../requirements.txt) |
| System libs (OpenCV/EasyOCR) | [`packages.txt`](../packages.txt) |
| Python version trên Cloud | [`.python-version`](../.python-version) → `3.11` |
| Repo **public** trên GitHub | Settings → Change visibility |
| Không commit secrets | `.streamlit/secrets.toml` đã gitignore |

---

## 1. Push code lên GitHub

Sau khi fork / clone:

```bash
git add .
git commit -m "Team ABC: ready for Streamlit Cloud"
git push origin main
```

Repo mẫu: `https://github.com/YOUR_USER/ura-hackathon-team-abc`

---

## 2. Tạo tài khoản Streamlit Cloud

1. Mở [share.streamlit.io](https://share.streamlit.io)
2. **Sign in with GitHub**
3. **Authorize** Streamlit truy cập GitHub (chọn repo hoặc all repos tùy team)

---

## 3. Tạo app mới

1. Click **Create app**
2. Điền form:

| Field | Giá trị |
|-------|---------|
| **Repository** | `YOUR_USER/ura-hackathon-team-abc` |
| **Branch** | `main` |
| **Main file path** | `streamlit_app.py` |
| **App URL** (optional) | `ura-team-abc` → `https://ura-team-abc.streamlit.app` |

3. Click **Deploy**

Streamlit sẽ:

- Cài `requirements.txt`
- Cài apt packages từ `packages.txt`
- Chạy `streamlit run streamlit_app.py`

**Lần đầu deploy:** 5–15 phút (download PyTorch + EasyOCR weights). Tab app hiển thị log build.

---

## 4. Kiểm tra sau deploy

1. Mở URL dạng `https://<app-name>.streamlit.app`
2. Xác nhận header: logo, title, subtitle, team links từ `team_config.py`
3. Tab **Live test** → upload ảnh JPG/PNG → **Chạy OCR**
4. Tab **About** → nội dung team

Nếu build fail → xem **Manage app → Logs** (mục 6 bên dưới).

---

## 5. Cập nhật app (redeploy)

Mỗi lần `git push` lên branch đã gắn (thường `main`), Streamlit Cloud **tự rebuild**.

```bash
# ví dụ sau khi sửa solution hoặc team_config
git add team_config.py solution/
git commit -m "Improve OCR pipeline"
git push origin main
```

Theo dõi tiến trình: **Manage app → Activity**.

---

## 6. Xử lý lỗi thường gặp

### Build fail — memory / timeout

Baseline dùng **PyTorch + EasyOCR** (~1 GB+ RAM lúc load). Gói Community Cloud free có giới hạn RAM.

**Cách xử lý:**

- Giữ **Live test** (upload 1 ảnh) — tránh batch lớn trên Cloud
- Thu gọn `requirements.txt` nếu team đổi sang OCR nhẹ hơn (PaddleOCR slim, API-only, …)
- Cân nhắc [Streamlit Teams](https://streamlit.io/cloud) nếu cần thêm RAM

### `libGL.so` / OpenCV import error

Đảm bảo [`packages.txt`](../packages.txt) có:

```text
libgl1
libglib2.0-0
```

Commit và push lại.

### App crash khi bấm **Chạy OCR**

- Lần đầu EasyOCR tải model ~200 MB — đợi 1–2 phút
- Xem **Logs** khi user trigger OCR
- Test local trước: `streamlit run streamlit_app.py`

### Sai tên team / link cũ trên Cloud

Sửa [`team_config.py`](../team_config.py) → push → đợi rebuild (hoặc **Reboot app** trong Manage app).

### Private images (1,202 ảnh)

Cloud **không** bundle full `data/private_test/images/` (gitignored, ~100 MB).

Demo Cloud chỉ dùng tab **Live test → Upload**. Batch submission chạy **local**:

```bash
python scripts/run_submission.py
```

---

## 7. Secrets (tùy chọn)

Nếu solution cần API key (OpenAI, Gemini, …):

**Local:** copy [`.streamlit/secrets.toml.example`](../.streamlit/secrets.toml.example) → `.streamlit/secrets.toml`

**Cloud:** **Manage app → Settings → Secrets**

```toml
OPENAI_API_KEY = "sk-..."
```

Trong code:

```python
import streamlit as st
api_key = st.secrets.get("OPENAI_API_KEY", "")
```

Không commit file secrets.

---

## 8. Custom domain (tùy chọn)

Streamlit Teams / enterprise hỗ trợ custom domain. Community Cloud dùng subdomain mặc định:

`https://<tên-app>.streamlit.app`

---

## 9. Ghi link app vào repo

Sau deploy, thêm URL vào [`team_config.py`](../team_config.py):

```python
STREAMLIT_APP_URL = "https://ura-team-abc.streamlit.app"
```

Và cập nhật README / About tab để BTC / reviewer mở nhanh.

---

## Tóm tắt một dòng

```text
Fork → team_config.py → push GitHub (public) → share.streamlit.io → Create app → streamlit_app.py → Deploy
```

## Tài liệu liên quan

- [Team setup](TEAM_SETUP.md)
- [Submission](SUBMISSION.md)
- [Streamlit Cloud docs](https://docs.streamlit.io/streamlit-community-cloud)

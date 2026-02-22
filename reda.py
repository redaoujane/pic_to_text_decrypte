import re
import numpy as np
import streamlit as st
from PIL import Image
from paddleocr import PaddleOCR

st.set_page_config(page_title="OCR Engine | by trojan", page_icon="📝")

@st.cache_resource
def load_model():
    return PaddleOCR(use_angle_cls=True, lang="en")

ocr = load_model()

def has_arabic(text):
    return bool(re.search(r'[\u0600-\u06FF]', text))

def fix_text(txt):
    if not has_arabic(txt):
        return txt

    t = txt[::-1]

    def keep_ltr(m):
        return m.group(0)[::-1]

    t = re.sub(r'[a-zA-Z0-9]+(?:[\-\.\,\s]+[a-zA-Z0-9]+)*', keep_ltr, t)
    t = t.translate(str.maketrans(')(][}{', '()[]{}'))
    return t

def rebuild_text(res):
    if not res or not res[0]:
        return ""

    items = []

    for r in res[0]:
        pts = r[0]
        txt = r[1][0]

        x = sum(p[0] for p in pts) / 4
        y = sum(p[1] for p in pts) / 4
        h = max(p[1] for p in pts) - min(p[1] for p in pts)

        items.append({
            "t": fix_text(txt),
            "x": x,
            "y": y,
            "h": h
        })

    items.sort(key=lambda i: i["y"])

    lines, line = [], []

    for it in items:
        if not line:
            line.append(it)
        else:
            avg = sum(i["y"] for i in line) / len(line)
            if abs(it["y"] - avg) < it["h"] * 0.6:
                line.append(it)
            else:
                lines.append(line)
                line = [it]

    if line:
        lines.append(line)

    out = []
    for ln in lines:
        ln.sort(key=lambda i: i["x"], reverse=has_arabic(ln[0]["t"]))
        out.append(" ".join(i["t"] for i in ln))

    return "\n".join(out)

st.title("Document OCR Engine 📝")

st.markdown("""
<div style='display:flex; align-items:center; gap:8px; margin-bottom:20px;'>
<span style='color:#555;'>Developed by <b>trojan</b></span>
<a href='https://www.linkedin.com/in/redaoujane/' target='_blank'>
<img src='https://cdn-icons-png.flaticon.com/512/174/174857.png' width='20'>
</a>
</div>
""", unsafe_allow_html=True)

file = st.file_uploader("Choose image", type=["png", "jpg", "jpeg"])

if file:
    img = Image.open(file)
    st.image(img, use_container_width=True)

    if st.button("Extract Text"):
        with st.spinner("processing..."):
            arr = np.array(img.convert("RGB"))
            res = ocr.ocr(arr)

            final = rebuild_text(res)

            if final.strip():
                st.success("Done")

                st.markdown(f"""
                <div style="font-size:18px; padding:15px; border:1px solid #ddd;
                border-radius:6px; background:#f7f7f7; white-space:pre-wrap;">
                {final}
                </div>
                """, unsafe_allow_html=True)

                st.text_area("Text:", final, height=150)
            else:
                st.warning("No text found")

st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#888; font-size:13px; margin-top:10px;'>
© 2026 OCR Engine. All rights reserved by
<a href='https://www.linkedin.com/in/redaoujane/' target='_blank'
style='color:#0A66C2; font-weight:bold; text-decoration:none;'>trojan</a>.
</div>
""", unsafe_allow_html=True)
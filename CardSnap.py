import streamlit as st
from PIL import Image
import io
import base64
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

# ── Page configuration ───────────────────────────────────────────────────────
st.set_page_config(page_title="CardSnap", page_icon="🪪", layout="centered", initial_sidebar_state="collapsed")

# ── Mobile-friendly CSS ──────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
* { font-family: 'Inter', sans-serif; }

/* Responsive container */
.block-container { padding: 1rem 1rem 3rem; max-width: 600px; }

/* Header */
.header { text-align: center; padding: 1.5rem 1rem; margin-bottom: 1rem; }
.header h1 { font-size: 1.6rem; font-weight: 700; color: #1e293b; margin: 0 0 0.3rem; }
.header p  { color: #64748b; font-size: 0.85rem; margin: 0; }

/* Upload label */
.upload-label {
    font-size: 0.9rem; font-weight: 600; color: #334155;
    margin: 1rem 0 0.3rem; display: block;
}

/* Buttons */
.stButton > button {
    background: #2563eb !important; color: white !important;
    border: none !important; border-radius: 10px !important;
    padding: 0.75rem !important; font-weight: 600 !important;
    font-size: 1rem !important; width: 100% !important;
}
.stDownloadButton > button {
    background: #059669 !important; color: white !important;
    border: none !important; border-radius: 10px !important;
    padding: 0.75rem !important; font-weight: 600 !important;
    font-size: 1rem !important; width: 100% !important;
}

/* File uploader */
[data-testid="stFileUploadDropzone"] {
    border: 2px dashed #cbd5e1 !important; border-radius: 10px !important;
    padding: 1rem !important;
}

/* Metric cards */
[data-testid="stMetric"] {
    background: #1e293b; border-radius: 8px; padding: 0.5rem;
    text-align: center;
}
[data-testid="stMetricValue"] { color: #e2e8f0 !important; }
[data-testid="stMetricLabel"] { color: #94a3b8 !important; }

/* Hide hamburger menu and footer for cleaner mobile experience */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  CORE FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def resize_pil(pil_img, max_width=800):
    """Resize image so width ≤ max_width, preserving aspect ratio."""
    w, h = pil_img.size
    if w <= max_width:
        return pil_img
    scale = max_width / w
    return pil_img.resize((max_width, int(h * scale)), Image.LANCZOS)


def create_pdf(front_pil, back_pil, target_kb=200):
    """
    A4 portrait PDF. Each card rendered at max 86mm wide, height auto based on
    image aspect ratio. Compresses JPEG quality from 70→20 until ≤ target_kb.
    """
    A4_W, A4_H = A4
    max_card_w = 86 * mm   # max width for card on page
    max_card_h = 80 * mm   # max height cap to prevent overflow
    gap = 12 * mm

    def card_dims(pil_img):
        """Calculate card dimensions preserving aspect ratio, fitting within max bounds."""
        w, h = pil_img.size
        scale = min(max_card_w / w, max_card_h / h)
        return w * scale, h * scale

    for quality in [70, 60, 50, 40, 30, 20]:
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=A4)
        c.setTitle("ID Card"); c.setAuthor(""); c.setSubject(""); c.setCreator("")

        if front_pil and back_pil:
            fw, fh = card_dims(front_pil)
            bw, bh = card_dims(back_pil)

            # Front (upper) — centered, shifted toward top
            fx = (A4_W - fw) / 2
            fy = A4_H / 2 + gap / 2 + 120
            f_buf = io.BytesIO()
            front_pil.convert("RGB").save(f_buf, "JPEG", quality=quality, optimize=True)
            f_buf.seek(0)
            c.drawInlineImage(Image.open(f_buf), fx, fy, fw, fh)

            # Back (lower) — centered
            bx = (A4_W - bw) / 2
            by = fy - gap - bh
            b_buf = io.BytesIO()
            back_pil.convert("RGB").save(b_buf, "JPEG", quality=quality, optimize=True)
            b_buf.seek(0)
            c.drawInlineImage(Image.open(b_buf), bx, by, bw, bh)
        else:
            # Single image centered, shifted up
            img = front_pil if front_pil else back_pil
            iw, ih = card_dims(img)
            ix = (A4_W - iw) / 2
            iy = (A4_H - ih) / 2 + 120
            i_buf = io.BytesIO()
            img.convert("RGB").save(i_buf, "JPEG", quality=quality, optimize=True)
            i_buf.seek(0)
            c.drawInlineImage(Image.open(i_buf), ix, iy, iw, ih)

        c.save()
        size_kb = len(buf.getvalue()) / 1024
        if size_kb <= target_kb:
            return buf.getvalue(), size_kb, quality

    return buf.getvalue(), size_kb, quality


def load_pil(uploaded_file):
    """Load uploaded file as PIL RGB image."""
    uploaded_file.seek(0)
    return Image.open(uploaded_file).convert("RGB")


# ══════════════════════════════════════════════════════════════════════════════
#  UI — Simple & Mobile Friendly
# ══════════════════════════════════════════════════════════════════════════════

# Header
st.markdown("""
<div class="header">
    <h1>🪪 CardSnap</h1>
    <p>Upload front & back → Get print-ready PDF under 200 KB</p>
</div>
""", unsafe_allow_html=True)

# ── Upload section (stacked for mobile) ──────────────────────────────────────
st.markdown('<span class="upload-label">📷 Front Side</span>', unsafe_allow_html=True)
front_file = st.file_uploader("front", type=["jpg","jpeg","png"], key="front", label_visibility="collapsed")

st.markdown('<span class="upload-label">📷 Back Side (optional)</span>', unsafe_allow_html=True)
back_file = st.file_uploader("back", type=["jpg","jpeg","png"], key="back", label_visibility="collapsed")

# ── Previews ─────────────────────────────────────────────────────────────────
if front_file or back_file:
    cols = st.columns(2)
    if front_file:
        front_file.seek(0)
        cols[0].image(front_file, caption="Front", use_container_width=True)
        front_file.seek(0)
    if back_file:
        back_file.seek(0)
        cols[1].image(back_file, caption="Back", use_container_width=True)
        back_file.seek(0)

# ── Generate button ──────────────────────────────────────────────────────────
st.markdown("")
custom_name = st.text_input("📝 File name (optional)", placeholder="e.g. aadhaar_rahul", label_visibility="visible")
generate = st.button("⚡ Generate PDF", use_container_width=True)

# ── Processing ───────────────────────────────────────────────────────────────
if generate:
    if not front_file and not back_file:
        st.error("⚠️ Upload at least one image.")
    else:
        with st.spinner("Generating PDF…"):
            front_pil = resize_pil(load_pil(front_file), max_width=800) if front_file else None
            back_pil  = resize_pil(load_pil(back_file),  max_width=800) if back_file else None
            pdf_bytes, final_kb, quality_used = create_pdf(front_pil, back_pil)

        # Auto-download via JS
        timestamp = datetime.now().strftime('%S%H%M_%d%m')
        if custom_name.strip():
            filename = f"{custom_name.strip()}_{timestamp}.pdf"
        else:
            filename = f"idcard_{timestamp}.pdf"
        b64_pdf = base64.b64encode(pdf_bytes).decode()
        st.components.v1.html(f'''
            <script>
                var a = document.createElement('a');
                a.href = 'data:application/pdf;base64,{b64_pdf}';
                a.download = '{filename}';
                a.click();
            </script>
        ''', height=0)

        # Results
        st.success(f"✅ Done! PDF size: **{final_kb:.1f} KB**")

        col1, col2 = st.columns(2)
        col1.metric("📦 Size", f"{final_kb:.1f} KB")
        col2.metric("🎨 Quality", str(quality_used))

        # Manual fallback download
        st.download_button("⬇️ Download PDF", data=pdf_bytes, file_name=filename,
                           mime="application/pdf", use_container_width=True)

# Footer
st.markdown("""
<div style="text-align:center; color:#94a3b8; font-size:0.75rem; margin-top:2rem;">
    Aadhaar · Voter ID · PAN · DL · Any Card<br>
    Processed locally · Nothing uploaded to server
</div>
""", unsafe_allow_html=True)

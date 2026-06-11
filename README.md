# 🪪 CardSnap

**CardSnap** is a mobile-friendly web app that converts ID card photos into a compact, print-ready A4 PDF — all under 200 KB. Upload the front and back of any card, and get an auto-download in seconds.

🔗 **Live Demo:** [card-snap-two.vercel.app](https://card-snap-two.vercel.app)

---

## ✨ Features

- 📷 Upload front and/or back of any ID card (JPG, JPEG, PNG)
- 📄 Generates a clean A4 portrait PDF with both sides laid out
- 📦 Auto-compresses output to ≤ 200 KB using adaptive JPEG quality
- 📝 Custom filename support with auto-generated timestamp suffix
- ⚡ Auto-download triggered on PDF generation
- 🔒 Processed entirely in-browser — nothing uploaded to any server
- 📱 Responsive, mobile-friendly UI built with Streamlit

---

## 🗂️ Supported Cards

- Aadhaar Card
- PAN Card
- Voter ID
- Driving Licence
- Any other photo ID card

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+

### Installation

```bash
git clone https://github.com/rahulbiswas12/CardSnap.git
cd CardSnap
pip install -r requirements.txt
```

### Run Locally

```bash
streamlit run CardSnap.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 📦 Dependencies

```
streamlit
Pillow
reportlab
```

---

## 🧠 How It Works

1. Upload front (and optionally back) image of your ID card.
2. Images are resized to a max width of 800px preserving aspect ratio.
3. Both images are rendered onto a single A4 page using ReportLab.
4. JPEG quality is progressively reduced (70 → 20) until the PDF is ≤ 200 KB.
5. The PDF auto-downloads with a timestamped filename.

---

## 📁 Project Structure

```
CardSnap/
├── CardSnap.py        # Main Streamlit app
├── requirements.txt   # Python dependencies
└── .devcontainer/     # Dev container config (GitHub Codespaces)
```

---

## 🛡️ Privacy

All image processing happens locally in your session. No images or data are sent to any external server.

---

## 👤 Author

**Rahul Biswas**
🌐 [rahulbiswas-nine.vercel.app](https://rahulbiswas-nine.vercel.app)
🐙 [@rahulbiswas12](https://github.com/rahulbiswas12)

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

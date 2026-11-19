# ✍️ Photo to Font

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Photo to Font** is an open-source web application that turns a photograph of your handwriting or hand-drawn letters into a real, installable TrueType vector font (`.ttf`).

Draw your letters on the printable grid template, snap a photo with your phone, upload it to the web app, test your font live in the browser, and download the `.ttf` file ready for Windows, macOS, iOS, Android, Figma, or Photoshop.

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/ai-entusiastik/photo-to-font)

---

## ✨ Features

- **Automatic Perspective Correction:** Uses OpenCV to detect the four corner registration markers on the template sheet and flatten tilted or angled photos automatically.
- **Shadow & Noise Removal:** Adaptive thresholding cleans uneven lighting and paper shadows so only crisp ink strokes remain.
- **Smooth Vector Tracing:** Converts raster bitmaps into scalable vector outlines (SVG) via **Potrace**.
- **TrueType Font Compilation:** Packages vector glyphs into a valid `.ttf` font file with proper glyph metrics using **fontTools**.
- **Live Browser Preview:** Instantly test your generated font in an interactive text box before downloading.
- **Zero-Config Cloud & Docker Support:** Run in one click via GitHub Codespaces or locally with Docker.

---

## 🚀 Quick Start

### Option 1: Run in Your Browser (GitHub Codespaces — No Installation)
Click the **"Open in GitHub Codespaces"** badge at the top of this page. GitHub will automatically build the container, start the server, and open the web interface in your browser within ~30 seconds.

### Option 2: Run Locally with Docker (Recommended)
No need to install Python, OpenCV, or Potrace manually:

    git clone https://github.com/ai-entusiastik/photo-to-font.git
    cd photo-to-font
    docker build -t photo-to-font .
    docker run -p 8000:8000 photo-to-font

Open **http://localhost:8000** in your browser.

### Option 3: Local Setup (Python)

1. **Clone the repository:**

       git clone https://github.com/ai-entusiastik/photo-to-font.git
       cd photo-to-font

2. **Install Potrace (vectorization engine):**
   - **macOS:** `brew install potrace`
   - **Ubuntu / Debian:** `sudo apt update && sudo apt install potrace`
   - **Windows:** Download the Windows binary from [Potrace SourceForge](https://potrace.sourceforge.net/), extract `potrace.exe`, and place it inside `photo-to-font/bin/potrace.exe` (no admin rights required).

3. **Create a virtual environment and install dependencies:**

       python -m venv venv
       # Activate on macOS/Linux:
       source venv/bin/activate
       # Activate on Windows (PowerShell):
       .\venv\Scripts\Activate.ps1
       pip install -r requirements.txt

4. **Start the web server:**

       python -m uvicorn app.main:app --reload

   Open **http://127.0.0.1:8000** in your browser.

---

## 📖 How to Use

1. **Download the Template:** Open the web app and click **Download Grid Template** to get `font_template.png`.
2. **Fill Out the Grid:** Print the template (or open it in a drawing app on an iPad/tablet) and write each character (`A–Z`, `0–9`) inside its corresponding box using a **thick black marker or dark pen**.
   - *Tip:* Avoid touching the light-gray guide letter in the top-left corner of each cell.
3. **Take a Photo:** Capture a clear, well-lit photo of the entire sheet. Make sure all **four black corner squares** are visible in the frame.
4. **Generate & Download:** Enter a name for your font, upload the photo, and click **Generate Font (.ttf)**. Type in the preview box to test your letters, then click **Download .ttf File**.

---

## 🧠 How It Works Under the Hood

    [ Uploaded Photo ]
            │
            ▼
    1. OpenCV (warp_to_template)
       Detects 4 black corner markers -> applies perspective transform -> flattens image
            │
            ▼
    2. OpenCV (adaptiveThreshold)
       Removes shadows & grid lines -> slices individual character cells
            │
            ▼
    3. Potrace
       Traces each black-and-white character bitmap into smooth SVG vector paths
            │
            ▼
    4. fontTools (FontBuilder)
       Converts cubic Bézier curves to quadratic TrueType outlines -> builds .ttf file

---

## 📁 Project Structure

    photo-to-font/
    ├── app/
    │   ├── __init__.py          # Package initializer
    │   ├── main.py              # FastAPI server & web UI endpoints
    │   ├── processor.py         # Image alignment, Potrace vectorization & TTF builder
    │   └── template_gen.py      # Printable grid template generator
    ├── static/                  # Generated template and static assets
    ├── .devcontainer/
    │   └── devcontainer.json    # One-click GitHub Codespaces configuration
    ├── Dockerfile               # Container setup with Python & Potrace pre-installed
    ├── requirements.txt         # Python dependencies
    ├── .gitignore              # Ignored local/temporary files
    └── README.md                # Project documentation

---

## 🤝 Contributing

Contributions, bug reports, and feature ideas are welcome! Feel free to open an issue or submit a pull request. Ideas for future improvements:
- Support for lowercase letters (`a–z`) and punctuation marks
- Automatic baseline alignment and dynamic glyph kerning/spacing
- Direct drawing canvas in the browser alongside photo upload

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).

Open http://localhost:8000 in your browser.



Option 3: Local Setup (Python)

Clone the repository:



Bash

git clone \[https://github.com/ai-entusiastik/photo-to-font.git](https://github.com/YOUR\_USERNAME/photo-to-font.git)

cd photo-to-font

Install Potrace (vectorization engine):



macOS: brew install potrace



Ubuntu / Debian: sudo apt update \&\& sudo apt install potrace



Windows: Download the Windows binary from Potrace SourceForge, extract potrace.exe, and place it inside photo-to-font/bin/potrace.exe (no admin rights required).



Create a virtual environment and install dependencies:



Bash

python -m venv venv



\# Activate on macOS/Linux:

source venv/bin/activate



\# Activate on Windows (PowerShell):

.\\venv\\Scripts\\Activate.ps1



pip install -r requirements.txt

Start the web server:



Bash

python -m uvicorn app.main:app --reload

Open http://127.0.0.1:8000 in your browser.



📖 How to Use

Download the Template: Open the web app and click Download Grid Template to get font\_template.png.



Fill Out the Grid: Print the template (or open it in a drawing app on an iPad/tablet) and write each character (A–Z, 0–9) inside its corresponding box using a thick black marker or dark pen.



Tip: Avoid touching the light-gray guide letter in the top-left corner of each cell.



Take a Photo: Capture a clear, well-lit photo of the entire sheet. Make sure all four black corner squares are visible in the frame.



Generate \& Download: Enter a name for your font, upload the photo, and click Generate Font (.ttf). Type in the preview box to test your letters, then click Download .ttf File.



🧠 How It Works Under the Hood

Plaintext

\[ Uploaded Photo ]

&#x20;       │

&#x20;       ▼

1\. OpenCV (warp\_to\_template)

&#x20;  Detects 4 black corner markers → applies perspective transform → flattens image

&#x20;       │

&#x20;       ▼

2\. OpenCV (adaptiveThreshold)

&#x20;  Removes shadows \& grid lines → slices individual character cells

&#x20;       │

&#x20;       ▼

3\. Potrace

&#x20;  Traces each black-and-white character bitmap into smooth SVG vector paths

&#x20;       │

&#x20;       ▼

4\. fontTools (FontBuilder)

&#x20;  Converts cubic Bézier curves to quadratic TrueType outlines → builds .ttf file

📁 Project Structure

Plaintext

photo-to-font/

├── app/

│   ├── \_\_init\_\_.py          # Package initializer

│   ├── main.py              # FastAPI server \& web UI endpoints

│   ├── processor.py         # Image alignment, Potrace vectorization \& TTF builder

│   └── template\_gen.py      # Printable grid template generator

├── static/                  # Generated template and static assets

├── .devcontainer/

│   └── devcontainer.json    # One-click GitHub Codespaces configuration

├── Dockerfile               # Container setup with Python \& Potrace pre-installed

├── requirements.txt         # Python dependencies

├── .gitignore               # Ignored local/temporary files

└── README.md                # Project documentation

🤝 Contributing

Contributions, bug reports, and feature ideas are welcome! Feel free to open an issue or submit a pull request. Ideas for future improvements:



Support for lowercase letters (a–z) and punctuation marks



Automatic baseline alignment and dynamic glyph kerning/spacing



Direct drawing canvas in the browser alongside photo upload


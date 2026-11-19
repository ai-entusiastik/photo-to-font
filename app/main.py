from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from app.processor import image_to_ttf
from app.template_gen import generate_template
import os

app = FastAPI(title="Photo to Font Generator")

os.makedirs("static", exist_ok=True)
generate_template("static/template.png")

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Photo to Font — Turn Your Handwriting Into a Real Font</title>
    <style>
        body { font-family: system-ui, -apple-system, sans-serif; max-width: 680px; margin: 40px auto; padding: 20px; background: #f9fafb; color: #111827; }
        .card { background: white; padding: 24px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.06); margin-bottom: 20px; }
        h1 { margin-top: 0; }
        .btn { display: inline-block; background: #2563eb; color: white; padding: 10px 18px; border-radius: 8px; text-decoration: none; border: none; cursor: pointer; font-size: 16px; }
        .btn:hover { background: #1d4ed8; }
        .btn-outline { background: white; color: #2563eb; border: 1px solid #2563eb; }
        .btn-outline:hover { background: #eff6ff; }
        input[type="text"], input[type="file"] { display: block; width: 100%; margin: 12px 0 20px; padding: 10px; border: 1px solid #d1d5db; border-radius: 8px; box-sizing: border-box; }
        #preview-box { display: none; margin-top: 20px; }
        textarea { width: 100%; height: 100px; font-size: 28px; padding: 12px; border-radius: 8px; border: 1px solid #d1d5db; box-sizing: border-box; }
    </style>
</head>
<body>
    <div class="card">
        <h1>Photo to Font</h1>
        <p>Turn a photo of your handwriting or drawn letters into a real, installable vector font (<code>.ttf</code>).</p>
        <p><strong>Step 1:</strong> Download the grid template, print it out (or open it on a tablet), and draw each letter with a black marker.</p>
        <a href="/download-template" class="btn btn-outline">Download Grid Template</a>
    </div>

    <div class="card">
        <p><strong>Step 2:</strong> Upload a photo of the filled template.</p>
        <form id="uploadForm">
            <label>Font Name:</label>
            <input type="text" name="font_name" value="MyHandwriting" required>
            
            <label>Photo of Your Letters:</label>
            <input type="file" name="file" accept="image/*" required>
            
            <button type="submit" class="btn">Generate Font (.ttf)</button>
        </form>

        <div id="preview-box">
            <h3>Done! Test your custom font right here:</h3>
            <textarea id="test-area" placeholder="Type uppercase letters to test...">HELLO WORLD 2026</textarea>
            <br><br>
            <a id="download-link" class="btn">Download .ttf File</a>
        </div>
    </div>

    <script>
        document.getElementById('uploadForm').onsubmit = async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const btn = e.target.querySelector('button');
            btn.textContent = 'Processing...';
            btn.disabled = true;

            const res = await fetch('/generate-font', { method: 'POST', body: formData });
            if (!res.ok) {
                alert('Server error while generating the font! Check the terminal output.');
                btn.textContent = 'Generate Font (.ttf)';
                btn.disabled = false;
                return;
            }
            const blob = await res.blob();
            const url = URL.createObjectURL(blob);

            const fontFace = new FontFace('CustomGeneratedFont', 'url(' + url + ')');
            await fontFace.load();
            document.fonts.add(fontFace);

            document.getElementById('test-area').style.fontFamily = 'CustomGeneratedFont, sans-serif';

            const dl = document.getElementById('download-link');
            dl.href = url;
            dl.download = formData.get('font_name') + '.ttf';

            document.getElementById('preview-box').style.display = 'block';
            btn.textContent = 'Generate Font (.ttf)';
            btn.disabled = false;
        };
    </script>
</body>
</html>"""

with open("static/index.html", "w", encoding="utf-8") as f:
    f.write(HTML_PAGE)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML_PAGE


@app.get("/download-template")
async def download_template():
    return FileResponse("static/template.png", filename="font_template.png")


@app.post("/generate-font")
async def create_font(file: UploadFile = File(...), font_name: str = Form("MyHandwriting")):
    image_bytes = await file.read()
    ttf_path = image_to_ttf(image_bytes, font_name)
    return FileResponse(ttf_path, filename=f"{font_name}.ttf", media_type="font/ttf")

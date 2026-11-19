from PIL import Image, ImageDraw
import os

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
COLS = 6
ROWS = 6
CELL_SIZE = 200
MARGIN = 60


def generate_template(output_path: str = "static/template.png"):
    width = COLS * CELL_SIZE + MARGIN * 2
    height = ROWS * CELL_SIZE + MARGIN * 2 + 60

    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)

    # Corner markers (black squares for automatic perspective alignment)
    marker_size = 30
    corners = [
        (15, 15),
        (width - 15 - marker_size, 15),
        (15, height - 15 - marker_size),
        (width - 15 - marker_size, height - 15 - marker_size)
    ]
    for x, y in corners:
        draw.rectangle([x, y, x + marker_size, y + marker_size], fill="black")

    draw.text((MARGIN, 20), "Write each character inside its box using a black marker:", fill="black")

    for idx, char in enumerate(ALPHABET):
        row = idx // COLS
        col = idx % COLS
        x0 = MARGIN + col * CELL_SIZE
        y0 = MARGIN + 40 + row * CELL_SIZE
        x1 = x0 + CELL_SIZE
        y1 = y0 + CELL_SIZE

        # Cell border
        draw.rectangle([x0, y0, x1, y1], outline="#CCCCCC", width=2)
        # Character hint in top-left corner
        draw.text((x0 + 10, y0 + 10), char, fill="#888888")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)
    return output_path
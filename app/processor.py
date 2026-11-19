import os
import subprocess
import tempfile
import cv2
import numpy as np
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.svgLib.path import SVGPath
from app.template_gen import ALPHABET, COLS, ROWS, CELL_SIZE, MARGIN


def warp_to_template(gray_img: np.ndarray, expected_w: int, expected_h: int) -> np.ndarray:
    blurred = cv2.GaussianBlur(gray_img, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 80, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    h, w = gray_img.shape
    candidates = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < (w * h) * 0.0002 or area > (w * h) * 0.02:
            continue
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.04 * peri, True)
        if len(approx) == 4:
            x, y, bw, bh = cv2.boundingRect(approx)
            aspect = bw / float(bh)
            if 0.75 <= aspect <= 1.25:
                M = cv2.moments(cnt)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    candidates.append((cx, cy))

    if len(candidates) >= 4:
        pts = np.array(candidates, dtype="float32")
        s = pts.sum(axis=1)
        diff = np.diff(pts, axis=1)

        tl = pts[np.argmin(s)]
        br = pts[np.argmax(s)]
        tr = pts[np.argmin(diff)]
        bl = pts[np.argmax(diff)]

        src_pts = np.array([tl, tr, br, bl], dtype="float32")
        dst_pts = np.array([
            [30, 30],
            [expected_w - 30, 30],
            [expected_w - 30, expected_h - 30],
            [30, expected_h - 30],
        ], dtype="float32")

        matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
        return cv2.warpPerspective(gray_img, matrix, (expected_w, expected_h))

    return cv2.resize(gray_img, (expected_w, expected_h))


def build_font(glyphs_svg: dict, font_name: str, output_path: str):
    fb = FontBuilder(1000, isTTF=True)
    glyph_order = [".notdef", "space"] + [f"uni{ord(c):04X}" for c in glyphs_svg.keys()]
    fb.setupGlyphOrder(glyph_order)

    cmap = {32: "space"}
    for c in glyphs_svg.keys():
        g_name = f"uni{ord(c):04X}"
        cmap[ord(c)] = g_name
        if c.isalpha():
            cmap[ord(c.lower())] = g_name
    fb.setupCharacterMap(cmap)

    glyphs = {}
    empty_pen = TTGlyphPen(None)
    glyphs[".notdef"] = empty_pen.glyph()
    glyphs["space"] = empty_pen.glyph()
    metrics = {".notdef": (500, 0), "space": (300, 0)}

    for char, svg_file in glyphs_svg.items():
        g_name = f"uni{ord(char):04X}"
        tt_pen = TTGlyphPen(None)
        cu2qu_pen = Cu2QuPen(tt_pen, max_err=1.0, reverse_direction=True)

        svg = SVGPath(svg_file)
        svg.draw(cu2qu_pen)

        glyphs[g_name] = tt_pen.glyph()
        metrics[g_name] = (600, 50)

    fb.setupGlyf(glyphs)
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=800, descent=-200)

    clean_ps_name = "".join(c for c in font_name if c.isalnum()) or "CustomFont"
    fb.setupNameTable({
        "familyName": font_name,
        "styleName": "Regular",
        "uniqueFontIdentifier": f"1.000;{clean_ps_name}-Regular",
        "fullName": f"{font_name} Regular",
        "version": "Version 1.000",
        "psName": f"{clean_ps_name}-Regular",
    })

    fb.setupOS2(
        sTypoAscender=800,
        sTypoDescender=-200,
        sTypoLineGap=0,
        usWinAscent=800,
        usWinDescent=200,
        sxHeight=500,
        sCapHeight=700,
    )
    fb.setupPost()

    fb.font["head"].unitsPerEm = 1000
    fb.font["maxp"].recalc(fb.font)
    for g_name in glyph_order:
        glyphs[g_name].recalcBounds(fb.font["glyf"])

    fb.save(output_path)


def image_to_ttf(image_bytes: bytes, font_name: str = "MyHandwriting") -> str:
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

    expected_w = COLS * CELL_SIZE + MARGIN * 2
    expected_h = ROWS * CELL_SIZE + MARGIN * 2 + 60

    aligned = warp_to_template(img, expected_w, expected_h)

    binary = cv2.adaptiveThreshold(
        aligned, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 15
    )

    glyphs_svg = {}
    local_potrace = os.path.join("bin", "potrace.exe")
    potrace_cmd = local_potrace if os.path.exists(local_potrace) else "potrace"

    with tempfile.TemporaryDirectory() as tmpdir:
        for idx, char in enumerate(ALPHABET):
            row = idx // COLS
            col = idx % COLS
            x0 = MARGIN + col * CELL_SIZE + 35
            y0 = MARGIN + 40 + row * CELL_SIZE + 35
            x1 = MARGIN + (col + 1) * CELL_SIZE - 15
            y1 = MARGIN + 40 + (row + 1) * CELL_SIZE - 15

            cell = binary[y0:y1, x0:x1]
            if cv2.countNonZero(cell) < 50:
                continue

            bmp_path = os.path.join(tmpdir, f"{idx}.bmp")
            svg_path = os.path.join(tmpdir, f"{idx}.svg")
            cv2.imwrite(bmp_path, 255 - cell)

            subprocess.run([potrace_cmd, bmp_path, "-s", "-o", svg_path], check=True)
            glyphs_svg[char] = svg_path

        output_ttf = tempfile.NamedTemporaryFile(delete=False, suffix=".ttf").name
        build_font(glyphs_svg, font_name, output_ttf)
        return output_ttf
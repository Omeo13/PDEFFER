import pytesseract
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

DEBUG_MODE = True
DEBUG_OUTPUT_DIR = "debug_output"

def extract_text(image):
    return pytesseract.image_to_string(image, config='--psm 3')

def detect_table_cells(image):
    raw = np.array(image)
    gray = cv2.cvtColor(raw, cv2.COLOR_RGB2GRAY)
    binarized = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                      cv2.THRESH_BINARY_INV, 15, 10)

    scale = 20
    horizontal_size = max(10, raw.shape[1] // scale)
    vertical_size = max(10, raw.shape[0] // scale)

    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontal_size, 1))
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, vertical_size))

    horizontal_lines = cv2.erode(binarized, horizontal_kernel)
    horizontal_lines = cv2.dilate(horizontal_lines, horizontal_kernel)
    vertical_lines = cv2.erode(binarized, vertical_kernel)
    vertical_lines = cv2.dilate(vertical_lines, vertical_kernel)

    intersections = cv2.bitwise_and(horizontal_lines, vertical_lines)
    intersections_coords = cv2.findNonZero(intersections)

    if intersections_coords is None or len(intersections_coords) < 4:
        return []

    pts = intersections_coords.reshape(-1, 2)

    def cluster_coords(coords, threshold=10):
        coords = sorted(coords)
        clusters = []
        current = [coords[0]]
        for p in coords[1:]:
            if abs(p - current[-1]) <= threshold:
                current.append(p)
            else:
                clusters.append(current)
                current = [p]
        clusters.append(current)
        return [int(np.mean(c)) for c in clusters]

    ys = sorted(set(pts[:, 1]))
    xs = sorted(set(pts[:, 0]))
    clustered_ys = cluster_coords(ys)
    clustered_xs = cluster_coords(xs)

    cells = []
    for i in range(len(clustered_ys) - 1):
        for j in range(len(clustered_xs) - 1):
            x = clustered_xs[j]
            y = clustered_ys[i]
            w = clustered_xs[j + 1] - x
            h = clustered_ys[i + 1] - y
            if w > 15 and h > 10:
                cells.append((x, y, w, h))

    return cells

def group_cells_into_rows(cells, row_threshold=10):
    rows = []
    current_row = []
    last_y = None
    for cell in sorted(cells, key=lambda b: (b[1], b[0])):
        x, y, w, h = cell
        if last_y is None or abs(y - last_y) <= row_threshold:
            current_row.append(cell)
            last_y = y
        else:
            rows.append(sorted(current_row, key=lambda b: b[0]))
            current_row = [cell]
            last_y = y
    if current_row:
        rows.append(sorted(current_row, key=lambda b: b[0]))
    return rows

def extract_text_from_cell(image, cell, padding=10):
    x, y, w, h = cell
    x0 = max(x - padding, 0)
    y0 = max(y - padding, 0)
    x1 = min(x + w + padding, image.width)
    y1 = min(y + h + padding, image.height)

    crop = image.crop((x0, y0, x1, y1)).convert("L")
    crop = crop.resize((crop.width * 3, crop.height * 3), resample=Image.LANCZOS)
    crop_cv = cv2.GaussianBlur(np.array(crop), (3, 3), 0)
    _, crop_cv = cv2.threshold(crop_cv, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    crop_processed = Image.fromarray(crop_cv)

    text = pytesseract.image_to_string(crop_processed, config='--psm 6').strip()
    return text

def extract_structured_data(image, debug_id=None):
    cells = detect_table_cells(image)
    if not cells:
        return {
            "top_text": extract_text(image),
            "table": None
        }

    table_top = min(c[1] for c in cells)
    top_text_img = image.crop((0, 0, image.width, table_top))
    top_text = extract_text(top_text_img).strip()

    rows = group_cells_into_rows(cells)
    table_data = []
    debug_overlay = image.copy()

    for r, row in enumerate(rows):
        row_data = []
        for c, cell in enumerate(row):
            text = extract_text_from_cell(image, cell)
            row_data.append(text)

            if DEBUG_MODE:
                draw = ImageDraw.Draw(debug_overlay)
                x, y, w, h = cell
                draw.rectangle([x, y, x + w, y + h], outline="red", width=2)
                try:
                    draw.text((x + 2, y + 2), text[:15], fill="blue")
                except Exception:
                    pass  # Skip draw error if font fails

        table_data.append(row_data)

    if DEBUG_MODE:
        os.makedirs(DEBUG_OUTPUT_DIR, exist_ok=True)
        debug_path = os.path.join(DEBUG_OUTPUT_DIR, f"DEBUG_{debug_id or 'image'}.png")
        debug_overlay.save(debug_path)
        print(f"[DEBUG] Saved debug overlay to {debug_path}")

    return {
        "top_text": top_text,
        "table": table_data
    }

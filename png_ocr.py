# png_ocr.py

import os
import pytesseract
import cv2
import numpy as np
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = "tesseract"  # Modify if needed

def extract_text(image):
    return pytesseract.image_to_string(image, config='--psm 3')

def detect_table_cells(image):
    raw = np.array(image)
    gray = cv2.cvtColor(raw, cv2.COLOR_RGB2GRAY)
    binarized = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                      cv2.THRESH_BINARY_INV, 15, 10)

    # Create line kernels
    scale = 20
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (max(10, raw.shape[1] // scale), 1))
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, max(10, raw.shape[0] // scale)))

    # Detect lines
    horizontal_lines = cv2.dilate(cv2.erode(binarized, horizontal_kernel), horizontal_kernel)
    vertical_lines = cv2.dilate(cv2.erode(binarized, vertical_kernel), vertical_kernel)

    # Find intersections
    intersections = cv2.bitwise_and(horizontal_lines, vertical_lines)
    intersections_coords = cv2.findNonZero(intersections)
    if intersections_coords is None or len(intersections_coords) < 4:
        return []

    pts = intersections_coords.reshape(-1, 2)

    def cluster_coords(coords, threshold=10):
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

def extract_text_from_cell(image, cell, padding=5):
    x, y, w, h = cell
    x0 = max(x - padding, 0)
    y0 = max(y - padding, 0)
    x1 = min(x + w + padding, image.width)
    y1 = min(y + h + padding, image.height)
    crop = image.crop((x0, y0, x1, y1)).convert("L")
    crop = crop.resize((crop.width * 3, crop.height * 3))
    text = pytesseract.image_to_string(crop, config='--psm 6').strip()
    return text

def scan_png(image_path):
    image = Image.open(image_path).convert("RGB")
    cells = detect_table_cells(image)
    if cells:
        rows = group_cells_into_rows(cells)
        table_data = []
        for row in rows:
            row_data = [extract_text_from_cell(image, cell) for cell in row]
            table_data.append(row_data)
        return table_data
    else:
        return [[extract_text(image)]]

if __name__ == "__main__":
    test_image = "output_pages/page_001.png"  # Example path
    data = scan_png(test_image)
    for row in data:
        print(row)

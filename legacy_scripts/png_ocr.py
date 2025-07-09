import cv2
import numpy as np
import pytesseract
from PIL import Image


def estimate_line_thickness(lines_img, axis='horizontal'):
    """
    Estimate median line thickness in pixels from a binary image of lines.
    axis: 'horizontal' or 'vertical' - affects how we measure thickness.
    """
    # Invert image: lines are white on black
    inverted = cv2.bitwise_not(lines_img)

    # Find contours (connected white blobs)
    contours, _ = cv2.findContours(inverted, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    thicknesses = []

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        # For horizontal lines, thickness is height; for vertical, thickness is width
        thickness = h if axis == 'horizontal' else w
        if thickness > 0:
            thicknesses.append(thickness)

    if not thicknesses:
        return None  # No lines found

    # Return median thickness as a robust estimate
    return int(np.median(thicknesses))
def detect_cells(image_cv, table_box, debug=False):
    x1, y1, x2, y2 = table_box
    roi = image_cv[y1:y2, x1:x2]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    scale = 20
    h_kernel_len = max(10, roi.shape[1] // scale)
    v_kernel_len = max(10, roi.shape[0] // scale)

    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (h_kernel_len, 1))
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, v_kernel_len))

    # Extract horizontal and vertical lines
    horizontal_lines = cv2.erode(binary, horizontal_kernel, iterations=1)
    horizontal_lines = cv2.dilate(horizontal_lines, horizontal_kernel, iterations=1)
    horizontal_lines = filter_short_lines(horizontal_lines, min_len=30, axis='horizontal')

    vertical_lines = cv2.erode(binary, vertical_kernel, iterations=1)
    vertical_lines = cv2.dilate(vertical_lines, vertical_kernel, iterations=1)
    vertical_lines = filter_short_lines(vertical_lines, min_len=70, axis='vertical')

    # Estimate line thickness
    h_thickness = estimate_line_thickness(horizontal_lines, axis='horizontal')
    v_thickness = estimate_line_thickness(vertical_lines, axis='vertical')

    if debug:
        print(f"[DEBUG] Estimated horizontal line thickness: {h_thickness}")
        print(f"[DEBUG] Estimated vertical line thickness: {v_thickness}")

    # Choose minimal thickness as bottleneck
    if h_thickness is None or v_thickness is None:
        thickness = 3  # fallback value
    else:
        thickness = min(h_thickness, v_thickness)

    # Adaptive dilation based on thickness
    if thickness <= 2:
        dilation_size = 3
    else:
        dilation_size = 1

    # Apply dilation to binary image to strengthen thin lines
    dilation_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (dilation_size, dilation_size))
    processed_binary = cv2.dilate(binary, dilation_kernel, iterations=1)

    # Recalculate lines on processed image
    horizontal_lines = cv2.erode(processed_binary, horizontal_kernel, iterations=1)
    horizontal_lines = cv2.dilate(horizontal_lines, horizontal_kernel, iterations=1)
    horizontal_lines = filter_short_lines(horizontal_lines, min_len=30, axis='horizontal')

    vertical_lines = cv2.erode(processed_binary, vertical_kernel, iterations=1)
    vertical_lines = cv2.dilate(vertical_lines, vertical_kernel, iterations=1)
    vertical_lines = filter_short_lines(vertical_lines, min_len=70, axis='vertical')

    # Get line positions for table grid
    x_lines = get_line_positions(vertical_lines, axis='vertical', scale=20, tol=5)
    y_lines = get_line_positions(horizontal_lines, axis='horizontal', scale=20, tol=8)

    if debug:
        print(f"[DEBUG] Grid lines - X: {len(x_lines)}, Y: {len(y_lines)}")

    cells = []
    for r in range(len(y_lines) - 1):
        for c in range(len(x_lines) - 1):
            cell_x1 = x1 + x_lines[c]
            cell_y1 = y1 + y_lines[r]
            cell_x2 = x1 + x_lines[c + 1]
            cell_y2 = y1 + y_lines[r + 1]
            cells.append((cell_x1, cell_y1, cell_x2, cell_y2))
    return cells


def extract_text(image_pil):
    gray = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2GRAY)
    return pytesseract.image_to_string(gray, config='--psm 6')

def detect_table_areas(image_cv, debug=True):
    gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)

    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    table_areas = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w > 100 and h > 50:
            table_areas.append((x, y, x + w, y + h))

    if debug:
        print(f"[DEBUG] Detected {len(table_areas)} potential tables")
    return table_areas

def filter_short_lines(lines_img, min_len=30, axis='horizontal'):
    result = np.zeros_like(lines_img)
    contours, _ = cv2.findContours(lines_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if axis == 'horizontal' and w >= min_len:
            cv2.drawContours(result, [cnt], -1, 255, -1)
        elif axis == 'vertical' and h >= min_len:
            cv2.drawContours(result, [cnt], -1, 255, -1)

    return result



def get_line_positions(binary_img, axis, scale, tol, debug=False, debug_prefix=""):
    if axis == 'horizontal':
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (binary_img.shape[1] // scale, 1))
    else:
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, binary_img.shape[0] // scale))

    lines = cv2.erode(binary_img, kernel, iterations=1)
    lines = cv2.dilate(lines, kernel, iterations=1)

    # Save raw lines before filtering
    if debug and debug_prefix:
        filename = f"debug_overlay/{debug_prefix}_{axis}_lines_raw.png"
        cv2.imwrite(filename, lines)
        print(f"[DEBUG] Saved raw {axis} lines to {filename}")

    # Use a lower min_len for vertical lines
    min_len = 15 if axis == 'vertical' else 30
    lines = filter_short_lines(lines, min_len=70 if axis == 'vertical' else 30, axis=axis)


    if debug and debug_prefix:
        filename = f"debug_overlay/{debug_prefix}_{axis}_lines_filtered.png"
        cv2.imwrite(filename, lines)
        print(f"[DEBUG] Saved filtered {axis} lines to {filename}")

    intersections = cv2.findNonZero(lines)
    if intersections is None:
        return []

    coords = sorted(set(p[0][1] if axis == 'horizontal' else p[0][0] for p in intersections))
    clustered = []
    cluster = [coords[0]]
    for v in coords[1:]:
        if abs(v - cluster[-1]) <= tol:
            cluster.append(v)
        else:
            clustered.append(int(np.mean(cluster)))
            cluster = [v]
    clustered.append(int(np.mean(cluster)))
    return clustered


def detect_cells(image_cv, table_box, debug=False):
    x1, y1, x2, y2 = table_box
    roi = image_cv[y1:y2, x1:x2]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    scale = 20
    h_kernel_len = max(10, roi.shape[1] // scale)
    v_kernel_len = max(10, roi.shape[0] // scale)

    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (h_kernel_len, 1))
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, v_kernel_len))

    horizontal_lines = cv2.erode(binary, horizontal_kernel, iterations=1)
    horizontal_lines = cv2.dilate(horizontal_lines, horizontal_kernel, iterations=1)
    horizontal_lines = filter_short_lines(horizontal_lines, min_len=30, axis='horizontal')

    vertical_lines = cv2.erode(binary, vertical_kernel, iterations=1)
    vertical_lines = cv2.dilate(vertical_lines, vertical_kernel, iterations=1)
    vertical_lines = filter_short_lines(vertical_lines, min_len=70, axis='vertical')

    x_lines = get_line_positions(vertical_lines, axis='vertical', scale=20, tol=5)
    y_lines = get_line_positions(horizontal_lines, axis='horizontal', scale=20, tol=8)

    if debug:
        print(f"[DEBUG] Grid lines - X: {len(x_lines)}, Y: {len(y_lines)}")

    cells = []
    for r in range(len(y_lines) - 1):
        for c in range(len(x_lines) - 1):
            cell_x1 = x1 + x_lines[c]
            cell_y1 = y1 + y_lines[r]
            cell_x2 = x1 + x_lines[c + 1]
            cell_y2 = y1 + y_lines[r + 1]
            cells.append((cell_x1, cell_y1, cell_x2, cell_y2))
    return cells



def group_cells(cells, row_tol=10):
    rows = []
    for cell in sorted(cells, key=lambda b: b[1]):
        y1 = cell[1]
        for row in rows:
            if abs(row[0][1] - y1) < row_tol:
                row.append(cell)
                break
        else:
            rows.append([cell])
    for row in rows:
        row.sort(key=lambda b: b[0])
    return rows

def extract_text_from_cell(image_cv, cell, debug=False):
    x1, y1, x2, y2 = cell
    roi = image_cv[y1:y2, x1:x2]

    if roi.size == 0:
        return ""

    # Preprocessing
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    padded = cv2.copyMakeBorder(gray, 5, 5, 5, 5, cv2.BORDER_CONSTANT, value=255)

    # Increase contrast (optional but useful)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4,4))
    contrast = clahe.apply(padded)

    # Save for debug
    if debug:
        debug_path = f"debug_overlay/cell_{x1}_{y1}_{x2}_{y2}_contrast.png"
        cv2.imwrite(debug_path, contrast)
        print(f"[DEBUG] Saved contrast-enhanced cell image to {debug_path}")

    config = config = r'--oem 3 --psm 6'

    text = pytesseract.image_to_string(contrast, config=config)

    if debug:
        print(f"[DEBUG] OCR cell ({x1}, {y1}, {x2}, {y2}): '{text.strip()}'")

    return text.strip()

import cv2
import numpy as np

def detect_table_areas_hough(image_cv, debug=False):
    """
    Detect table areas in the image using Hough line detection.

    Args:
        image_cv (np.ndarray): Input BGR image.
        debug (bool): If True, show intermediate images.

    Returns:
        List of bounding boxes of detected tables in format (x, y, w, h).
    """
    gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
    # Binarize the image - you may tune thresholding method here
    _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

    if debug:
        cv2.imshow("Binary", binary)
        cv2.waitKey(0)

    # Detect horizontal lines
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    horizontal_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)

    # Detect vertical lines
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
    vertical_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vertical_kernel, iterations=2)

    if debug:
        cv2.imshow("Horizontal lines", horizontal_lines)
        cv2.imshow("Vertical lines", vertical_lines)
        cv2.waitKey(0)

    # Combine lines to get table mask
    table_mask = cv2.bitwise_and(horizontal_lines, vertical_lines)

    if debug:
        cv2.imshow("Table mask", table_mask)
        cv2.waitKey(0)

    # Find contours from the table mask
    contours, _ = cv2.findContours(table_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    boxes = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        # Filter out small boxes that are unlikely tables
        if w > 50 and h > 50:
            boxes.append((x, y, w, h))
            if debug:
                print(f"Detected table box: x={x}, y={y}, w={w}, h={h}")

    if debug:
        # Draw detected boxes on a copy of the image for visualization
        img_copy = image_cv.copy()
        for (x, y, w, h) in boxes:
            cv2.rectangle(img_copy, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.imshow("Detected tables", img_copy)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return boxes








def extract_structured_data(image_pil, debug=False, use_hough=False, debug_id=None):
    import cv2
    import numpy as np

    image_cv = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)

    if use_hough:
        # Use Hough transform based table detection as fallback
        table_areas = detect_table_areas_hough(image_cv, debug)
    else:
        # Use your default table detection method
        table_areas = detect_table_areas(image_cv, debug)

    tables = []
    cell_boxes = []

    for box in table_areas:
        cells = detect_cells(image_cv, box, debug)
        rows = group_cells(cells)
        data = []
        for row in rows:
            row_text = []
            for cell in row:
                text = extract_text_from_cell(image_cv, cell, debug=debug)
                row_text.append(text)
                cell_boxes.append(cell)  # Collect bounding box here
            data.append(row_text)
        tables.append({"data": data, "box": box})

    return {"tables": tables, "cell_boxes": cell_boxes}

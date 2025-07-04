from PIL import Image
from png_ocr import extract_structured_data
from docx_writer import write_ocr_output_to_docx
import cv2

# === Paths ===
input_image_path = "/home/omeo/PycharmProjects/PythonProject11/output_pages/page1.png"
output_docx_path = "output_docx/page1.docx"
debug_id = "page1"

# === Load Image ===
image_pil = Image.open(input_image_path).convert("RGB")

# === Run OCR extraction without Hough ===
ocr_data = extract_structured_data(image_pil, debug=True, debug_id=debug_id)

# === Write to DOCX ===
write_ocr_output_to_docx(ocr_data, output_docx_path)

print(f"✅ Saved: {output_docx_path}")

# === (Optional) Visualize detected tables and cells ===
import cv2
import numpy as np

def draw_boxes(image_cv, boxes, color=(0,255,0), thickness=2):
    img = image_cv.copy()
    for (x1, y1, x2, y2) in boxes:
        cv2.rectangle(img, (x1, y1), (x2, y2), color, thickness)
    return img

def visualize_debug(image_path, ocr_data, save_path="debug_overlay.png"):
    image_cv = cv2.imread(image_path)

    # Draw table bounding boxes in blue
    if "table_boxes" in ocr_data:
        image_cv = draw_boxes(image_cv, ocr_data["table_boxes"], color=(255, 0, 0), thickness=3)

    # Draw cell bounding boxes in green
    if "cell_boxes" in ocr_data:
        image_cv = draw_boxes(image_cv, ocr_data["cell_boxes"], color=(0, 255, 0), thickness=1)

    cv2.imwrite(save_path, image_cv)
    print(f"[DEBUG] Saved visualization to {save_path}")

# After writing DOCX, call visualization:
visualize_debug(input_image_path, ocr_data)

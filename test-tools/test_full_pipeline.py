import os
from PIL import Image
import cv2

from pdf_to_png import pdf_to_png as convert_pdf_to_png

from png_ocr import extract_structured_data
from docx_writer import write_ocr_output_to_docx

# === Input PDF ===
input_pdf_path = "/home/omeo/Documents/testpdf2.pdf"  # CHANGE if needed

# === Output folders ===
png_output_folder = "output_pages"
docx_output_folder = "output_docx"
debug_output_folder = "debug_overlay"

os.makedirs(png_output_folder, exist_ok=True)
os.makedirs(docx_output_folder, exist_ok=True)
os.makedirs(debug_output_folder, exist_ok=True)

# === Step 1: Convert PDF to PNGs ===
print(f"[INFO] Converting PDF to PNGs...")
image_paths = convert_pdf_to_png(input_pdf_path, output_folder=png_output_folder, dpi=300)
print(f"[INFO] Converted {len(image_paths)} page(s)")

# === Step 2: Process Each PNG ===
def draw_boxes(image_cv, boxes, color=(0, 255, 0), thickness=2):
    for (x1, y1, x2, y2) in boxes:
        cv2.rectangle(image_cv, (x1, y1), (x2, y2), color, thickness)
    return image_cv

def save_debug_overlay(image_path, ocr_data, save_path):
    image_cv = cv2.imread(image_path)
    if "table_boxes" in ocr_data:
        image_cv = draw_boxes(image_cv, ocr_data["table_boxes"], color=(255, 0, 0), thickness=3)
    if "cell_boxes" in ocr_data:
        image_cv = draw_boxes(image_cv, ocr_data["cell_boxes"], color=(0, 255, 0), thickness=1)
    cv2.imwrite(save_path, image_cv)
    print(f"[DEBUG] Saved: {save_path}")

for i, image_path in enumerate(image_paths):
    page_id = f"page_{i+1:03d}"
    print(f"\n[INFO] Processing {page_id}...")

    image_pil = Image.open(image_path).convert("RGB")
    ocr_data = extract_structured_data(image_pil, debug=True, debug_id=page_id)

    # Save DOCX
    docx_path = os.path.join(docx_output_folder, f"{page_id}.docx")
    write_ocr_output_to_docx(ocr_data, docx_path)
    print(f"[✅] DOCX saved: {docx_path}")

    # Save debug overlay
    debug_path = os.path.join(debug_output_folder, f"{page_id}_debug.png")
    save_debug_overlay(image_path, ocr_data, debug_path)

print("\n✅ Full pipeline test complete.")

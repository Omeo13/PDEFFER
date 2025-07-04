import os
from PIL import Image
import json

from png_ocr import extract_structured_data
from docx_writer import write_ocr_output_to_docx

# === CONFIG ===
image_path = "/home/omeo/PycharmProjects/PythonProject11/output_pages/page_001.png"
output_docx_path = os.path.splitext(image_path)[0] + "_ocr_output.docx"
debug_id = "test001"

# === LOAD IMAGE ===
print(f"[DEBUG WRAPPER] Loading image from: {image_path}")
image = Image.open(image_path)

# === RUN OCR ===
print(f"[DEBUG WRAPPER] Running OCR on image...")
ocr_data = extract_structured_data(image, debug=True, debug_id=debug_id)

# === DUMP OCR STRUCTURE ===
print("\n[DEBUG WRAPPER] OCR Output Dump (truncated):")
print(json.dumps({
    "top_text": ocr_data["top_text"][:200] + "...",  # show only beginning of paragraph
    "tables": [
        {
            "rows": len(t.get("data", [])),
            "cols": max((len(row) for row in t.get("data", [])), default=0)
        } for t in ocr_data.get("tables", [])
    ]
}, indent=2))

# === SAVE DOCX ===
print(f"\n[DEBUG WRAPPER] Writing DOCX to: {output_docx_path}")
write_ocr_output_to_docx(ocr_data, output_docx_path)

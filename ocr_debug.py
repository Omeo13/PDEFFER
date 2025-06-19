from PIL import Image
from png_ocr import extract_structured_data
from docx_writer import write_ocr_output_to_docx

# === Input/Output Paths ===
input_image_path = "/home/omeo/PycharmProjects/PythonProject11/output_pages/page_001.png"       # Change if needed
output_docx_path = "output_docx/page1.docx"
debug_id = "page1"

# === Load Image and Run OCR ===
image = Image.open(input_image_path).convert("RGB")
ocr_data = extract_structured_data(image, debug_id=debug_id)

# === Write DOCX Output ===
write_ocr_output_to_docx(ocr_data, output_docx_path)

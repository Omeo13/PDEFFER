from PIL import Image
from png_ocr import extract_structured_data
from docx_writer import write_ocr_output_to_docx

# Replace this with a real test image path
input_image_path = "output_pages/page1.png"
output_docx_path = "output_docx/page1.docx"
debug_id = "page1"

# Load image
image = Image.open(input_image_path).convert("RGB")

# Run OCR
ocr_data = extract_structured_data(image, debug_id=debug_id)

# Write DOCX output
write_ocr_output_to_docx(ocr_data, output_docx_path)


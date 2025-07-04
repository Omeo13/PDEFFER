from PIL import Image
from png_ocr import extract_structured_data
from docx_writer import write_ocr_output_to_docx

input_image_path = "output_pages/page_001.png"
output_docx_path = "output_docx/page1.docx"
debug_id = "page1"

print("[DEBUG] Starting script...")

image = Image.open(input_image_path).convert("RGB")
ocr_data = extract_structured_data(image, debug=True, debug_id=debug_id)
write_ocr_output_to_docx(ocr_data, output_docx_path)


try:
    # Load image
    image = Image.open(input_image_path).convert("RGB")
    print("[DEBUG] Image loaded.")

    # Extract OCR structured data
    ocr_data = extract_structured_data(image, debug=True, debug_id=debug_id)
    print("[DEBUG] OCR data extracted.")
    print(f"  - Top text length: {len(ocr_data.get('top_text', ''))}")
    print(f"  - Tables detected: {len(ocr_data.get('tables', []))}")

    for idx, table in enumerate(ocr_data.get("tables", [])):
        print(f"    Table {idx}:")
        print(f"      - Rows: {len(table['data'])}")
        print(f"      - Cells: {len(table['cells'])}")
        print(f"      - Merged cells: {len(table['merged_cells'])}")
        for row in table['data']:
            print(f"        {row}")

    # Write DOCX output
    write_ocr_output_to_docx(ocr_data, output_docx_path)
    print(f"[✅] DOCX saved to: {output_docx_path}")

except Exception as e:
    print("[❌] Exception occurred:", e)

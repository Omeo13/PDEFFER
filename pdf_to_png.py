import os
from pdf2image import convert_from_path

def pdf_to_png(pdf_path, output_folder="output_pages", dpi=300):
    os.makedirs(output_folder, exist_ok=True)
    pages = convert_from_path(pdf_path, dpi=dpi)

    output_paths = []
    for i, page in enumerate(pages):
        output_path = os.path.join(output_folder, f"page_{i + 1:03d}.png")
        page.save(output_path, "PNG")
        output_paths.append(output_path)
        print(f"Saved: {output_path}")

    return output_paths

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python pdf_to_png.py input_file.pdf")
    else:
        pdf_path = sys.argv[1]
        pdf_to_png(pdf_path)

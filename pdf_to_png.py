import os
from pdf2image import convert_from_path

def pdf_to_png(pdf_path, output_folder="output_pages", dpi=300):
    """
    Converts each page of a PDF file into a PNG image.

    Parameters:
    - pdf_path (str): Path to the input PDF file.
    - output_folder (str): Directory where PNG images will be saved.
    - dpi (int): Resolution of the output images.

    Returns:
    - output_paths (list): List of file paths to the saved PNG images.
    """
    os.makedirs(output_folder, exist_ok=True)  # Ensure output directory exists

    pages = convert_from_path(pdf_path, dpi=dpi)  # Convert PDF pages to PIL images

    output_paths = []
    for i, page in enumerate(pages):
        # Create output file name for each page (e.g., page_001.png)
        output_path = os.path.join(output_folder, f"page_{i + 1:03d}.png")
        page.save(output_path, "PNG")  # Save image as PNG
        output_paths.append(output_path)
        print(f"Saved: {output_path}")  # Feedback for each saved file

    # NOTE: This module does not handle table detection or nested tables.
    #       Detection and handling of nested tables must be implemented in the OCR and table-detection stage.

    return output_paths

# This block runs only when the script is executed directly, not when imported
if __name__ == "__main__":
    import sys

    # Check for proper usage: expect a PDF file path as an argument
    if len(sys.argv) < 2:
        print("Usage: python pdf_to_png.py input_file.pdf")
    else:
        pdf_path = sys.argv[1]
        pdf_to_png(pdf_path)  # Run the conversion function

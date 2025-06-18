# docx_writer.py

from docx import Document

def write_table_to_docx(table_data, output_path):
    """
    Accepts a list of rows, each row being a list of cell texts.
    Writes this as a DOCX table.
    """
    doc = Document()
    if not table_data or not any(table_data):
        doc.add_paragraph("No readable content found.")
    elif len(table_data) == 1 and len(table_data[0]) == 1:
        # Only one block of text, not a table
        doc.add_paragraph(table_data[0][0])
    else:
        table = doc.add_table(rows=len(table_data), cols=max(len(row) for row in table_data))
        table.style = 'Table Grid'
        for i, row in enumerate(table_data):
            for j, cell_text in enumerate(row):
                table.cell(i, j).text = cell_text if cell_text else ""
    doc.save(output_path)

if __name__ == "__main__":
    # Demo usage
    dummy_data = [
        ["Name", "Age", "City"],
        ["Alice", "30", "New York"],
        ["Bob", "25", "London"],
        ["Charlie", "35", "Berlin"]
    ]
    write_table_to_docx(dummy_data, "demo_output.docx")
    print("DOCX written to 'demo_output.docx'")

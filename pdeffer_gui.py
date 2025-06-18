import os
from tkinter import Tk, Label, Button, filedialog, messagebox, StringVar, OptionMenu

def select_input_file():
    filetypes = [("Supported files", "*.pdf *.png *.jpg *.jpeg"),
                 ("PDF files", "*.pdf"),
                 ("Image files", "*.png *.jpg *.jpeg")]
    filename = filedialog.askopenfilename(title="Select input file", filetypes=filetypes)
    if filename:
        input_path_var.set(filename)

def select_output_folder():
    folder = filedialog.askdirectory(title="Select output folder")
    if folder:
        output_folder_var.set(folder)

def run_selected_module():
    input_path = input_path_var.get()
    output_folder = output_folder_var.get()
    module = module_var.get()

    if not input_path:
        messagebox.showerror("Error", "Please select an input file.")
        return
    if not output_folder:
        messagebox.showerror("Error", "Please select an output folder.")
        return

    # Here you would call your actual module functions, for now just placeholders:
    if module == "PDF to PNG":
        messagebox.showinfo("Info", f"Would run PDF to PNG on:\n{input_path}\nOutput to:\n{output_folder}")
        # import pdf_to_png; pdf_to_png.process_pdf(input_path, output_folder)

    elif module == "PNG OCR & Table Detect":
        messagebox.showinfo("Info", f"Would run OCR & table detection on:\n{input_path}\nOutput to:\n{output_folder}")
        # import png_scan; png_scan.process_single_image(input_path, output_folder)

    elif module == "Write DOCX":
        messagebox.showinfo("Info", f"Would run DOCX writer on OCR data from:\n{input_path}\nOutput to:\n{output_folder}")
        # import docx_writer; docx_writer.write_table_to_docx(ocr_data, os.path.join(output_folder, "output.docx"))

    else:
        messagebox.showerror("Error", "Unknown module selected.")

root = Tk()
root.title("PDEffer GUI")
root.geometry("400x220")

input_path_var = StringVar()
output_folder_var = StringVar()
module_var = StringVar(value="PDF to PNG")

Label(root, text="Input File:").pack(pady=(10, 0))
Button(root, text="Select Input File", command=select_input_file).pack()
Label(root, textvariable=input_path_var, wraplength=380).pack(pady=(0,10))

Label(root, text="Output Folder:").pack()
Button(root, text="Select Output Folder", command=select_output_folder).pack()
Label(root, textvariable=output_folder_var, wraplength=380).pack(pady=(0,10))

Label(root, text="Select Module to Run:").pack()
modules = ["PDF to PNG", "PNG OCR & Table Detect", "Write DOCX"]
OptionMenu(root, module_var, *modules).pack(pady=(0,20))

Button(root, text="Run", command=run_selected_module).pack()

root.mainloop()

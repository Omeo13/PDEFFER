import os
from tkinter import Tk, Label, Button, filedialog, messagebox, StringVar, OptionMenu

def select_input():
    module = module_var.get()
    if module == "PDF to PNG" or module == "PNG OCR & Table Detect (single)":
        # Select a single file
        filetypes = [("Supported files", "*.pdf *.png *.jpg *.jpeg"),
                     ("PDF files", "*.pdf"),
                     ("Image files", "*.png *.jpg *.jpeg")]
        filename = filedialog.askopenfilename(title="Select input file", filetypes=filetypes)
        if filename:
            input_path_var.set(filename)
    else:
        # Select input folder for batch
        folder = filedialog.askdirectory(title="Select input folder")
        if folder:
            input_path_var.set(folder)
    validate_inputs()

def select_output_folder():
    folder = filedialog.askdirectory(title="Select output folder")
    if folder:
        output_folder_var.set(folder)
    validate_inputs()

def validate_inputs():
    # Enable Run button only if input and output are set
    if input_path_var.get() and output_folder_var.get():
        run_button.config(state="normal")
    else:
        run_button.config(state="disabled")

def run_selected_module():
    input_path = input_path_var.get()
    output_folder = output_folder_var.get()
    module = module_var.get()

    status_var.set("Running... Please wait.")
    root.update_idletasks()

    try:
        if module == "PDF to PNG":
            # Example call - replace with your actual import & function
            # import pdf_to_png
            # pdf_to_png.process_pdf(input_path, output_folder)
            messagebox.showinfo("Info", f"Would run PDF to PNG on:\n{input_path}\nOutput to:\n{output_folder}")

        elif module == "PNG OCR & Table Detect (single)":
            # import png_ocr
            # png_ocr.process_single_image(input_path, output_folder)
            messagebox.showinfo("Info", f"Would run OCR & table detection on single image:\n{input_path}\nOutput to:\n{output_folder}")

        elif module == "PNG OCR & Table Detect (batch)":
            # import png_ocr
            # png_ocr.batch_process_images(input_path, output_folder)
            messagebox.showinfo("Info", f"Would run OCR & table detection on batch folder:\n{input_path}\nOutput to:\n{output_folder}")

        elif module == "Write DOCX":
            # import docx_writer
            # ocr_data = ... get OCR data from somewhere or previous step
            # docx_writer.write_ocr_output_to_docx(ocr_data, os.path.join(output_folder, "output.docx"))
            messagebox.showinfo("Info", f"Would write DOCX from OCR data.\nOutput to:\n{output_folder}")

        else:
            messagebox.showerror("Error", "Unknown module selected.")

        status_var.set("Done.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred:\n{e}")
        status_var.set("Error.")

def on_module_change(*args):
    # Clear input path when module changes
    input_path_var.set("")
    validate_inputs()

root = Tk()
root.title("PDEffer GUI")
root.geometry("500x250")
root.resizable(False, False)

input_path_var = StringVar()
output_folder_var = StringVar()
module_var = StringVar(value="PDF to PNG")
status_var = StringVar(value="")

# Input selection
Label(root, text="Input File or Folder:").grid(row=0, column=0, sticky='e', padx=10, pady=10)
input_entry = Label(root, textvariable=input_path_var, anchor="w", relief="sunken", width=50)
input_entry.grid(row=0, column=1, padx=10, pady=10, sticky='we')
Button(root, text="Browse...", command=select_input).grid(row=0, column=2, padx=10)

# Output folder selection
Label(root, text="Output Folder:").grid(row=1, column=0, sticky='e', padx=10, pady=10)
output_entry = Label(root, textvariable=output_folder_var, anchor="w", relief="sunken", width=50)
output_entry.grid(row=1, column=1, padx=10, pady=10, sticky='we')
Button(root, text="Browse...", command=select_output_folder).grid(row=1, column=2, padx=10)

# Module selection
Label(root, text="Select Module to Run:").grid(row=2, column=0, sticky='e', padx=10, pady=10)
modules = [
    "PDF to PNG",
    "PNG OCR & Table Detect (single)",
    "PNG OCR & Table Detect (batch)",
    "Write DOCX"
]
module_menu = OptionMenu(root, module_var, *modules)
module_menu.grid(row=2, column=1, padx=10, pady=10, sticky='we')

# Run button
run_button = Button(root, text="Run", command=run_selected_module, state="disabled")
run_button.grid(row=3, column=1, pady=20)

# Status label
status_label = Label(root, textvariable=status_var, anchor='w')
status_label.grid(row=4, column=0, columnspan=3, padx=10, sticky='we')

# Bind module_var change event to reset input and validate
module_var.trace_add("write", on_module_change)

# Grid column configuration for responsive layout
root.grid_columnconfigure(1, weight=1)

root.mainloop()

import os
import io
import uuid
import time
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi_utils.tasks import repeat_every
from PIL import Image
import pdf_to_png
import png_ocr
import docx_writer

app = FastAPI()

TEMP_DIR = "tmp_local/pdeffer"
CLEANUP_OLDER_THAN_SECONDS = 3600  # 1 hour

@app.on_event("startup")
@repeat_every(seconds=60 * 30)  # every 30 minutes
def cleanup_old_jobs() -> None:
    now = time.time()
    if not os.path.exists(TEMP_DIR):
        return
    for job_folder in os.listdir(TEMP_DIR):
        folder_path = os.path.join(TEMP_DIR, job_folder)
        if os.path.isdir(folder_path):
            last_modified = os.path.getmtime(folder_path)
            age = now - last_modified
            if age > CLEANUP_OLDER_THAN_SECONDS:
                try:
                    shutil.rmtree(folder_path)
                    print(f"[cleanup] Removed old job folder: {folder_path}")
                except Exception as e:
                    print(f"[cleanup] Failed to remove {folder_path}: {e}")

@app.post("/process/")
async def process_pdf(
    file: UploadFile = File(...),
    debug: bool = Query(False, description="Enable debug mode"),
    use_hough: bool = Query(False, description="Enable Hough transform fallback"),
):
    # Create unique job directory
    job_id = str(uuid.uuid4())
    work_dir = os.path.join(TEMP_DIR, job_id)
    os.makedirs(work_dir, exist_ok=True)

    pdf_path = os.path.join(work_dir, file.filename)
    with open(pdf_path, "wb") as f:
        f.write(await file.read())

    # Convert PDF to PNG images
    try:
        png_paths = pdf_to_png.convert_pdf_to_png(pdf_path, output_folder=work_dir)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF to PNG conversion failed: {e}")

    ocr_results = []
    for png_path in png_paths:
        # Open image for OCR
        image_pil = Image.open(png_path)

        # Extract OCR data (supporting Hough fallback)
        ocr_data = png_ocr.extract_structured_data(image_pil, debug=debug, use_hough=use_hough)
        ocr_results.append(ocr_data)

    # Write all OCR data to one multi-page DOCX
    docx_path = os.path.join(work_dir, "output.docx")
    try:
        docx_writer.write_multi_page_ocr_output_to_docx(ocr_results, docx_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DOCX writing failed: {e}")

    return {
        "message": "Processing complete",
        "job_id": job_id,
        "download_url": f"/download/{job_id}"
    }

@app.get("/download/{job_id}")
async def download_docx(job_id: str):
    docx_path = os.path.join(TEMP_DIR, job_id, "output.docx")
    if not os.path.exists(docx_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=docx_path, filename="output.docx", media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

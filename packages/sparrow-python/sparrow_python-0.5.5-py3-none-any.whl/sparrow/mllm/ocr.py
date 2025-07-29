import os
import shutil

from fastapi import FastAPI, Form, UploadFile
from fastapi.responses import JSONResponse
from transformers import AutoModel, AutoTokenizer

app = FastAPI()

# Load the model and tokenizer
MODEL_NAME = "/home/kunyuan/models/stepfun-ai/GOT-OCR2_0"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
model = AutoModel.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True,
    low_cpu_mem_usage=True,
    device_map="cuda",
    use_safetensors=True,
    pad_token_id=tokenizer.eos_token_id,

)
model = model.eval().cuda()


@app.post("/v1/chat")
async def chat_completions(
        file: UploadFile,
        ocr_type: str = Form(...),
        ocr_box: str = Form(None),
        ocr_color: str = Form(None),
        render: bool = Form(False),
):
    """Handle OCR requests

    Args:
        file (UploadFile): The image file to process.
        ocr_type (str): The OCR type, e.g., 'ocr' or 'format'.
        ocr_box (str, optional): Specific OCR box configuration.
        ocr_color (str, optional): Specific OCR color configuration.
        render (bool, optional): Whether to render the OCR results.

    Returns:
        JSONResponse: OCR result.
    """
    try:
        # Save the uploaded file temporarily
        temp_dir = "./temp"
        os.makedirs(temp_dir, exist_ok=True)
        temp_file_path = os.path.join(temp_dir, file.filename)

        with open(temp_file_path, "wb") as temp_file:
            shutil.copyfileobj(file.file, temp_file)

        # Perform OCR with additional parameters
        if render:
            res = model.chat(
                tokenizer,
                temp_file_path,
                ocr_type=ocr_type,
                ocr_box=ocr_box,
                ocr_color=ocr_color,
                render=True,
                save_render_file="./rendered_result.html",
            )
        else:
            res = model.chat(
                tokenizer,
                temp_file_path,
                ocr_type=ocr_type,
                ocr_box=ocr_box,
                ocr_color=ocr_color,
            )

        # Clean up the temporary file
        os.remove(temp_file_path)

        return JSONResponse(content={"ocr_result": res}, status_code=200)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/v1/chat/crop")
async def chat_crop_completions(
        file: UploadFile,
        ocr_type: str = Form(...),
):
    """Handle multi-crop OCR requests.

    Args:
        file (UploadFile): The image file to process.
        ocr_type (str): The OCR type, e.g., 'ocr' or 'format'.

    Returns:
        JSONResponse: OCR result.
    """
    try:
        # Save the uploaded file temporarily
        temp_dir = "./temp"
        os.makedirs(temp_dir, exist_ok=True)
        temp_file_path = os.path.join(temp_dir, file.filename)

        with open(temp_file_path, "wb") as temp_file:
            shutil.copyfileobj(file.file, temp_file)

        # Perform multi-crop OCR
        res = model.chat_crop(tokenizer, temp_file_path, ocr_type=ocr_type)

        # Clean up the temporary file
        os.remove(temp_file_path)

        return JSONResponse(content={"ocr_result": res}, status_code=200)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9999)

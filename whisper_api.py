
import os
import tempfile
import threading

os.environ["HF_HUB_OFFLINE"] = "1"

import whisper
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse

app = FastAPI(title="Verity JE Whisper API")

MODEL_DIR = r"D:\VerityAI\models\whisper"
MODEL_NAME = "base"

print("正在加载本地 Whisper base 模型，请稍候……")
model = whisper.load_model(
    MODEL_NAME,
    device="cpu",
    download_root=MODEL_DIR,
)
print("Whisper 模型加载成功。")

transcribe_lock = threading.Lock()


@app.get("/v1/models")
def list_models():
    return {
        "object": "list",
        "data": [
            {
                "id": "base",
                "object": "model",
                "owned_by": "local",
            }
        ],
    }


@app.post("/v1/audio/transcriptions")
async def transcriptions(
    file: UploadFile = File(...),
    language: str = Form("zh"),
    response_format: str = Form("json"),
    model_name: str = Form("base", alias="model"),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="缺少音频文件名")

    suffix = os.path.splitext(file.filename)[1] or ".wav"
    temp_path = None

    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="音频文件为空")

        with tempfile.NamedTemporaryFile(
            suffix=suffix,
            delete=False,
        ) as temp:
            temp.write(content)
            temp_path = temp.name

        with transcribe_lock:
            result = model.transcribe(
                temp_path,
                language=language or "zh",
                fp16=False,
            )

        text = result.get("text", "").strip()

        if response_format == "text":
            from fastapi.responses import PlainTextResponse
            return PlainTextResponse(text)

        return JSONResponse({"text": text})

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Whisper 识别失败：{exc}",
        ) from exc
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=9000)

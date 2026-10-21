
import os
import io
import re
import threading

os.environ["HF_HOME"] = r"D:\VerityAI\hf_cache"
os.environ["HF_HUB_CACHE"] = r"D:\VerityAI\hf_cache\hub"
os.environ["HF_HUB_OFFLINE"] = "1"

import numpy as np
import soundfile as sf
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from kokoro import KPipeline

app = FastAPI(title="Verity JE Kokoro API")

# 按语言分别加载管线，复用 D 盘已有模型缓存
pipelines = {}
pipeline_lock = threading.Lock()
generation_lock = threading.Lock()


def get_pipeline(lang_code):
    with pipeline_lock:
        if lang_code not in pipelines:
            pipelines[lang_code] = KPipeline(lang_code=lang_code)
        return pipelines[lang_code]


class SpeechRequest(BaseModel):
    model: str = "kokoro"
    input: str
    voice: str | None = None
    response_format: str = "wav"
    speed: float = 1.0


@app.get("/v1/models")
def list_models():
    return {
        "object": "list",
        "data": [
            {"id": "kokoro", "object": "model", "owned_by": "local"}
        ],
    }


@app.post("/v1/audio/speech")
def create_speech(req: SpeechRequest):
    text = req.input.strip()

    if not text:
        raise HTTPException(status_code=400, detail="input 不能为空")

    if len(text) > 2000:
        raise HTTPException(status_code=400, detail="单次文本不能超过 2000 字符")

    if not 0.5 <= req.speed <= 2.0:
        raise HTTPException(status_code=400, detail="speed 必须在 0.5 到 2.0 之间")

    is_chinese = bool(re.search(r"[\u4e00-\u9fff]", text))

    if is_chinese:
        lang_code = "z"
        voice = req.voice or "zf_xiaobei"
    else:
        lang_code = "a"
        voice = req.voice or "af_heart"

    try:
        pipeline = get_pipeline(lang_code)

        # 防止多个请求同时占用模型造成冲突
        with generation_lock:
            chunks = []
            for _, _, audio in pipeline(
                text,
                voice=voice,
                speed=req.speed,
            ):
                if audio is not None:
                    chunks.append(audio.detach().cpu().numpy())

        if not chunks:
            raise RuntimeError("Kokoro 没有生成音频")

        audio_data = np.concatenate(chunks)
        buffer = io.BytesIO()
        sf.write(buffer, audio_data, 24000, format="WAV")
        wav_data = buffer.getvalue()

        return Response(
            content=wav_data,
            media_type="audio/wav",
            headers={"Content-Disposition": 'inline; filename="speech.wav"'},
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Kokoro 合成失败：{exc}",
        ) from exc


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8880)

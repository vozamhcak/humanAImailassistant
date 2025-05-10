from pathlib import Path
from typing import Dict, List

from fastapi import FastAPI, HTTPException  # type: ignore
from fastapi.staticfiles import StaticFiles  # type: ignore
from fastapi.responses import JSONResponse, HTMLResponse  # type: ignore
from pydantic import BaseModel  # type: ignore

from backend.gpt import analyze_email

app = FastAPI(title="AI Email Assistant")

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
if not FRONTEND_DIR.exists():
    raise RuntimeError("Папка frontend не найдена. Создайте каталог frontend рядом с backend.")

app.mount("/static", StaticFiles(directory=FRONTEND_DIR / "static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Отдаём index.html"""
    index_file = FRONTEND_DIR / "index.html"
    return index_file.read_text(encoding="utf‑8")


class EmailIn(BaseModel):
    text: str


@app.post("/analyze")
async def analyze(in_data: EmailIn):
    try:
        result: Dict[str, str | List[str]] = analyze_email(in_data.text)
        return JSONResponse(result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


class FeedbackIn(BaseModel):
    message: str


@app.post("/feedback")
async def feedback(data: FeedbackIn):
    print("Feedback:", data.message)
    return {"status": "ok"}

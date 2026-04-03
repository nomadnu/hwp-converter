"""
HWP → PDF 변환 서버 (클라우드 배포용 - Linux + LibreOffice)
"""

import os
import uuid
import shutil
import subprocess
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="HWP → PDF 변환기")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

OUTPUT_DIR = Path("/tmp/hwp_output")
TMP_DIR    = Path("/tmp/hwp_tmp")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TMP_DIR.mkdir(parents=True, exist_ok=True)

# LibreOffice 경로 (Linux)
LO = shutil.which("libreoffice") or shutil.which("soffice") or "/usr/bin/libreoffice"


@app.get("/", response_class=HTMLResponse)
async def root():
    p = Path("index.html")
    if p.exists():
        return HTMLResponse(content=p.read_text(encoding="utf-8"))
    return HTMLResponse("<h2>index.html을 찾을 수 없습니다.</h2>")


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "libreoffice": LO,
        "lo_exists": Path(LO).exists() if LO else False,
    }


@app.post("/convert")
async def convert(file: UploadFile = File(...)):
    filename = file.filename or ""
    ext = Path(filename).suffix.lower()

    if ext not in (".hwp", ".hwpx"):
        raise HTTPException(400, "HWP 또는 HWPX 파일만 업로드 가능합니다.")

    original_stem = Path(filename).stem
    job_id  = str(uuid.uuid4())[:8]
    job_dir = TMP_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    try:
        # 한글 파일명 → 영문으로 저장
        hwp_path = job_dir / f"input{ext}"
        hwp_path.write_bytes(await file.read())

        # LibreOffice 변환 (Linux headless)
        result = subprocess.run(
            [
                LO,
                "--headless",
                "--norestore",
                "--convert-to", "pdf",
                "--outdir", str(job_dir),
                str(hwp_path),
            ],
            capture_output=True,
            text=True,
            timeout=120,
            stdin=subprocess.DEVNULL,
            env={**os.environ, "HOME": "/tmp"},  # LibreOffice 프로필 경로
        )

        print(f"[returncode] {result.returncode}")
        print(f"[stdout] {result.stdout[:300]}")
        print(f"[stderr] {result.stderr[:300]}")

        # PDF 찾기
        pdf_tmp = job_dir / "input.pdf"
        if not pdf_tmp.exists():
            pdfs = list(job_dir.glob("*.pdf"))
            if not pdfs:
                detail = (result.stderr or result.stdout or "변환 실패")[:400]
                raise HTTPException(500, f"변환 실패: {detail}")
            pdf_tmp = pdfs[0]

        # 결과 저장
        pdf_out = OUTPUT_DIR / f"{job_id}.pdf"
        shutil.copy(pdf_tmp, pdf_out)

    finally:
        shutil.rmtree(job_dir, ignore_errors=True)

    return FileResponse(
        path=str(pdf_out),
        media_type="application/pdf",
        filename=f"{original_stem}.pdf",
        headers={"X-File-Id": job_id},
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"서버 시작: http://0.0.0.0:{port}")
    uvicorn.run("server:app", host="0.0.0.0", port=port)

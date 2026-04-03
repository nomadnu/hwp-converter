"""
HWP → PDF 변환 서버 (Railway 배포용)
"""
import os, uuid, shutil, subprocess
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

LO = shutil.which("libreoffice") or shutil.which("soffice") or "/usr/bin/libreoffice"

def get_env():
    """LibreOffice 실행에 필요한 환경변수"""
    env = dict(os.environ)
    env["HOME"] = "/tmp"
    # Java 경로 자동 탐지
    import glob
    java_paths = glob.glob("/usr/lib/jvm/java-17*") + glob.glob("/usr/lib/jvm/java-default")
    if java_paths:
        env["JAVA_HOME"] = java_paths[0]
        env["PATH"] = java_paths[0] + "/bin:" + env.get("PATH", "")
    return env


@app.get("/", response_class=HTMLResponse)
async def root():
    p = Path("/app/index.html")
    return HTMLResponse(p.read_text(encoding="utf-8") if p.exists() else "<h2>index.html 없음</h2>")


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "libreoffice": LO,
        "java_home": os.environ.get("JAVA_HOME", "not set"),
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

        result = subprocess.run(
            [
                LO,
                "--headless",
                "--norestore",
                "--nofirststartwizard",
                "-env:UserInstallation=file:///tmp/lo_profile",
                "--convert-to", "pdf",
                "--outdir", str(job_dir),
                str(hwp_path),
            ],
            capture_output=True,
            text=True,
            timeout=120,
            stdin=subprocess.DEVNULL,
            env=get_env(),
        )

        print(f"[rc={result.returncode}]")
        print(f"[stdout] {result.stdout[:300]}")
        print(f"[stderr] {result.stderr[:300]}")

        # PDF 찾기
        pdf_tmp = job_dir / "input.pdf"
        if not pdf_tmp.exists():
            pdfs = list(job_dir.glob("*.pdf"))
            if not pdfs:
                detail = (result.stderr or result.stdout or "변환 실패")[:300]
                raise HTTPException(500, f"변환 실패: {detail}")
            pdf_tmp = pdfs[0]

        pdf_out = OUTPUT_DIR / f"{job_id}.pdf"
        shutil.copy(pdf_tmp, pdf_out)

    finally:
        shutil.rmtree(job_dir, ignore_errors=True)

    return FileResponse(
        path=str(pdf_out),
        media_type="application/pdf",
        filename=f"{original_stem}.pdf",
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"[서버 시작] http://0.0.0.0:{port}")
    uvicorn.run("server:app", host="0.0.0.0", port=port)

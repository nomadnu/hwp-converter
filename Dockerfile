FROM python:3.11-slim

# LibreOffice + 한글 폰트 설치
RUN apt-get update && apt-get install -y \
    libreoffice \
    libreoffice-writer \
    fonts-noto-cjk \
    fonts-noto-cjk-extra \
    --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리
WORKDIR /app

# Python 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 파일 복사
COPY server.py .
COPY index.html .

# 출력 폴더 생성
RUN mkdir -p /tmp/hwp_output /tmp/hwp_tmp

EXPOSE 8000

CMD ["python", "server.py"]

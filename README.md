# HWP → PDF 변환기 (클라우드 배포)

누구나 링크 하나로 HWP 파일을 PDF로 변환할 수 있는 웹 서비스입니다.

---

## 🚀 Render.com 무료 배포 방법

### 1단계 — GitHub에 업로드

1. [github.com](https://github.com) 회원가입/로그인
2. 우측 상단 **`+` → New repository** 클릭
3. Repository name: `hwp-converter`
4. **Public** 선택 → **Create repository**
5. 이 폴더의 파일들을 모두 업로드
   - `Upload files` 클릭 → 전체 드래그앤드롭

### 2단계 — Render.com 배포

1. [render.com](https://render.com) 회원가입 (GitHub 계정으로 로그인 가능)
2. **New → Web Service** 클릭
3. GitHub 저장소 `hwp-converter` 연결
4. 설정:
   - **Environment**: `Docker`
   - **Plan**: `Free`
5. **Create Web Service** 클릭
6. 5~10분 기다리면 배포 완료!

### 3단계 — 완료!

배포 후 아래와 같은 URL이 생성됩니다:
```
https://hwp-converter-xxxx.onrender.com
```

이 링크를 카카오톡, 문자 등으로 공유하면
**누구나 PC/모바일에서 HWP → PDF 변환 가능!**

---

## ⚠️ 무료 플랜 제한사항

| 항목 | 내용 |
|------|------|
| 슬립 모드 | 15분 비활성 시 서버가 잠듦 (첫 요청 시 30초 대기) |
| 월 사용량 | 750시간 무료 |
| 파일 저장 | 재시작 시 변환된 PDF 초기화 (다운로드 후 삭제 권장) |

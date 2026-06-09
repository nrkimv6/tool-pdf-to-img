# Cloud Run HTTP Wrapper 설계 — python-pdf-to-img

> 작성일: 2026-06-09
> 관련 계획서: `2026-06-08_public_gcp_free_tier_roadmap_todo-14.md`
> 실제 배포(Cloud Run visibility 변경, deploy)는 Phase M — 사용자 별도 승인 후 수행

---

## 1. CLI entrypoint vs 변환 함수 분리 분석

`main.py`는 이미 두 계층으로 분리되어 있다.

| 계층 | 함수/위치 | 역할 |
|------|----------|------|
| 변환 로직 | `convert_pdf_to_images(pdf_path, output_dir, pages, dpi, image_format, prefix, verbose)` | PDF → 이미지 변환 핵심 로직. 파일 경로 기반 |
| CLI entrypoint | `main()` + `if __name__ == "__main__"` | argparse 인수 파싱, 파일 목록 수집, `convert_pdf_to_images` 호출 |
| 페이지 파싱 | `parse_page_range(page_str, total_pages)` | 페이지 범위 문자열 → 0-indexed 리스트 변환 |

**HTTP wrapper 재사용 경로**: `convert_pdf_to_images()`를 직접 임포트하면 CLI 없이도 변환 가능.
추가로 필요한 것은 업로드된 바이트 스트림을 임시 파일로 저장 후 경로를 넘기는 어댑터뿐이다.

---

## 2. HTTP Wrapper 설계

### 2.1 엔드포인트

```
POST /convert
Content-Type: multipart/form-data
```

### 2.2 Request 파라미터

| 필드 | 타입 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| `file` | File (PDF) | 필수 | — | 변환할 PDF 파일 (최대 50MB) |
| `pages` | string | 선택 | 전체 | 페이지 범위 (예: `1-5`, `1,3,7`, `all`) |
| `dpi` | int | 선택 | 150 | 출력 해상도 (50–600 범위 허용) |
| `format` | string | 선택 | `png` | 출력 형식 (`png`, `jpg`, `webp`) |

### 2.3 Response

```
200 OK
Content-Type: application/zip
Content-Disposition: attachment; filename="converted_images.zip"

[ZIP 파일 바이너리 — 변환된 이미지 파일 포함]
```

**에러 응답**:

| 상태 코드 | 조건 |
|----------|------|
| `400 Bad Request` | 파일 누락, PDF 아님, 페이지 범위 파싱 실패, dpi 범위 초과 |
| `413 Payload Too Large` | 업로드 50MB 초과 |
| `415 Unsupported Media Type` | PDF 아닌 파일 타입 |
| `422 Unprocessable Entity` | 손상된 PDF, 암호화된 PDF |
| `504 Gateway Timeout` | 변환 60초 초과 |

### 2.4 처리 흐름

```
multipart upload
  └─ 크기 검증 (≤ 50MB)
  └─ MIME 검증 (application/pdf)
  └─ tempfile.NamedTemporaryFile 저장
  └─ convert_pdf_to_images() 호출 (tempdir 출력)
  └─ 출력 이미지 → ZIP 압축 (메모리 내 BytesIO)
  └─ 임시 파일/디렉토리 즉시 삭제 (finally 블록)
  └─ ZIP 스트림 반환
```

---

## 3. 운영 경계값

| 항목 | 값 | 근거 |
|------|-----|------|
| 업로드 상한 | 50MB | Cloud Run request body 기본 한도 (32MB HTTP/1.1) 대비 여유, 실용적 PDF 크기 |
| 변환 타임아웃 | 60초 | Cloud Run 최대 request timeout 3600초 내, 일반 PDF 기준 충분 |
| 출력 파일 보존 | 응답 후 즉시 삭제 | 임시 파일 누적 방지, 개인정보 보호 (finally 블록 보장) |
| Cloud Run 메모리 | 512MB (권장 시작값) | PyMuPDF 고DPI 렌더링 시 메모리 사용 고려 |
| 동시성 | 1 (초기) | 단일 요청 완료 후 다음 처리, free-tier 내 안전 운영 |

---

## 4. Cloud Run Free-Tier 운영 기준

| 항목 | Free-tier 한도 | 예상 사용 |
|------|---------------|----------|
| 요청 수 | 200만 건/월 | 개인/소규모 도구 수준 (<<200만) |
| 컴퓨팅 | 180,000 vCPU-초/월, 360,000 GB-초/월 | 요청당 ~1–5초 예상, 여유 있음 |
| 네트워크 아웃바운드 | 1GB/월 | ZIP 응답 크기 제한 없지만 실제 사용량 낮음 |

**Free-tier 초과 방지 전략**:
- 동시성 1 설정으로 요청 burst 제한
- min-instances=0 (cold start 허용, 유휴 과금 없음)
- Cloud Run CPU는 요청 처리 중에만 할당

---

## 5. 구현 파일 구조 (Phase M 배포 시)

```
python-pdf-to-img/
├── main.py              # 기존 CLI (변경 없음)
├── app.py               # FastAPI HTTP wrapper (신규)
├── Dockerfile           # Cloud Run 컨테이너 (신규)
├── requirements.txt     # PyMuPDF, fastapi, uvicorn (신규)
└── docs/plan/
    └── cloud-run-wrapper-spec.md  # 이 파일
```

`app.py`는 `main.py`에서 `convert_pdf_to_images`, `parse_page_range`를 직접 임포트하여 재사용한다.
CLI `main()` 함수는 수정하지 않는다.

---

## 6. Phase M 게이트 (실제 배포 전 필수)

- [ ] 사용자 명시 승인 (repo visibility: public, Cloud Run 배포)
- [ ] `app.py` 구현 및 로컬 테스트
- [ ] `Dockerfile` 작성 및 `docker build` 검증
- [ ] Cloud Run 서비스 생성 (`gcloud run deploy`)
- [ ] 엔드포인트 smoke test (실제 PDF 업로드)

> 이 문서는 설계 명세이며, Phase M 항목은 사용자 승인 없이 실행하지 않는다.

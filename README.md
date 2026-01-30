## 사용법

```bash
# 설치
pip install PyMuPDF

# 기본 사용
python pdf_to_images.py document.pdf

# 출력 경로 지정
python pdf_to_images.py document.pdf -o ./output_images

# 여러 파일 한번에 처리
python pdf_to_images.py file1.pdf file2.pdf file3.pdf
python pdf_to_images.py *.pdf

# 특정 페이지만 추출
python pdf_to_images.py doc.pdf --pages 1-5
python pdf_to_images.py doc.pdf --pages "1,3,5,10-15"

# 고해상도 JPG로 출력
python pdf_to_images.py doc.pdf --dpi 300 --format jpg
```

## 주요 기능

| 옵션 | 설명 |
|------|------|
| `-o, --output` | 출력 디렉토리 지정 |
| `-p, --pages` | 페이지 범위 (예: `1-5`, `1,3,7`, `all`) |
| `-d, --dpi` | 해상도 (기본 150, 인쇄용 300 권장) |
| `-f, --format` | 이미지 형식 (png/jpg/webp) |
| `--prefix` | 출력 파일명 접두사 |
| `-q, --quiet` | 진행 상황 숨기기 |

---

## 개선사항 제안

**기능 확장**
- 멀티스레딩/멀티프로세싱으로 대용량 PDF 처리 속도 개선
- 암호 보호된 PDF 지원 (`--password` 옵션)
- 이미지 크기 지정 옵션 (`--width`, `--height`)
- GUI 버전 (PyQt/Tkinter)

**품질 옵션**
- JPEG 품질 조절 옵션
- 컬러/그레이스케일 선택
- 이미지 압축 레벨 설정

**사용성**
- 드래그앤드롭 지원 (exe로 빌드 시)
- 설정 파일 지원 (자주 쓰는 옵션 저장)
- 진행률 프로그레스바 (tqdm 사용)


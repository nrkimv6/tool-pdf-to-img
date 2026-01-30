#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PDF to Images Converter
PDF 문서를 이미지 파일로 변환하는 CLI 도구

사용법:
    python pdf_to_images.py input.pdf
    python pdf_to_images.py input.pdf -o ./output
    python pdf_to_images.py *.pdf --pages 1-5
    python pdf_to_images.py file1.pdf file2.pdf --dpi 200 --format png
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

try:
    import fitz  # PyMuPDF
except ImportError:
    print("Error: PyMuPDF가 설치되지 않았습니다.")
    print("설치 명령: pip install PyMuPDF")
    sys.exit(1)


def parse_page_range(page_str: str, total_pages: int) -> list[int]:
    """
    페이지 범위 문자열을 파싱하여 페이지 번호 리스트 반환
    
    지원 형식:
        - "1" : 단일 페이지
        - "1-5" : 범위
        - "1,3,5" : 개별 페이지
        - "1-3,7,9-11" : 혼합
        - "all" : 전체 페이지
    
    Args:
        page_str: 페이지 범위 문자열
        total_pages: PDF 총 페이지 수
        
    Returns:
        0-indexed 페이지 번호 리스트
    """
    if page_str.lower() == "all":
        return list(range(total_pages))
    
    pages = set()
    parts = page_str.replace(" ", "").split(",")
    
    for part in parts:
        if "-" in part:
            start, end = part.split("-", 1)
            start = int(start) if start else 1
            end = int(end) if end else total_pages
            
            # 범위 검증
            start = max(1, min(start, total_pages))
            end = max(1, min(end, total_pages))
            
            pages.update(range(start - 1, end))  # 0-indexed로 변환
        else:
            page_num = int(part)
            if 1 <= page_num <= total_pages:
                pages.add(page_num - 1)  # 0-indexed로 변환
    
    return sorted(pages)


def convert_pdf_to_images(
    pdf_path: Path,
    output_dir: Path,
    pages: Optional[str] = None,
    dpi: int = 150,
    image_format: str = "png",
    prefix: Optional[str] = None,
    verbose: bool = True
) -> list[Path]:
    """
    PDF 파일을 이미지로 변환
    
    Args:
        pdf_path: PDF 파일 경로
        output_dir: 출력 디렉토리
        pages: 변환할 페이지 범위 (None이면 전체)
        dpi: 출력 해상도 (기본: 150)
        image_format: 출력 형식 (png, jpg, jpeg, webp)
        prefix: 출력 파일명 접두사 (None이면 PDF 파일명 사용)
        verbose: 진행 상황 출력 여부
        
    Returns:
        생성된 이미지 파일 경로 리스트
    """
    # PDF 열기
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error: PDF 파일을 열 수 없습니다 - {pdf_path}")
        print(f"  상세: {e}")
        return []
    
    total_pages = len(doc)
    
    if verbose:
        print(f"\n📄 {pdf_path.name} (총 {total_pages}페이지)")
    
    # 페이지 범위 결정
    if pages:
        page_indices = parse_page_range(pages, total_pages)
    else:
        page_indices = list(range(total_pages))
    
    if not page_indices:
        print(f"  ⚠️  유효한 페이지가 없습니다.")
        doc.close()
        return []
    
    # 출력 디렉토리 생성
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 파일명 접두사 설정
    file_prefix = prefix if prefix else pdf_path.stem
    
    # 이미지 형식 설정
    fmt = image_format.lower()
    if fmt == "jpg":
        fmt = "jpeg"
    
    # DPI를 zoom factor로 변환 (기본 72 DPI 기준)
    zoom = dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)
    
    created_files = []
    
    for i, page_num in enumerate(page_indices):
        page = doc[page_num]
        
        # 페이지를 이미지로 렌더링
        pix = page.get_pixmap(matrix=matrix)
        
        # 파일명 생성 (페이지 번호는 1-indexed로 표시)
        output_filename = f"{file_prefix}_page_{page_num + 1:04d}.{fmt}"
        output_path = output_dir / output_filename
        
        # 이미지 저장
        if fmt == "jpeg":
            pix.save(output_path, output=fmt, jpg_quality=95)
        else:
            pix.save(output_path)
        
        created_files.append(output_path)
        
        if verbose:
            progress = (i + 1) / len(page_indices) * 100
            print(f"  [{progress:5.1f}%] 페이지 {page_num + 1} → {output_filename}")
    
    doc.close()
    
    if verbose:
        print(f"  ✅ {len(created_files)}개 이미지 생성 완료")
    
    return created_files


def main():
    parser = argparse.ArgumentParser(
        description="PDF 문서를 이미지 파일로 변환합니다.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  %(prog)s document.pdf                      # 기본 설정으로 변환
  %(prog)s document.pdf -o ./images          # 출력 경로 지정
  %(prog)s *.pdf --pages 1-10                # 여러 파일, 1-10페이지만
  %(prog)s doc.pdf --pages "1,3,5-7"         # 특정 페이지들
  %(prog)s doc.pdf --dpi 300 --format jpg    # 고해상도 JPG
  %(prog)s doc.pdf --prefix "scan"           # 파일명 접두사 지정

페이지 범위 형식:
  - 단일 페이지: "5"
  - 범위: "1-10"
  - 개별 선택: "1,3,5,7"
  - 혼합: "1-3,7,10-15"
  - 전체: "all"
        """
    )
    
    parser.add_argument(
        "input",
        nargs="+",
        help="변환할 PDF 파일 (여러 파일 또는 와일드카드 사용 가능)"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="출력 디렉토리 (기본: PDF 파일과 같은 위치에 '[파일명]_images' 폴더)"
    )
    
    parser.add_argument(
        "-p", "--pages",
        type=str,
        default=None,
        help="변환할 페이지 범위 (예: '1-5', '1,3,5', '1-3,7,10-15', 'all')"
    )
    
    parser.add_argument(
        "-d", "--dpi",
        type=int,
        default=150,
        help="출력 해상도 DPI (기본: 150, 인쇄용: 300 권장)"
    )
    
    parser.add_argument(
        "-f", "--format",
        type=str,
        choices=["png", "jpg", "jpeg", "webp"],
        default="png",
        help="출력 이미지 형식 (기본: png)"
    )
    
    parser.add_argument(
        "--prefix",
        type=str,
        default=None,
        help="출력 파일명 접두사 (기본: PDF 파일명)"
    )
    
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="진행 상황 출력 숨기기"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )
    
    args = parser.parse_args()
    
    # 입력 파일 수집
    input_files = []
    for pattern in args.input:
        path = Path(pattern)
        if path.exists():
            input_files.append(path)
        else:
            # 와일드카드 패턴 처리
            matches = list(Path(".").glob(pattern))
            input_files.extend(matches)
    
    # PDF 파일만 필터링
    pdf_files = [f for f in input_files if f.suffix.lower() == ".pdf"]
    
    if not pdf_files:
        print("Error: 유효한 PDF 파일을 찾을 수 없습니다.")
        sys.exit(1)
    
    # 중복 제거
    pdf_files = list(dict.fromkeys(pdf_files))
    
    verbose = not args.quiet
    
    if verbose:
        print(f"🔄 PDF to Images Converter")
        print(f"   처리할 파일: {len(pdf_files)}개")
        print(f"   해상도: {args.dpi} DPI")
        print(f"   출력 형식: {args.format.upper()}")
        if args.pages:
            print(f"   페이지 범위: {args.pages}")
    
    total_images = 0
    
    for pdf_file in pdf_files:
        # 출력 디렉토리 결정
        if args.output:
            if len(pdf_files) == 1:
                output_dir = Path(args.output)
            else:
                # 여러 파일일 경우 각 PDF별 하위 폴더 생성
                output_dir = Path(args.output) / pdf_file.stem
        else:
            output_dir = pdf_file.parent / f"{pdf_file.stem}_images"
        
        created = convert_pdf_to_images(
            pdf_path=pdf_file,
            output_dir=output_dir,
            pages=args.pages,
            dpi=args.dpi,
            image_format=args.format,
            prefix=args.prefix,
            verbose=verbose
        )
        
        total_images += len(created)
    
    if verbose:
        print(f"\n🎉 완료! 총 {total_images}개 이미지 생성")


if __name__ == "__main__":
    main()
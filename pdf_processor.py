import os
import requests
from PyPDF2 import PdfReader
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFProcessor:
    """PDF 파일을 처리하고 텍스트를 추출하는 클래스"""
    
    def __init__(self, download_dir: str = "pdfs"):
        self.download_dir = download_dir
        os.makedirs(download_dir, exist_ok=True)
    
    def download_pdf_from_url(self, url: str, filename: str) -> Optional[str]:
        """URL에서 PDF 파일을 다운로드합니다."""
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            filepath = os.path.join(self.download_dir, filename)
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"PDF 다운로드 완료: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"PDF 다운로드 실패: {e}")
            return None
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """PDF 파일에서 텍스트를 추출합니다."""
        try:
            reader = PdfReader(pdf_path)
            text = ""
            
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text.strip():
                    text += f"\n--- 페이지 {page_num + 1} ---\n"
                    text += page_text
                    text += "\n"
            
            logger.info(f"텍스트 추출 완료: {len(text)} 문자")
            return text
        except Exception as e:
            logger.error(f"텍스트 추출 실패: {e}")
            return ""
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """텍스트를 청크로 나눕니다."""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # 문장 경계에서 자르기
            if end < len(text):
                # 마지막 마침표나 줄바꿈을 찾아서 자르기
                last_period = text.rfind('.', start, end)
                last_newline = text.rfind('\n', start, end)
                cut_point = max(last_period, last_newline)
                
                if cut_point > start:
                    end = cut_point + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
            if start >= len(text):
                break
        
        logger.info(f"텍스트를 {len(chunks)}개 청크로 분할")
        return chunks
    
    def process_pdf_file(self, pdf_path: str) -> List[str]:
        """PDF 파일을 처리하여 청크로 나눈 텍스트를 반환합니다."""
        text = self.extract_text_from_pdf(pdf_path)
        if text:
            return self.chunk_text(text)
        return []
    
    def get_pdf_metadata(self, pdf_path: str) -> Dict:
        """PDF 파일의 메타데이터를 추출합니다."""
        try:
            reader = PdfReader(pdf_path)
            metadata = {
                'num_pages': len(reader.pages),
                'filename': os.path.basename(pdf_path),
                'file_size': os.path.getsize(pdf_path)
            }
            
            if reader.metadata:
                metadata.update({
                    'title': reader.metadata.get('/Title', ''),
                    'author': reader.metadata.get('/Author', ''),
                    'subject': reader.metadata.get('/Subject', ''),
                    'creator': reader.metadata.get('/Creator', '')
                })
            
            return metadata
        except Exception as e:
            logger.error(f"메타데이터 추출 실패: {e}")
            return {}
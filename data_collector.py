import os
import requests
import json
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import logging
from datetime import datetime
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataCollector:
    """공공데이터 포탈에서 주택정책 보도자료를 수집하는 클래스"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("DECODING_API_KEY")
        if not self.api_key:
            logger.warning("API 키가 설정되지 않았습니다.")
        
        self.base_url = "https://www.data.go.kr"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_housing_policy_releases(self, page: int = 1, rows: int = 10) -> List[Dict]:
        """주택정책 보도자료 목록을 가져옵니다."""
        try:
            # 공공데이터 포탈 API 엔드포인트
            url = "https://www.data.go.kr/tcs/dss/selectApiDataDetailView.do"
            params = {
                'publicDataPk': '15109325',
                'page': page,
                'rows': rows
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            # HTML 파싱
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 보도자료 목록 추출 (실제 구조에 따라 수정 필요)
            releases = []
            
            # 테이블이나 리스트에서 보도자료 정보 추출
            # 실제 웹사이트 구조에 맞게 수정
            items = soup.find_all('tr') or soup.find_all('li')
            
            for item in items:
                try:
                    # 제목, 날짜, 링크 등 추출
                    title_elem = item.find('a') or item.find('h3') or item.find('td')
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        
                        # 링크 추출
                        link = title_elem.get('href') if title_elem.name == 'a' else None
                        if link and not link.startswith('http'):
                            link = self.base_url + link
                        
                        # 날짜 추출
                        date_elem = item.find('span', class_='date') or item.find('td', class_='date')
                        date = date_elem.get_text(strip=True) if date_elem else ""
                        
                        releases.append({
                            'title': title,
                            'date': date,
                            'link': link,
                            'source': '공공데이터포털'
                        })
                        
                except Exception as e:
                    logger.warning(f"항목 파싱 실패: {e}")
                    continue
            
            logger.info(f"{len(releases)}개의 보도자료를 찾았습니다.")
            return releases
            
        except Exception as e:
            logger.error(f"보도자료 목록 가져오기 실패: {e}")
            return []
    
    def get_pdf_links_from_release(self, release_url: str) -> List[str]:
        """보도자료 페이지에서 PDF 링크들을 추출합니다."""
        try:
            response = self.session.get(release_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            pdf_links = []
            
            # PDF 링크 찾기
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.lower().endswith('.pdf'):
                    if not href.startswith('http'):
                        href = self.base_url + href
                    pdf_links.append(href)
            
            logger.info(f"PDF 링크 {len(pdf_links)}개 발견")
            return pdf_links
            
        except Exception as e:
            logger.error(f"PDF 링크 추출 실패: {e}")
            return []
    
    def search_housing_policy_pdfs(self, keywords: List[str] = None) -> List[Dict]:
        """주택정책 관련 PDF 파일들을 검색합니다."""
        if keywords is None:
            keywords = ['주택정책', '보도자료', '주택', '부동산', '정책']
        
        all_pdfs = []
        
        try:
            # 여러 페이지에서 검색
            for page in range(1, 6):  # 최대 5페이지
                releases = self.get_housing_policy_releases(page=page)
                
                for release in releases:
                    title = release.get('title', '').lower()
                    
                    # 키워드가 포함된 보도자료만 필터링
                    if any(keyword in title for keyword in keywords):
                        link = release.get('link')
                        if link:
                            pdf_links = self.get_pdf_links_from_release(link)
                            
                            for pdf_link in pdf_links:
                                all_pdfs.append({
                                    'title': release['title'],
                                    'date': release['date'],
                                    'pdf_url': pdf_link,
                                    'source_url': link
                                })
                
                # 요청 간격 조절
                time.sleep(1)
            
            logger.info(f"총 {len(all_pdfs)}개의 PDF 파일을 찾았습니다.")
            return all_pdfs
            
        except Exception as e:
            logger.error(f"PDF 검색 실패: {e}")
            return []
    
    def save_pdf_info(self, pdfs: List[Dict], filename: str = "pdf_info.json"):
        """PDF 정보를 JSON 파일로 저장합니다."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(pdfs, f, ensure_ascii=False, indent=2)
            
            logger.info(f"PDF 정보를 {filename}에 저장했습니다.")
            
        except Exception as e:
            logger.error(f"PDF 정보 저장 실패: {e}")
    
    def load_pdf_info(self, filename: str = "pdf_info.json") -> List[Dict]:
        """저장된 PDF 정보를 로드합니다."""
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
            
        except Exception as e:
            logger.error(f"PDF 정보 로드 실패: {e}")
            return []
    
    def get_sample_pdf_urls(self) -> List[str]:
        """샘플 PDF URL들을 반환합니다 (테스트용)"""
        # 실제 공공데이터 포탈의 주택정책 PDF URL들
        # 실제 운영 시에는 위의 메서드들을 사용하여 동적으로 수집
        sample_urls = [
            "https://www.molit.go.kr/news/news_list.jsp?news_type=news&page=1",
            # 실제 PDF URL들을 여기에 추가
        ]
        
        return sample_urls
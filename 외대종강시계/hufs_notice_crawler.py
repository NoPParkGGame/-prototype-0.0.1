import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

class HUFSNoticeCrawler:
    """
    한국외대 공지사항 크롤러
    - 메인 페이지의 공지사항을 크롤링
    - 캐시 기능으로 서버 부하 감소
    """
    
    def __init__(self):
        """
        크롤러 초기화
        - base_url: 크롤링 대상 URL
        - headers: 브라우저 에뮬레이션을 위한 헤더
        - cache_file: 캐시 저장 파일 경로
        """
        self.base_url = "https://www.hufs.ac.kr/hufs/11281/subview.do"
        self.domain = "https://www.hufs.ac.kr"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.cache_file = 'notice_cache.json'
    
    def _load_cache(self):
        """
        캐시된 공지사항 데이터 로드
        Returns:
            dict or None: 캐시된 데이터 또는 실패 시 None
        """
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def _save_cache(self, notices):
        """
        공지사항 데이터 캐시 저장
        Args:
            notices (list): 저장할 공지사항 리스트
        """
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'notices': notices
            }
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"캐시 저장 실패: {e}")

    def _extract_notice_info(self, row):
        """
        공지사항 행에서 정보 추출
        Args:
            row (BeautifulSoup): 공지사항 행 요소
        Returns:
            dict or None: 추출된 공지사항 정보 또는 실패 시 None
        """
        title_td = row.find('td', class_='td-subject')
        date_td = row.find('td', class_='td-date')
        writer_td = row.find('td', class_='td-write')
        
        if not (title_td and date_td):
            return None
            
        link_tag = title_td.find('a')
        if not link_tag:
            return None
            
        # 공지사항 정보 추출
        link = link_tag.get('href', '')
        title = (link_tag.find('strong') or link_tag).text.strip()
        full_date = date_td.text.strip()
        date = '.'.join(full_date.split('.')[1:3])  # MM.DD 형식으로 변환
        writer = writer_td.text.strip() if writer_td else ''
        
        return {
            'date': date,
            'title': title,
            'writer': writer,
            'link': self.domain + link if link else ''
        }

    def get_notices(self):
        """
        공지사항 크롤링 실행
        Returns:
            list: 크롤링된 공지사항 리스트
        """
        try:
            # 공지사항 페이지 요청
            response = requests.get(self.base_url, headers=self.headers)
            response.raise_for_status()
            
            # HTML 파싱
            soup = BeautifulSoup(response.text, 'html.parser')
            notice_rows = soup.find_all('tr', class_='')
            
            # 공지사항 정보 추출
            notices = []
            for row in notice_rows:
                notice_info = self._extract_notice_info(row)
                if notice_info:
                    notices.append(notice_info)
            
            # 캐시 저장 및 결과 반환
            self._save_cache(notices)
            return notices

        except requests.RequestException as e:
            print(f"공지사항 크롤링 실패: {e}")
            return []

if __name__ == "__main__":
    # 크롤러 테스트 코드
    crawler = HUFSNoticeCrawler()
    notices = crawler.get_notices()
    
    # 결과 출력
    for notice in notices:
        print("\n" + "="*20)
        print(f"날짜: {notice['date']}")
        print(f"제목: {notice['title']}")
        print(f"작성자: {notice['writer']}")
        print(f"링크: {notice['link']}")
import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime, timedelta

class HUFSScheduleCrawler:
    """
    한국외대 학사일정 크롤러
    - 학기 시작/종료 일자 크롤링
    - 24시간 캐시 기능으로 서버 부하 감소
    """
    
    def __init__(self):
        """
        크롤러 초기화
        - base_url: 메인 페이지 URL (학사일정 섹션)
        - headers: 브라우저 에뮬레이션용 헤더
        - cache_file: 캐시 파일 경로
        - cache_duration: 캐시 유효 기간 (24시간)
        """
        self.base_url = "https://www.hufs.ac.kr/hufs/index.do#section4"
        self.domain = "https://www.hufs.ac.kr"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.cache_file = 'schedule_cache.json'
        self.cache_duration = timedelta(hours=24)

    def _load_cache(self):
        """
        캐시된 학사일정 데이터 로드
        Returns:
            dict or None: 유효한 캐시 데이터 또는 None
        """
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    cache_time = datetime.fromisoformat(data['timestamp'])
                    
                    # 캐시 유효성 검사
                    if cache_time + self.cache_duration > datetime.now():
                        return data['schedule']
        except Exception as e:
            print(f"캐시 로드 실패: {e}")
        return None

    def _save_cache(self, schedule_dates):
        """
        학사일정 데이터 캐시 저장
        Args:
            schedule_dates (dict): 저장할 학사일정 데이터
        """
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'schedule': schedule_dates
            }
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"캐시 저장 실패: {e}")

    def _extract_schedule_dates(self, content_list):
        """
        학사일정 리스트에서 날짜 정보 추출
        Args:
            content_list (ResultSet): BeautifulSoup으로 파싱된 학사일정 리스트
        Returns:
            dict: 추출된 학사일정 날짜
        """
        schedule_dates = {
            'first_start': None,   # 1학기 개강일
            'first_end': None,     # 1학기 종강일
            'second_start': None,  # 2학기 개강일
            'second_end': None     # 2학기 종강일
        }
        
        for item in content_list:
            date_elems = item.find_all('p', class_='list-date')
            event_elems = item.find_all('p', class_='list-content')
            
            for date, event in zip(date_elems, event_elems):
                date_str = date.get_text(strip=True).split('~')[-1].strip()
                event_str = event.get_text(strip=True)
                
                # 주요 학사일정 매칭
                if '제1학기 개강' in event_str:
                    schedule_dates['first_start'] = date_str
                elif '제1학기 기말시험' in event_str:
                    schedule_dates['first_end'] = date_str
                elif '제2학기 개강' in event_str:
                    schedule_dates['second_start'] = date_str
                elif '제2학기 기말시험' in event_str:
                    schedule_dates['second_end'] = date_str
                    
        return schedule_dates

    def get_schedule(self):
        """
        학사일정 크롤링 실행
        Returns:
            dict: 학사일정 날짜 정보
        """
        # 캐시 확인
        cached_data = self._load_cache()
        if cached_data:
            return cached_data

        try:
            # 메인 페이지에서 학사일정 링크 추출
            response = requests.get(self.base_url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            schedule_link = soup.select_one('#top_k2wiz_GNB_11360')
            if not schedule_link:
                raise ValueError("학사일정 링크를 찾을 수 없습니다.")

            # 학사일정 페이지 크롤링
            schedule_url = self.domain + schedule_link['href']
            schedule_response = requests.get(schedule_url, headers=self.headers)
            schedule_response.raise_for_status()
            
            schedule_soup = BeautifulSoup(schedule_response.text, 'html.parser')
            content_wrap = schedule_soup.find('div', class_='wrap-contents')
            
            if not content_wrap:
                raise ValueError("학사일정 내용을 찾을 수 없습니다.")
            
            # 학사일정 추출 및 캐시 저장
            schedule_dates = self._extract_schedule_dates(content_wrap.find_all('li'))
            self._save_cache(schedule_dates)
            return schedule_dates

        except Exception as e:
            print(f"학사일정 크롤링 실패: {e}")
            # 기본 일정 반환
            default_dates = {
                'first_start': "03.04",
                'first_end': "06.20",
                'second_start': "09.01",
                'second_end': "12.19"
            }
            self._save_cache(default_dates)
            return default_dates

if __name__ == "__main__":
    # 크롤러 테스트
    crawler = HUFSScheduleCrawler()
    dates = crawler.get_schedule()
    print("학사일정 크롤링 결과:")
    for key, value in dates.items():
        print(f"{key}: {value}")
from datetime import datetime
import sys
import os

# 상대 import 시도, 실패 시 절대 import
try:
    from .crawler.schedule import HUFSScheduleCrawler
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from crawler.schedule import HUFSScheduleCrawler

class HUFSClock:
    """
    한국외대 학사일정 기반 타이머
    - 학기와 방학 기간을 자동으로 판단
    - 종강/개강까지 남은 시간을 계산
    - 크롤링된 학사일정을 기반으로 동작
    """

    def __init__(self):
        """
        타이머 초기화
        - 학사일정 크롤러를 통해 날짜 정보 로드
        - 학기 시작/종료일을 datetime 객체로 변환
        - 현재 학기 상태 초기화
        """
        # 크롤러를 통해 학사일정 로드
        crawler = HUFSScheduleCrawler()
        schedule_dates = crawler.get_schedule()
        
        # 각 학기 시작/종료일 설정
        self.first_semester_start = self._parse_date(schedule_dates['first_start'])   # 1학기 시작일
        self.first_semester_end = self._parse_date(schedule_dates['first_end'])       # 1학기 종료일
        self.second_semester_start = self._parse_date(schedule_dates['second_start']) # 2학기 시작일
        self.second_semester_end = self._parse_date(schedule_dates['second_end'])     # 2학기 종료일
        
        # 초기 상태 설정
        self.is_semester = True  # 학기 중 여부
        self.current_semester = self._determine_current_semester()  # 현재 학기 판단
    
    def _parse_date(self, date_str):
        """
        날짜 문자열을 datetime 객체로 변환
        Args:
            date_str (str): "MM.DD" 형식의 날짜 문자열
        Returns:
            datetime: 현재 연도의 해당 날짜 객체
        """
        current_year = datetime.now().year
        month, day = map(int, date_str.split('.'))
        return datetime(current_year, month, day)
    
    def _determine_current_semester(self):
        """
        현재 날짜가 속한 학기 판단
        Returns:
            int: 1(1학기), 2(2학기), 0(방학)
        """
        current = datetime.now()
        # 각 학기 기간과 현재 날짜 비교
        if self.first_semester_start <= current <= self.first_semester_end:
            return 1
        elif self.second_semester_start <= current <= self.second_semester_end:
            return 2
        return 0  # 학기 기간에 속하지 않으면 방학
    
    def check_period(self):
        """
        현재 학기/방학 상태 업데이트
        - 현재 학기 재판단
        - 학기/방학 플래그 설정
        """
        self.current_semester = self._determine_current_semester()
        self.is_semester = (self.current_semester != 0)  # 0이 아니면 학기 중
    
    def get_remaining_time(self):
        """
        다음 이벤트(종강/개강)까지 남은 시간 계산
        Returns:
            tuple: (남은 일수, 시간, 분, 초, 기간 타입)
        """
        current = datetime.now()
        
        # 현재 상태에 따른 목표 날짜 설정
        if self.current_semester == 1:  # 1학기
            target_date = self.first_semester_end
        elif self.current_semester == 2:  # 2학기
            target_date = self.second_semester_end
        else:  # 방학 중
            if current > self.second_semester_end:  # 겨울방학
                target_date = self.first_semester_start
            else:  # 여름방학
                target_date = self.second_semester_start
        
        # 남은 시간 계산
        remaining = target_date - current
        days = remaining.days
        hours = remaining.seconds // 3600
        minutes = (remaining.seconds % 3600) // 60
        seconds = remaining.seconds % 60
        
        # 기간 타입 설정 (종강/개강)
        if days == 0 and self.is_semester:
            period_type = "종강! 고생했어요"
        else:
            period_type = f"{self.current_semester}학기 종강({target_date.strftime('%m.%d')})까지" if self.is_semester else f"다음 학기개강({target_date.strftime('%m.%d')})까지..."
        
        return days, hours, minutes, seconds, period_type
    
    def display_time(self):
        """
        현재 상태와 남은 시간을 문자열로 반환
        Returns:
            str: 포맷팅된 시간 정보 문자열
        """
        self.check_period()  # 현재 상태 업데이트
        days, hours, minutes, seconds, period_type = self.get_remaining_time()
        if period_type == "종강! 고생했어요":
            return period_type
        else:
            return f"{period_type}까지 남은 시간:\n{days}일 {hours}시간 {minutes}분 {seconds}초"

def main():
    """테스트용 메인 함수"""
    clock = HUFSClock()
    print(clock.display_time())

if __name__ == "__main__":
    main()
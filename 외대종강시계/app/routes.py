from flask import render_template, jsonify
from app.models import HUFSClock, HUFSNoticeCrawler
from datetime import datetime
from app import app

"""
HUFS 종강시계 Flask 애플리케이션
- 실시간 타이머 업데이트
- 공지사항 자동 크롤링
- 테마 변경 기능
"""

@app.route('/')
def home():
    """메인 페이지 렌더링
    - 타이머 초기값 설정
    - 공지사항 초기 로드
    - 현재 시간 표시
    """
    # 타이머 초기화
    clock = HUFSClock()
    days, hours, minutes, seconds, period_type = clock.get_remaining_time()
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 공지사항 초기 로드
    notice_crawler = HUFSNoticeCrawler()
    notices = notice_crawler.get_notices()
    last_update = datetime.now().strftime('%Y.%m.%d %H:%M:%S')
    
    # 템플릿 렌더링
    return render_template('index.html',
                         days=days,
                         hours=hours,
                         minutes=minutes,
                         seconds=seconds,
                         period_type=period_type,
                         current_time=current_time,
                         last_update=last_update,
                         notices=notices)

@app.route('/update')
def update_time():
    """실시간 시간 정보 업데이트 API
    Returns:
        JSON: {
            days: 남은 일수,
            hours: 남은 시간,
            minutes: 남은 분,
            seconds: 남은 초,
            period_type: 현재 기간 타입(종강/개강),
            current_time: 현재 시각
        }
    """
    clock = HUFSClock()
    days, hours, minutes, seconds, period_type = clock.get_remaining_time()
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    return jsonify({
        'days': days,
        'hours': hours,
        'minutes': minutes,
        'seconds': seconds,
        'period_type': period_type,
        'current_time': current_time
    })

@app.route('/notices')
def get_notices():
    """공지사항 새로고침 API
    Returns:
        성공 시: {notices: 공지사항 목록, last_update: 갱신 시각}
        실패 시: {error: 오류 내용, message: 오류 메시지}, 500
    """
    try:
        print("공지사항 새로고침 요청 받음") # 디버깅용 로그
        # 공지사항 크롤링
        notice_crawler = HUFSNoticeCrawler()
        notices = notice_crawler.get_notices()
        last_update = datetime.now().strftime('%Y.%m.%d %H:%M:%S')
        
        return jsonify({
            'notices': notices,
            'last_update': last_update
        })
    
    except Exception as e:
        print(f"공지사항 업데이트 실패: {str(e)}") # 디버깅용 로그
        return jsonify({
            'error': str(e),
            'message': '공지사항 업데이트 실패'
        }), 500

@app.route('/schedule')
def get_schedule():
    """학사 일정 정보 제공 API
    Returns:
        JSON: {
            is_semester: 현재 학기 여부,
            current_semester: 현재 학기 (1: 1학기, 2: 2학기, 0: 방학),
            end_date: 현재 학기 종료일 (형식: YYYY년 MM월 DD일),
            next_start_date: 다음 학기 시작일 (형식: YYYY년 MM월 DD일, 방학 중일 경우)
        }
    """
    try:
        clock = HUFSClock()
        current_semester = clock.current_semester
        is_semester = clock.is_semester
        
        response = {
            'is_semester': is_semester,
            'current_semester': current_semester
        }
        
        if is_semester:
            if current_semester == 1:
                response['end_date'] = clock.first_semester_end.strftime('%Y년 %m월 %d일')
            else:
                response['end_date'] = clock.second_semester_end.strftime('%Y년 %m월 %d일')
        else:
            if current_semester == 0:  # 방학 중
                if datetime.now() > clock.second_semester_end:  # 겨울방학
                    response['next_start_date'] = clock.first_semester_start.strftime('%Y년 %m월 %d일')
                else:  # 여름방학
                    response['next_start_date'] = clock.second_semester_start.strftime('%Y년 %m월 %d일')
        
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)  # 개발 서버 실행 (디버그 모드)
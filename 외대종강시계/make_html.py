from flask import Flask, render_template, jsonify
from hufs_notice_crawler import HUFSNoticeCrawler
from time_info import HUFSClock
from datetime import datetime

"""
HUFS 종강시계 Flask 애플리케이션
- 실시간 타이머 업데이트
- 공지사항 자동 크롤링
- 테마 변경 기능
"""

# Flask 앱 초기화 (정적/템플릿 파일 경로 설정)
app = Flask(__name__, 
           static_folder='./static',
           template_folder='./templates'
)

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
        # 공지사항 크롤링
        notice_crawler = HUFSNoticeCrawler()
        notices = notice_crawler.get_notices()
        last_update = datetime.now().strftime('%Y.%m.%d %H:%M:%S')
        
        return jsonify({
            'notices': notices,
            'last_update': last_update
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': '공지사항 업데이트 실패'
        }), 500

if __name__ == '__main__':
    app.run(debug=True)  # 개발 서버 실행 (디버그 모드)
/**
 * DOM 요소 접근 안전하게 처리
 */
function getElement(selector) {
    const element = document.querySelector(selector);
    if (!element) {
        console.warn(`Element not found: ${selector}`);
        return null;
    }
    return element;
}

/**
 * 시간 정보 업데이트 함수
 */
let logCounter = 0;

function updateTime() {
    fetch('/update')
        .then(response => response.json())
        .then(data => {
            const periodType = getElement('.period-type');
            const timer = getElement('.timer');
            const currentTime = getElement('#currentTime');

            if (periodType && timer && currentTime) {
                const timerText = `${data.days}일 ${data.hours}시간 ${data.minutes}분 ${data.seconds}초`;
                periodType.textContent = data.period_type;
                timer.textContent = timerText;
                currentTime.textContent = data.current_time;
                
                if (logCounter % 10 === 0) {
                    console.log(`[${new Date().toLocaleTimeString()}] 시간 업데이트: ${timerText}`);
                }
                logCounter++;
            }
        })
        .catch(error => console.error('시간 업데이트 실패:', error));
}

// 자동 시간 업데이트 설정 (1초마다)
setInterval(updateTime, 1000);

// 초기 실행
updateTime(); // 초기 실행

/**
 * 테마 변경 함수
 * @param {string} theme - 적용할 테마 ('default' 또는 'dark')
 */
function changeTheme(theme) {
    const body = getElement('body');
    const defaultBg = getElement('.background.default');
    const darkBg = getElement('.background.dark');
    
    if (body && defaultBg && darkBg) {
        body.className = `theme-${theme}`;
        
        if (theme === 'dark') {
            defaultBg.style.opacity = '0';
            darkBg.style.opacity = '1';
        } else {
            defaultBg.style.opacity = '1';
            darkBg.style.opacity = '0';
        }
        
        localStorage.setItem('theme', theme);
    }
}

/**
 * 공지사항 새로고침 함수
 * - 서버로부터 최신 공지사항을 가져옴
 * - 테이블 내용 업데이트
 * - 마지막 업데이트 시간 표시
 */
async function refreshNotices() {
    console.log('새로고침 함수 호출됨');  // 디버깅 로그
    
    try {
        const response = await fetch('/notices');
        const data = await response.json();
        
        console.log('서버 응답:', data);  // 디버깅 로그
        
        // 공지사항 테이블 업데이트
        const tbody = document.querySelector('.notice-table tbody');
        tbody.innerHTML = data.notices.map(notice => `
            <tr onclick="window.open('${notice.link}', '_blank')" class="notice-row">
                <td class="notice-title-cell">
                    <div class="notice-content">
                        <span class="notice-date">${notice.date}</span>
                        <span class="notice-title-text">${notice.title}</span>
                    </div>
                </td>
            </tr>
        `).join('');

        // 마지막 업데이트 시간 갱신
        const lastUpdateElement = document.querySelector('.last-update');
        lastUpdateElement.textContent = data.last_update;
        
        // 애니메이션 적용
        lastUpdateElement.classList.remove('highlight');
        void lastUpdateElement.offsetWidth;  // 리플로우 트리거
        lastUpdateElement.classList.add('highlight');
        
        console.log('새로고침 완료');  // 디버깅 로그
    } catch (error) {
        console.error('새로고침 실패:', error);
    }
}

/**
 * 마지막 업데이트 시간 표시 및 애니메이션 적용
 * @param {string} time - 업데이트 시간 문자열
 */
function updateLastUpdateTime(time) {
    const lastUpdateElement = document.querySelector('.last-update');
    lastUpdateElement.textContent = time;
    
    // 애니메이션 효과 적용
    lastUpdateElement.classList.remove('highlight');
    void lastUpdateElement.offsetWidth; // 리플로우 트리거
    lastUpdateElement.classList.add('highlight');
}

/**
 * 에러 메시지 표시
 */
function showErrorMessage() {
    const tbody = document.querySelector('.notice-table tbody');
    tbody.innerHTML = `
        <tr>
            <td>
                <div class="error-message">네트워크 오류</div>
            </td>
        </tr>
    `;
}

/**
 * 초기 학사일정 정보 로깅
 */
function logInitialSchedule() {
    fetch('/schedule')  // 새로운 엔드포인트 필요
        .then(response => response.json())
        .then(data => {
            console.log('=== 학사일정 정보 ===');
            if (data.is_semester) {
                console.log(`현재: ${data.current_semester}학기 진행 중`);
                console.log(`종강일: ${data.end_date}`);
            } else {
                console.log('현재: 방학 중');
                console.log(`다음 학기 개강일: ${data.next_start_date}`);
            }
            console.log('==================');
        })
        .catch(error => console.error('학사일정 정보 로드 실패:', error));
}

// 페이지 로드 시 저장된 테마 적용
document.addEventListener('DOMContentLoaded', () => {
    // 초기 학사일정 정보 로깅
    logInitialSchedule();
    
    const savedTheme = localStorage.getItem('theme') || 'default';
    changeTheme(savedTheme);

    const refreshBtn = document.querySelector('.refresh-btn');
    if (refreshBtn) {
        console.log('새로고침 버튼 찾음');  // 디버깅 로그
        refreshBtn.addEventListener('click', refreshNotices);
    } else {
        console.log('새로고침 버튼을 찾을 수 없음');  // 디버깅 로그
    }
});



/**
 * 시간 정보 업데이트 함수
 * - 서버로부터 최신 시간 정보를 가져옴
 * - DOM 요소 업데이트
 */
function updateTime() {
    fetch('/update')
        .then(response => response.json())
        .then(data => {
            // 타이머와 현재 시간 업데이트
            document.querySelector('.period-type').textContent = data.period_type;
            document.querySelector('.timer').textContent = 
                `${data.days}일 ${data.hours}시간 ${data.minutes}분 ${data.seconds}초`;
            document.getElementById('currentTime').textContent = data.current_time;
        })
        .catch(error => console.error('시간 업데이트 실패:', error));
}

// 자동 시간 업데이트 설정
setInterval(updateTime, 1000);
updateTime(); // 초기 실행

/**
 * 테마 변경 함수
 * @param {string} theme - 적용할 테마 ('default' 또는 'dark')
 */
function changeTheme(theme) {
    // DOM 요소 참조
    const body = document.querySelector('body');
    const defaultBg = document.querySelector('.background.default');
    const darkBg = document.querySelector('.background.dark');
    
    // 테마 클래스 적용
    body.className = `theme-${theme}`;
    
    // 배경 이미지 전환
    if (theme === 'dark') {
        defaultBg.style.opacity = '0';
        darkBg.style.opacity = '1';
    } else {
        defaultBg.style.opacity = '1';
        darkBg.style.opacity = '0';
    }

    // 테마 설정 저장
    localStorage.setItem('theme', theme);
}

/**
 * 공지사항 새로고침 함수
 * - 서버로부터 최신 공지사항을 가져옴
 * - 테이블 내용 업데이트
 * - 마지막 업데이트 시간 표시
 */
async function refreshNotices() {
    try {
        // 공지사항 데이터 가져오기
        const response = await fetch('/notices');
        const data = await response.json();
        
        // 테이블 내용 업데이트
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
        updateLastUpdateTime(data.last_update);
        
    } catch (error) {
        console.error('공지사항 업데이트 실패:', error);
        showErrorMessage();
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

// 페이지 로드 시 저장된 테마 적용
document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme') || 'default';
    changeTheme(savedTheme);
});



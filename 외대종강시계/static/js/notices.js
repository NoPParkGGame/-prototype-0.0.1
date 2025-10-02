async function refreshNotices() {
    try {
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
        document.querySelector('.last-update').textContent = data.last_update;
    } catch (error) {
        console.error('공지사항 업데이트 실패:', error);
    }
}
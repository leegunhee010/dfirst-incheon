/* consultation.js — 상담현황 슬라이드 (회전 애니메이션만 담당) */
/* 메시지 데이터(회사명 풀·생성 공식)는 서버(PHP, functions.php의 poedit_inquiry_messages)에서 생성 */
/* 여기서는 #sliding-content[data-messages]에 담긴 최종 4건을 4초마다 순환 표시만 한다 */
/* 내용(mp-text)·날짜(mp-date)는 각자 자기 셀(overflow:hidden) 안에서 세로로 굴러간다 →
   내용이 제목/날짜 줄 위로 침범해 보이지 않음(모바일 2줄 레이아웃 대응). */

(function () {
    document.addEventListener("DOMContentLoaded", function () {
        var slidingContent = document.getElementById("sliding-content");
        if (!slidingContent) return;

        var messages;
        try {
            messages = JSON.parse(slidingContent.getAttribute("data-messages") || "[]");
        } catch (e) {
            messages = [];
        }
        if (!messages.length) return;

        // 구조 1회 생성 (이후엔 텍스트 값만 갱신). 각 셀이 자기 줄만큼 잘라(overflow:hidden) 내부를 굴린다.
        slidingContent.innerHTML =
            '<div class="message-pair">' +
                '<div class="mp-cell mp-text"><div class="mp-inner"></div></div>' +
                '<div class="mp-cell mp-date"><div class="mp-inner"></div></div>' +
            '</div>';
        var textInner = slidingContent.querySelector(".mp-text .mp-inner");
        var dateInner = slidingContent.querySelector(".mp-date .mp-inner");
        if (!textInner || !dateInner) return;

        function setContent(msg) {
            textInner.textContent = msg.text;
            dateInner.textContent = msg.date;
        }

        var currentIndex = 0;
        setContent(messages[currentIndex]);
        if (messages.length < 2) return;
        currentIndex = 1;

        // 굴리는 거리 = 각 셀 높이 (데스크톱 30 / 모바일 20 등 CSS에 따름)
        function cellH(inner) {
            return (inner.parentElement && inner.parentElement.offsetHeight) || 30;
        }
        function setTransition(v) {
            textInner.style.transition = v;
            dateInner.style.transition = v;
        }
        function setY(ty, dy) {
            textInner.style.transform = "translateY(" + ty + "px)";
            dateInner.style.transform = "translateY(" + dy + "px)";
        }

        setInterval(function () {
            var msg = messages[currentIndex];
            var th = cellH(textInner), dh = cellH(dateInner);
            // 1) 현재 내용 위로 슬라이드 아웃
            setTransition("transform 0.5s ease");
            setY(-th, -dh);
            setTimeout(function () {
                // 2) 애니 끄고 아래로 순간이동 + 새 내용 렌더
                setTransition("none");
                setY(th, dh);
                setContent(msg);
                // 3) 다시 애니 켜고 제자리로 슬라이드 인
                setTimeout(function () {
                    setTransition("transform 0.5s ease");
                    setY(0, 0);
                }, 50);
            }, 500);
            currentIndex = (currentIndex + 1) % messages.length;
        }, 4000);
    });
})();

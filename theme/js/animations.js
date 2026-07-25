/* animations.js — 메인 페이지 애니메이션 모음 */

document.addEventListener('DOMContentLoaded', function () {

    /* ========== 통계 카운터 룰렛 ========== */
    function shuffleArray(arr) {
        var a = arr.slice();
        for (var i = a.length - 1; i > 0; i--) {
            var j = Math.floor(Math.random() * (i + 1));
            var tmp = a[i]; a[i] = a[j]; a[j] = tmp;
        }
        return a;
    }

    function buildRoulette(ul, targetDigit) {
        ul.innerHTML = '';
        var random1 = shuffleArray([0,1,2,3,4,5,6,7,8,9]);
        var random2 = shuffleArray([0,1,2,3,4,5,6,7,8,9]);
        var all = random1.concat(random2);
        all.forEach(function (num) {
            var li = document.createElement('li');
            li.className = 'count-num-item';
            li.textContent = num;
            ul.appendChild(li);
        });
        var index = all.lastIndexOf(parseInt(targetDigit));
        var itemH = ul.querySelector('.count-num-item') ? ul.querySelector('.count-num-item').offsetHeight : 52;
        var offset = index > 0 ? index * itemH : 10 * itemH;
        setTimeout(function () {
            ul.style.transform = 'translateY(-' + offset + 'px)';
        }, 50);
    }

    function startRouletteAnimation(container) {
        var wraps = container.querySelectorAll('.count-num-item-wrap');
        var digitCount = wraps.length;
        var number = container.dataset.number.padStart(digitCount, '0');
        var digits = number.split('');
        var boxes = container.querySelectorAll('.count-num-item-box');
        digits.forEach(function (digit, idx) {
            buildRoulette(boxes[idx], digit);
        });
    }

    var statsObserver = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            var el = entry.target;
            if (entry.isIntersecting) {
                startRouletteAnimation(el);
            } else {
                el.querySelectorAll('.count-num-item-box').forEach(function (box) {
                    box.innerHTML = '';
                    box.style.transform = 'translateY(0)';
                });
            }
        });
    }, { threshold: 0.6 });

    document.querySelectorAll('.stat-number').forEach(function (el) {
        statsObserver.observe(el);
    });

    /* ========== 뉴스 캐러셀 드래그 + 프로그레스 ========== */
    var scrollContainer = document.getElementById('scrollContainer');
    var newsProgressBar = document.getElementById('scrollProgressBar');

    if (scrollContainer) {
        /* 모바일: 2번째 카드를 초기 중앙에 배치 */
        if (window.innerWidth <= 767) {
            var secondCard = scrollContainer.querySelectorAll('.news-card')[1];
            if (secondCard) {
                var cardCenter = secondCard.offsetLeft - (scrollContainer.offsetWidth - secondCard.offsetWidth) / 2;
                scrollContainer.scrollLeft = cardCenter;
            }
        }
    }

    if (scrollContainer && newsProgressBar) {
        scrollContainer.addEventListener('scroll', function () {
            var scrollLeft = scrollContainer.scrollLeft;
            var maxScroll = scrollContainer.scrollWidth - scrollContainer.clientWidth;
            var percent = maxScroll > 0 ? (scrollLeft / maxScroll) * 100 : 0;
            newsProgressBar.style.width = percent + '%';
        });

        scrollContainer.addEventListener('wheel', function (e) {
            if (Math.abs(e.deltaX) > Math.abs(e.deltaY)) {
                e.preventDefault();
            }
        }, { passive: false });

        var isDown = false, startX, scrollLeft;
        scrollContainer.addEventListener('mousedown', function (e) {
            isDown = true;
            scrollContainer.classList.add('active');
            startX = e.pageX - scrollContainer.offsetLeft;
            scrollLeft = scrollContainer.scrollLeft;
            e.preventDefault();
        });
        window.addEventListener('mouseup', function () {
            isDown = false;
            scrollContainer.classList.remove('active');
        });
        window.addEventListener('mousemove', function (e) {
            if (!isDown) return;
            e.preventDefault();
            var x = e.pageX - scrollContainer.offsetLeft;
            scrollContainer.scrollLeft = scrollLeft - (x - startX) * 2;
        });
    }

    /* ========== 리뷰 카드 무한 스크롤 ========== */
    var reviewContainer = document.getElementById('reviewScrollInner');
    if (reviewContainer) {
        var reviewData = [
            { logo: "theme/assets/first/LOGO_Kookmin-bank.jpg", title: "디자인부터 인쇄까지 빠르게 받아볼 수 있었습니다", text: "시안을 2가지로 제안해주셔서 선택의 폭이 넓었고, 수정도 신속하게 진행되어 인쇄까지 빠르게 받아볼 수 있었습니다." },
            { logo: "theme/assets/first/LOGO_hite-jinro.jpg", title: "캐릭터 활용 홍보물, 기대 이상이었습니다", text: "브랜드 캐릭터를 활용한 홍보물을 의뢰했는데 톤앤매너를 정확히 살려주셔서 내부 반응이 아주 좋았습니다." },
            { logo: "theme/assets/first/LOGO_mirae.jpg", title: "너무 만족스럽고 수정이 필요없네요", text: "너무 만족스러운 디자인이고 수정 없이 마무리하면 될 것 같습니다 ^^ 대표님께서도 감사하다고 전해달라 하시네요." },
            { logo: "theme/assets/first/LOGO_ewha-university.png", title: "수정없이 한번에 컨펌되었습니다!", text: "컨셉이 정해진 것이 없었는데 원하는 디자인으로 잘 나왔습니다. 수정 없이 한번에 컨펌되어 편하게 작업했습니다~" },
            { logo: "theme/assets/first/LOGO_nationalforensic-logo.jpg", title: "보고서·브로슈어 모두 믿고 맡깁니다", text: "기관 발간물 특성상 검수 기준이 까다로운데도 일정과 품질 모두 정확하게 맞춰주셨습니다." },
            { logo: "theme/assets/first/LOGO_samsung-bio.jpg", title: "빠르고 신속한 작업! 다음에 또 요청드리겠습니다!", text: "리플렛 디자인 의뢰 후 마음에 들어서 포스터 디자인까지 의뢰하게 되었네요^^ 빠르고 친절하게 작업해주셔서 감사드립니다!" },
            { logo: "theme/assets/first/LOGO_cj-enm.png", title: "전체적으로 디자인이 좋아서 수정할 필요가 없습니다!", text: "전체적으로 디자인이 좋아서 개선할 것이 없습니다! 포스터와 랜딩페이지까지 시간 내에 빠르게 제작해주셔서 감사드립니다." },
            { logo: "theme/assets/first/LOGO_k-league.jpg", title: "좋은 작업물 만들어주셔서 감사드립니다!", text: "일정이 타이트했는데 기한에 맞춰 잘 작업해주셨습니다~ 두 가지 제작물의 톤앤매너까지 잘 맞춰주셔서 마음에 드네요." }
        ];

        function createReviewCard(data, index) {
            var card = document.createElement('div');
            card.className = 'review-card';
            if (index % 2 === 1) card.classList.add('right-column');
            card.innerHTML = '<div class="review-content"><img src="' + data.logo + '" class="review-logo" alt=""><h3>' + data.title + '</h3><p>' + data.text + '</p></div>';
            return card;
        }

        var isMobile = window.innerWidth <= 767;
        var loopCount = isMobile ? 2 : 3;

        for (var loop = 0; loop < loopCount; loop++) {
            reviewData.forEach(function (item, idx) {
                reviewContainer.appendChild(createReviewCard(item, loop * reviewData.length + idx));
            });
        }

        if (isMobile) {
            var scrollX = 0;
            var speed = 0.5;
            var scrollUnit = reviewContainer.scrollWidth / 2;

            function reviewHScrollLoop() {
                scrollX += speed;
                if (scrollX >= scrollUnit) scrollX = 0;
                reviewContainer.style.transform = 'translateX(' + (-scrollX) + 'px)';
                requestAnimationFrame(reviewHScrollLoop);
            }
            reviewHScrollLoop();
        } else {
            var scrollTop = 0;
            var scrollSpeed = 0.5;
            var scrollUnit = reviewContainer.scrollHeight / 3;

            function reviewScrollLoop() {
                scrollTop += scrollSpeed;
                if (scrollTop >= scrollUnit) scrollTop = 0;
                reviewContainer.style.transform = 'translateY(' + (-scrollTop) + 'px)';
                requestAnimationFrame(reviewScrollLoop);
            }
            reviewScrollLoop();
        }
    }

    /* ========== 차별점 사이드바 스크롤 ==========
       인디케이터(#feature-list .active) + 페이드 + 클릭 이동은
       front-page.php 인라인 스크립트에서 단독으로 처리한다.
       (두 곳에서 .active 를 건드리면 충돌해 깜빡이므로 여기서는 제거함) */

    /* FAQ 아코디언은 front-page.php 인라인 스크립트에서 단독 처리 (중복 핸들러 제거) */

});

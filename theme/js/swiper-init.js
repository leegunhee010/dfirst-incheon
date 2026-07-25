/* swiper-init.js — 히어로 슬라이더 초기화 */
/* 원본 poedit.co.kr 인라인 스크립트에서 추출 */

document.addEventListener('DOMContentLoaded', function () {
    const swiperEl = document.querySelector('.swiper-container');
    if (!swiperEl) return;

    const swiper = new Swiper('.swiper-container', {
        loop: true,
        autoplay: {
            delay: 3000,
            disableOnInteraction: false
        },
        speed: 700,
        allowTouchMove: false,
        simulateTouch: false
    });

    document.querySelector('.swiper-button-prev-custom').addEventListener('click', function () {
        swiper.slidePrev();
    });
    document.querySelector('.swiper-button-next-custom').addEventListener('click', function () {
        swiper.slideNext();
    });

    var progressBar = document.getElementById('progressBar');
    var slideCounter = document.querySelector('.swiper-counter');

    function updateUI() {
        var current = swiper.realIndex + 1;
        var total = document.querySelectorAll('.swiper-container .swiper-slide:not(.swiper-slide-duplicate)').length;
        slideCounter.querySelector('.current').textContent = current;
        slideCounter.querySelector('.total').textContent = ' / ' + total;
    }

    function animateBar() {
        progressBar.style.transition = 'none';
        progressBar.style.width = '0%';
        void progressBar.offsetWidth;
        progressBar.style.transition = 'width 3s linear';
        progressBar.style.width = '100%';
    }

    swiper.on('slideChangeTransitionStart', function () {
        updateUI();
        animateBar();
    });

    setTimeout(function () {
        updateUI();
        animateBar();
    }, 100);

    // ===== 모바일 히어로 캐러셀 (가운데 카드 강조형, 바닐라) =====
    var mobileCarousel = document.getElementById('mobileHeroCarousel');
    if (mobileCarousel) initLrCarousel(mobileCarousel, { autoplayMs: 3000 });
});

/* ============================================================================
   가운데 카드 강조형 캐러셀 — initLrCarousel(rootEl [, options])
   ----------------------------------------------------------------------------
   무한 루프(양끝 클론) · 스와이프/드래그 · 자동재생 · 점 인디케이터.
   options.autoplayMs : 자동재생 간격(ms). 기본 5000. 0이면 자동재생 안 함.
   ============================================================================ */
function initLrCarousel(root, options) {
  options = options || {};
  var AUTOPLAY_MS = options.autoplayMs != null ? options.autoplayMs : 5000;

  var viewport = root.querySelector('.lrc-viewport');
  var track    = root.querySelector('.lrc-track');
  var dotsEl   = root.querySelector('.lrc-dots');
  var heroBg   = root.querySelector('.lrc-hero-bg-img'); // 없을 수도 있음(옵션)
  if (!track) return;

  var origSlides = Array.prototype.slice.call(track.querySelectorAll('.lrc-slide'));
  var total = origSlides.length;
  if (total === 0) return;

  var cur = 1, startX = 0, baseOffset = 0, dragging = false, timer = null, running = false;

  // 무한 루프: 마지막을 앞에, 첫 번째를 뒤에 클론으로 붙임
  var lastClone = origSlides[total - 1].cloneNode(true);
  var firstClone = origSlides[0].cloneNode(true);
  lastClone.setAttribute('aria-hidden', 'true');
  firstClone.setAttribute('aria-hidden', 'true');
  track.insertBefore(lastClone, origSlides[0]);
  track.appendChild(firstClone);

  var allSlides = Array.prototype.slice.call(track.querySelectorAll('.lrc-slide'));
  var allTotal = allSlides.length; // total + 2

  // 점(dot) 생성
  dotsEl.innerHTML = '';
  origSlides.forEach(function (_, i) {
    var d = document.createElement('div');
    d.className = 'lrc-dot' + (i === 0 ? ' is-active' : '');
    d.addEventListener('click', function () { go(i + 1); reset(); });
    dotsEl.appendChild(d);
  });

  // i번째 슬라이드가 가운데 오도록 track을 얼마나 옮길지 계산
  function getOffset(i) {
    var slideW = allSlides[1].offsetWidth;
    return (viewport.offsetWidth - slideW) / 2 - i * slideW;
  }

  function updateDots(cloneIdx) {
    var realIdx = cloneIdx === 0 ? total - 1 : (cloneIdx === allTotal - 1 ? 0 : cloneIdx - 1);
    dotsEl.querySelectorAll('.lrc-dot').forEach(function (d, i) {
      d.classList.toggle('is-active', i === realIdx);
    });
    // 활성 카드의 data-bg 를 상단 흐린 배경에 반영 (배경 레이어가 있을 때만)
    if (heroBg) {
      var bg = origSlides[realIdx] && origSlides[realIdx].getAttribute('data-bg');
      heroBg.style.background = bg || 'none';
    }
  }

  function go(i, anim) {
    if (anim === undefined) anim = true;
    if (!viewport.offsetWidth) return;
    if (i >= allTotal) i = 1;      // 범위 보정(백그라운드 복귀 방어)
    else if (i < 0) i = total;
    cur = i;
    track.style.transition = anim ? 'transform .45s cubic-bezier(.25,.46,.45,.94)' : 'none';
    track.style.transform = 'translateX(' + getOffset(cur) + 'px)';
    allSlides.forEach(function (s, idx) { s.classList.toggle('is-active', idx === cur); });
    updateDots(cur);
  }

  // 클론 끝에 닿으면 애니메이션 없이 진짜 슬라이드로 순간이동 → 무한 루프
  track.addEventListener('transitionend', function () {
    if (cur === 0) go(total, false);
    else if (cur === allTotal - 1) go(1, false);
  });

  // 터치(모바일)
  track.addEventListener('touchstart', function (e) {
    dragging = true; startX = e.touches[0].clientX;
    baseOffset = getOffset(cur); track.style.transition = 'none'; clearInterval(timer);
  }, { passive: true });
  track.addEventListener('touchmove', function (e) {
    if (!dragging) return;
    track.style.transform = 'translateX(' + (baseOffset + e.touches[0].clientX - startX) + 'px)';
  }, { passive: true });
  track.addEventListener('touchend', function (e) {
    if (!dragging) return; dragging = false;
    var dx = e.changedTouches[0].clientX - startX;
    if (Math.abs(dx) > 50) go(dx < 0 ? cur + 1 : cur - 1); else go(cur);
    reset();
  });

  // 마우스 드래그(데스크탑)
  track.addEventListener('mousedown', function (e) {
    dragging = true; startX = e.clientX;
    baseOffset = getOffset(cur); track.style.transition = 'none'; clearInterval(timer); e.preventDefault();
  });
  track.addEventListener('mousemove', function (e) {
    if (!dragging) return;
    track.style.transform = 'translateX(' + (baseOffset + e.clientX - startX) + 'px)';
  });
  track.addEventListener('mouseup', function (e) {
    if (!dragging) return; dragging = false;
    var dx = e.clientX - startX;
    if (Math.abs(dx) > 50) go(dx < 0 ? cur + 1 : cur - 1); else go(cur);
    reset();
  });
  track.addEventListener('mouseleave', function () {
    if (dragging) { dragging = false; go(cur); reset(); }
  });

  // 자동재생
  function start() {
    clearInterval(timer); running = true;
    if (AUTOPLAY_MS > 0) timer = setInterval(function () { go(cur + 1); }, AUTOPLAY_MS);
  }
  function reset() { clearInterval(timer); start(); }
  function pause() { clearInterval(timer); running = false; }
  function resume() { requestAnimationFrame(function () { go(cur, false); start(); }); }

  // 탭이 백그라운드에서 돌아올 때 위치 재보정(빈 화면 방지)
  document.addEventListener('visibilitychange', function () {
    if (document.hidden) clearInterval(timer);
    else if (running) requestAnimationFrame(function () { go(cur, false); start(); });
  });

  // 창 크기 변경 시 오프셋 재계산
  window.addEventListener('resize', function () { go(cur, false); });

  // 외부에서 제어하고 싶을 때 사용: el._lrc.pause() / resume() / go(i)
  root._lrc = { pause: pause, resume: resume, go: go };

  requestAnimationFrame(function () { go(1, false); start(); });
}

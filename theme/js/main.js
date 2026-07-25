/* main.js — 공통 JS (플로팅 배너 + 애니메이션) */
/* 원본 poedit.co.kr inline script에서 복사 */
/* 상단 카운터(실시간 이용자 수·잔여 프로젝트)는 로직 노출 방지를 위해 서버(PHP, functions.php)로 이전 */

// ========== Fade-up 애니메이션 ==========
(function() {
    var sections = document.querySelectorAll('section');
    sections.forEach(function(section, index) {
        if (index === 0) return;
        if (section.classList.contains('cta-section')) return;
        section.classList.add('fade-up');
    });

    var childSelectors = [
        '.service-item', '.fsc-box',
        '.stat-item',
        '.portfolio-card',
        '.news-card',
        '.pf-card', '.rv-card', '.rv-text-card',
        '.col-card', '.nt-row',
        '.about-board-col',
        '.ct-form-row', '.ct-left', '.ct-right',
        '.difference-block', '.faq-item'
    ];
    var children = document.querySelectorAll(childSelectors.join(','));
    children.forEach(function(el) {
        el.classList.add('fade-up-child');
    });

    var observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });

    document.querySelectorAll('.fade-up, .fade-up-child').forEach(function(el) {
        observer.observe(el);
    });
})();

// ========== 모바일 메뉴 ==========
(function() {
    var menu = document.getElementById('mobileMenu');
    var backdrop = document.getElementById('mobileMenuBackdrop');
    var openBtn = document.getElementById('mobileMenuBtn');
    var closeBtn = document.getElementById('mobileMenuClose');
    if (!menu || !openBtn) return;

    function open() {
        menu.classList.add('open');
        if (backdrop) backdrop.classList.add('open');
        document.body.style.overflow = 'hidden';
    }
    function close() {
        menu.classList.remove('open');
        if (backdrop) backdrop.classList.remove('open');
        document.body.style.overflow = '';
    }

    openBtn.addEventListener('click', open);
    closeBtn.addEventListener('click', close);
    if (backdrop) backdrop.addEventListener('click', close);

    menu.querySelectorAll('.mobile-menu-nav a').forEach(function(link) {
        link.addEventListener('click', close);
    });

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && menu.classList.contains('open')) close();
    });
})();

// ========== 플로팅 배너 ==========
(function() {
    const banner = document.getElementById('floatingBanner');
    if (!banner) return;

    window.addEventListener('scroll', function() {
        const scrollTop = window.scrollY;
        const windowHeight = window.innerHeight;
        const bodyHeight = document.body.offsetHeight;
        const distanceToBottom = bodyHeight - (scrollTop + windowHeight);

        if (scrollTop < 100 || distanceToBottom < 100) {
            banner.classList.add('hidden');
        } else {
            banner.classList.remove('hidden');
        }
    });

    banner.addEventListener('click', function() {
        window.location.href = '/contact';
    });
})();

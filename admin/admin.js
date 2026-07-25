/* 퍼스트디자인 관리자 — 프론트 로직 */
(function () {
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return [].slice.call((r || document).querySelectorAll(s)); };
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function fmt(iso) { try { var d = new Date(iso); return d.getFullYear() + '.' + String(d.getMonth() + 1).padStart(2, '0') + '.' + String(d.getDate()).padStart(2, '0'); } catch (e) { return ''; } }
  var STLABEL = { new: '신규', inprogress: '진행중', done: '완료' };

  function api(path, opts) {
    opts = opts || {};
    opts.credentials = 'include';
    if (opts.body && !(opts.body instanceof FormData)) {
      opts.headers = Object.assign({ 'Content-Type': 'application/json' }, opts.headers || {});
      opts.body = JSON.stringify(opts.body);
    }
    return fetch((window.API_BASE || '') + path, opts).then(function (r) {
      if (r.status === 401) { showLogin(); throw new Error('unauth'); }
      return r.json().catch(function () { return {}; });
    });
  }
  var toastT;
  function toast(msg) { var t = $('#toast'); t.textContent = msg; t.classList.add('show'); clearTimeout(toastT); toastT = setTimeout(function () { t.classList.remove('show'); }, 2200); }

  // ---------- 인증 ----------
  function showLogin() { $('#login').classList.remove('hide'); $('#app').classList.add('hide'); }
  function showApp() { $('#login').classList.add('hide'); $('#app').classList.remove('hide'); switchTab('dash'); }
  function doLogin() {
    var u = $('#u').value, p = $('#p').value;
    $('#loginErr').textContent = '';
    api('/api/login', { method: 'POST', body: { username: u, password: p } })
      .then(function (r) { if (r.ok) showApp(); else $('#loginErr').textContent = r.error || '로그인 실패'; })
      .catch(function () { $('#loginErr').textContent = '아이디 또는 비밀번호가 올바르지 않습니다.'; });
  }
  $('#loginBtn').addEventListener('click', doLogin);
  $('#p').addEventListener('keydown', function (e) { if (e.key === 'Enter') doLogin(); });
  $('#logoutBtn').addEventListener('click', function () { api('/api/logout', { method: 'POST' }).then(showLogin); });

  // ---------- 탭 ----------
  function switchTab(tab) {
    $$('.side nav a').forEach(function (a) { a.classList.toggle('on', a.getAttribute('data-tab') === tab); });
    $$('[data-pane]').forEach(function (s) { s.classList.toggle('hide', s.getAttribute('data-pane') !== tab); });
    if (tab === 'dash') loadDash();
    if (tab === 'hero') loadHero();
    if (tab === 'inq') loadInq();
    if (tab === 'pf') loadPf();
    if (tab === 'col') { loadCol(); maybeShowDraftNote(); }
    if (tab === 'copy') loadCopy();
    if (tab === 'faq') loadFaqPages();
    if (tab === 'img') loadImagePages();
    if (tab === 'seo') { loadSeo(); loadSettings(); }
    if (tab === 'acct') loadAdmins();
  }
  $$('.side nav a').forEach(function (a) { a.addEventListener('click', function () { switchTab(a.getAttribute('data-tab')); }); });

  // ---------- 대시보드 ----------
  function loadDash() {
    api('/api/stats').then(function (s) {
      $('#statCards').innerHTML =
        scard(s.inquiries, '전체 문의') + scard(s.inquiriesNew, '신규 문의') + scard(s.portfolio, '포트폴리오') + scard(s.columns, '칼럼 글');
      updateBadge(s.inquiriesNew);
      var rows = (s.recent || []).map(function (q) {
        return '<tr><td>' + fmt(q.createdAt) + '</td><td><b>' + esc(q.company) + '</b><br><span class="msg">' + esc(q.name) + ' · ' + esc(q.field) + '</span></td><td>' + esc(q.phone) + '</td><td><span class="st ' + q.status + '">' + (STLABEL[q.status] || q.status) + '</span></td></tr>';
      }).join('');
      $('#recentWrap').innerHTML = rows ? '<table><thead><tr><th>접수일</th><th>업체/담당</th><th>연락처</th><th>상태</th></tr></thead><tbody>' + rows + '</tbody></table>' : '<p style="color:#6b6f66">문의가 없습니다.</p>';
    }).catch(function () {});
  }
  function scard(n, l) { return '<div class="scard"><div class="n">' + n + '</div><div class="l">' + l + '</div></div>'; }
  function updateBadge(n) { var b = $('#inqBadge'); if (n > 0) { b.textContent = n; b.classList.remove('hide'); } else b.classList.add('hide'); }

  // ---------- 히어로 배너 ----------
  var heroSlides = [];
  function loadHero() { api('/api/hero').then(function (list) { heroSlides = list || []; renderHero(); }).catch(function () {}); }
  function renderHero() {
    $('#heroList').innerHTML = heroSlides.map(function (s, i) {
      return '<div class="panel" data-idx="' + i + '">' +
        '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px"><h2 style="margin:0">슬라이드 ' + (i + 1) + '</h2>' +
        '<div style="display:flex;gap:6px"><button class="btn ghost sm" data-up="' + i + '" type="button">↑</button><button class="btn ghost sm" data-down="' + i + '" type="button">↓</button><button class="btn del sm" data-rm="' + i + '" type="button">삭제</button></div></div>' +
        '<div class="field"><label>배경 이미지</label><div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap"><div style="width:128px;height:70px;border-radius:8px;border:1px solid var(--line);background-color:var(--ink);background-size:cover;background-position:center;' + (s.image ? "background-image:url('/" + esc(s.image) + "')" : '') + '"></div><input type="file" accept="image/*" data-img="' + i + '"></div></div>' +
        '<div class="field"><label>상단 라벨 (영문 eyebrow)</label><input data-f="eyebrow" data-i="' + i + '" value="' + esc(s.eyebrow) + '"></div>' +
        '<div class="field"><label>제목 — <b>*단어*</b> = 초록 강조, 줄바꿈 = Enter</label><textarea data-f="title" data-i="' + i + '" rows="2">' + esc(s.title) + '</textarea></div>' +
        '<div class="field"><label>설명</label><textarea data-f="subtitle" data-i="' + i + '" rows="2">' + esc(s.subtitle) + '</textarea></div>' +
        '<div class="field"><label>글자색 (배경 밝기에 맞춰 선택)</label><select data-f="textColor" data-i="' + i + '"><option value="dark"' + ((s.textColor || 'dark') === 'dark' ? ' selected' : '') + '>다크 — 어두운 글자 (밝은 배경용)</option><option value="light"' + (s.textColor === 'light' ? ' selected' : '') + '>화이트 — 밝은 글자 (어두운 배경용)</option></select></div>' +
        '<div class="formrow" style="grid-template-columns:1fr 1fr"><div class="field"><label>버튼1 텍스트</label><input data-f="btn1Text" data-i="' + i + '" value="' + esc(s.btn1Text) + '"></div><div class="field"><label>버튼1 링크</label><input data-f="btn1Link" data-i="' + i + '" value="' + esc(s.btn1Link) + '"></div></div>' +
        '<div class="formrow" style="grid-template-columns:1fr 1fr"><div class="field"><label>버튼2 텍스트</label><input data-f="btn2Text" data-i="' + i + '" value="' + esc(s.btn2Text) + '"></div><div class="field"><label>버튼2 링크</label><input data-f="btn2Link" data-i="' + i + '" value="' + esc(s.btn2Link) + '"></div></div>' +
        '</div>';
    }).join('') || '<p style="color:#6b6f66">슬라이드가 없습니다. 아래에서 추가하세요.</p>';
    $$('#heroList [data-f]').forEach(function (el) { el.addEventListener('input', function () { heroSlides[+el.getAttribute('data-i')][el.getAttribute('data-f')] = el.value; }); });
    $$('#heroList [data-img]').forEach(function (el) { el.addEventListener('change', function () { var f = el.files[0]; if (!f) return; var idx = +el.getAttribute('data-img'); var fd = new FormData(); fd.append('file', f); api('/api/upload', { method: 'POST', body: fd }).then(function (r) { if (r.url) { heroSlides[idx].image = r.url; renderHero(); toast('이미지 업로드됨'); } }); }); });
    $$('#heroList [data-rm]').forEach(function (b) { b.addEventListener('click', function () { heroSlides.splice(+b.getAttribute('data-rm'), 1); renderHero(); }); });
    $$('#heroList [data-up]').forEach(function (b) { b.addEventListener('click', function () { var i = +b.getAttribute('data-up'); if (i > 0) { var t = heroSlides[i - 1]; heroSlides[i - 1] = heroSlides[i]; heroSlides[i] = t; renderHero(); } }); });
    $$('#heroList [data-down]').forEach(function (b) { b.addEventListener('click', function () { var i = +b.getAttribute('data-down'); if (i < heroSlides.length - 1) { var t = heroSlides[i + 1]; heroSlides[i + 1] = heroSlides[i]; heroSlides[i] = t; renderHero(); } }); });
  }
  if ($('#heroAdd')) $('#heroAdd').addEventListener('click', function () { heroSlides.push({ image: '', eyebrow: '', title: '새 슬라이드 *제목*', subtitle: '', btn1Text: '무료 견적 받기 →', btn1Link: 'index.html#contact', btn2Text: '포트폴리오 보기', btn2Link: 'portfolio.html' }); renderHero(); });
  if ($('#heroSave')) $('#heroSave').addEventListener('click', function () { api('/api/hero', { method: 'PUT', body: { slides: heroSlides } }).then(function () { toast('히어로 저장됨 (홈 반영)'); }); });

  // ---------- 문의 ----------
  function loadInq() {
    api('/api/inquiries').then(function (list) {
      updateBadge(list.filter(function (x) { return x.status === 'new'; }).length);
      if (!list.length) { $('#inqWrap').innerHTML = '<p style="color:#6b6f66">접수된 문의가 없습니다.</p>'; return; }
      var rows = list.map(function (q) {
        var opts = ['new', 'inprogress', 'done'].map(function (s) { return '<option value="' + s + '"' + (q.status === s ? ' selected' : '') + '>' + STLABEL[s] + '</option>'; }).join('');
        return '<tr>' +
          '<td>' + fmt(q.createdAt) + '</td>' +
          '<td><b>' + esc(q.company) + '</b><br><span class="msg">' + esc(q.name) + '</span></td>' +
          '<td>' + esc(q.phone) + '<br><span class="msg">' + esc(q.email) + '</span></td>' +
          '<td>' + esc(q.field) + '<div class="msg" title="' + esc(q.message) + '">' + esc(q.message) + '</div></td>' +
          '<td><select data-id="' + q.id + '" class="stSel">' + opts + '</select></td>' +
          '<td><button class="btn del sm" data-del="' + q.id + '">삭제</button></td>' +
          '</tr>';
      }).join('');
      $('#inqWrap').innerHTML = '<table><thead><tr><th>접수일</th><th>업체/담당</th><th>연락처</th><th>분야 / 내용</th><th>상태</th><th></th></tr></thead><tbody>' + rows + '</tbody></table>';
      $$('.stSel').forEach(function (sel) { sel.addEventListener('change', function () { api('/api/inquiries/' + sel.getAttribute('data-id'), { method: 'PATCH', body: { status: sel.value } }).then(function () { toast('상태 변경됨'); loadInq(); }); }); });
      $$('[data-del]').forEach(function (b) { b.addEventListener('click', function () { if (!confirm('이 문의를 삭제할까요?')) return; api('/api/inquiries/' + b.getAttribute('data-del'), { method: 'DELETE' }).then(function () { toast('삭제됨'); loadInq(); }); }); });
    }).catch(function () {});
  }

  // ---------- 포트폴리오 ----------
  function loadPf() {
    api('/api/portfolio').then(function (list) {
      $('#pfWrap').innerHTML = list.map(function (p) {
        return '<div class="pfc"><div class="th" style="background-image:url(\'' + (window.API_BASE||'') + '/' + esc(p.image) + '\')"></div><div class="b"><div class="c">' + esc(p.category) + '</div><div class="t">' + esc(p.title) + '</div><div class="row"><button class="btn del sm" data-del="' + p.id + '">삭제</button></div></div></div>';
      }).join('') || '<p style="color:#6b6f66">작업이 없습니다.</p>';
      $$('#pfWrap [data-del]').forEach(function (b) { b.addEventListener('click', function () { if (!confirm('이 작업을 삭제할까요?')) return; api('/api/portfolio/' + b.getAttribute('data-del'), { method: 'DELETE' }).then(function () { toast('삭제됨'); loadPf(); }); }); });
    }).catch(function () {});
  }
  $('#pfAdd').addEventListener('click', function () {
    var title = $('#pfTitle').value.trim(), cat = $('#pfCat').value, file = $('#pfImg').files[0];
    if (!title) { toast('제목을 입력하세요'); return; }
    if (!file) { toast('이미지를 선택하세요'); return; }
    var fd = new FormData(); fd.append('title', title); fd.append('category', cat); fd.append('image', file);
    api('/api/portfolio', { method: 'POST', body: fd }).then(function () { toast('추가됨'); $('#pfTitle').value = ''; $('#pfImg').value = ''; loadPf(); });
  });

  // ---------- 칼럼 ----------
  var editingCol = null, coverUrl = '', savedRange = null;
  var colEditor = $('#colEditor');
  function loadCol() {
    api('/api/columns').then(function (list) {
      var rows = list.map(function (c) {
        var th = c.thumbnail || c.image || '';
        var thumbCell = th ? '<div style="width:56px;height:42px;border-radius:6px;background:#eee url(\'' + (window.API_BASE||'') + '/' + esc(th) + '\') center/cover"></div>' : '<div style="width:56px;height:42px;border-radius:6px;background:var(--paper)"></div>';
        var draftBadge = c.status === 'draft' ? ' <span class="st inprogress" style="font-size:11px">임시저장</span>' : '';
        return '<tr><td>' + thumbCell + '</td><td><b>' + esc(c.title) + '</b>' + draftBadge + '<br><span class="msg">' + esc(c.excerpt) + '</span></td><td>' + esc(c.category) + '</td><td>' + fmt(c.createdAt) + '</td><td><button class="btn ghost sm" data-edit="' + c.id + '">수정</button> <button class="btn del sm" data-del="' + c.id + '">삭제</button></td></tr>';
      }).join('');
      $('#colWrap').innerHTML = list.length ? '<table><thead><tr><th></th><th>제목</th><th>카테고리</th><th>작성일</th><th></th></tr></thead><tbody>' + rows + '</tbody></table>' : '<p style="color:#6b6f66">글이 없습니다.</p>';
      window.__cols = list;
      $$('#colWrap [data-del]').forEach(function (b) { b.addEventListener('click', function () { if (!confirm('이 글을 삭제할까요?')) return; api('/api/columns/' + b.getAttribute('data-del'), { method: 'DELETE' }).then(function () { toast('삭제됨'); loadCol(); }); }); });
      $$('#colWrap [data-edit]').forEach(function (b) { b.addEventListener('click', function () { startEdit(b.getAttribute('data-edit')); }); });
    }).catch(function () {});
  }
  // 본문 에디터: 커서 위치 저장 + 삽입
  function saveRange() { var s = window.getSelection(); if (s && s.rangeCount && colEditor && colEditor.contains(s.anchorNode)) savedRange = s.getRangeAt(0).cloneRange(); }
  function restoreRange() { if (savedRange) { var s = window.getSelection(); s.removeAllRanges(); s.addRange(savedRange); } }
  if (colEditor) {
    ['keyup', 'mouseup', 'blur'].forEach(function (ev) { colEditor.addEventListener(ev, saveRange); });
    function insertNodeAtCursor(node) {
      colEditor.focus(); restoreRange();
      var sel = window.getSelection();
      if (!sel.rangeCount) { colEditor.appendChild(node); saveRange(); return; }
      var range = sel.getRangeAt(0); range.collapse(false); range.insertNode(node);
      range.setStartAfter(node); range.collapse(true); sel.removeAllRanges(); sel.addRange(range); saveRange();
    }
    $$('.rt-toolbar [data-cmd]').forEach(function (b) {
      b.addEventListener('mousedown', function (e) { e.preventDefault(); });
      b.addEventListener('click', function () {
        colEditor.focus(); restoreRange();
        var cmd = b.getAttribute('data-cmd'), val = b.getAttribute('data-val');
        document.execCommand(cmd, false, val ? '<' + val + '>' : null); saveRange();
      });
    });
    // 링크 삽입 / 수정 / 해제
    function normalizeUrl(u) { u = String(u).trim(); if (!u) return ''; if (/^(https?:|mailto:|tel:|\/|#)/i.test(u)) return u; return 'https://' + u; }
    function setLinkAttrs(a) { var href = a.getAttribute('href') || ''; if (/^https?:\/\//i.test(href)) { a.setAttribute('target', '_blank'); a.setAttribute('rel', 'noopener noreferrer'); } else { a.removeAttribute('target'); a.removeAttribute('rel'); } }
    function anchorAtSelection() { var s = window.getSelection(); var n = s && s.anchorNode; while (n && n !== colEditor) { if (n.nodeType === 1 && n.tagName === 'A') return n; n = n.parentNode; } return null; }
    if ($('#edLinkBtn')) {
      $('#edLinkBtn').addEventListener('mousedown', function (e) { e.preventDefault(); saveRange(); });
      $('#edLinkBtn').addEventListener('click', function () {
        colEditor.focus(); restoreRange();
        var sel = window.getSelection();
        var a = anchorAtSelection();
        if (a) {
          var next = prompt('링크 주소 (URL)\n비우고 확인하면 링크가 해제됩니다.', a.getAttribute('href') || '');
          if (next === null) return;
          next = next.trim();
          if (!next) { var rg = document.createRange(); rg.selectNode(a); sel.removeAllRanges(); sel.addRange(rg); document.execCommand('unlink'); toast('링크 해제됨'); }
          else { a.setAttribute('href', normalizeUrl(next)); setLinkAttrs(a); toast('링크 수정됨'); }
          saveRange(); scheduleAutosave(); return;
        }
        var url = prompt('링크 주소 (URL)\n선택한 글자에 링크가 걸립니다. 선택 안 했으면 주소가 그대로 삽입됩니다.\n예: https://www.example.com', 'https://');
        if (url === null) return;
        url = normalizeUrl(url);
        if (!url || url === 'https://') { toast('링크 주소를 입력하세요'); return; }
        if (sel && !sel.isCollapsed) { document.execCommand('createLink', false, url); }
        else { var link = document.createElement('a'); link.href = url; link.textContent = url; insertNodeAtCursor(link); }
        $$('a', colEditor).forEach(setLinkAttrs);
        toast('링크 삽입됨'); saveRange(); scheduleAutosave();
      });
    }
    $('#edImgBtn').addEventListener('mousedown', function (e) { e.preventDefault(); saveRange(); });
    $('#edImgBtn').addEventListener('click', function () { $('#edImgFile').click(); });
    $('#edImgFile').addEventListener('change', function () {
      var f = this.files[0]; this.value = ''; if (!f) return;
      var fd = new FormData(); fd.append('file', f);
      api('/api/upload', { method: 'POST', body: fd }).then(function (r) {
        if (!r.url) return;
        var img = document.createElement('img'); img.src = '/' + r.url;
        img.alt = (prompt('이미지 대체 텍스트 (ALT)\n검색엔진과 AI가 이미지의 내용과 의미를 이해하는 데 사용됩니다.\n예: 명함 4종 디자인 시안이 책상 위에 놓인 모습\n(건너뛰려면 비워두고 확인)', '') || '').trim();
        var p = document.createElement('p'); p.appendChild(img);
        insertNodeAtCursor(p);
        var sp = document.createElement('p'); sp.innerHTML = '<br>'; insertNodeAtCursor(sp);
        toast(img.alt ? '이미지 삽입됨 (ALT 입력됨)' : '이미지 삽입됨 — ALT 미입력 (이미지 클릭 후 ALT 버튼으로 추가 가능)');
        scheduleAutosave();
      });
    });
  }
  // 커버 업로드
  if ($('#coverUp')) {
    $('#coverUp').addEventListener('click', function () {
      var f = $('#coverFile').files[0]; if (!f) { toast('커버 이미지를 선택하세요'); return; }
      var fd = new FormData(); fd.append('file', f);
      api('/api/upload', { method: 'POST', body: fd }).then(function (r) { if (r.url) { coverUrl = r.url; $('#coverPrev').style.backgroundImage = "url('" + (window.API_BASE||'') + "/" +r.url + "')"; toast('커버 업로드됨'); } });
    });
    $('#coverClear').addEventListener('click', function () { coverUrl = ''; $('#coverPrev').style.backgroundImage = ''; });
  }
  // 본문 이미지 크기/정렬 조절
  var imgTool = $('#imgTool'), selImg = null;
  function placeImgTool(img) { var r = img.getBoundingClientRect(); imgTool.classList.remove('hide'); imgTool.style.top = (window.pageYOffset + r.top - 46) + 'px'; imgTool.style.left = (window.pageXOffset + r.left) + 'px'; }
  function updateAltBtn() { var b = $('#imgAltBtn'); if (!b || !selImg) return; var has = !!(selImg.getAttribute('alt') || '').trim(); b.textContent = has ? 'ALT ✓' : 'ALT'; b.classList.toggle('on', has); }
  function selectImg(img) { if (selImg) selImg.classList.remove('sel'); selImg = img; if (img) { img.classList.add('sel'); placeImgTool(img); updateAltBtn(); } else if (imgTool) imgTool.classList.add('hide'); }
  if (colEditor && imgTool) {
    colEditor.addEventListener('click', function (e) { if (e.target && e.target.tagName === 'IMG') selectImg(e.target); else selectImg(null); });
    imgTool.addEventListener('mousedown', function (e) { e.preventDefault(); });
    imgTool.addEventListener('click', function (e) {
      var b = e.target.closest('button'); if (!b || !selImg) return;
      if (b.dataset.w) { selImg.style.width = b.dataset.w + '%'; selImg.style.height = 'auto'; }
      else if (b.dataset.al) {
        var al = b.dataset.al, w = selImg.style.width;
        selImg.style.float = ''; selImg.style.display = ''; selImg.style.margin = '';
        if (al === 'center') { selImg.style.display = 'block'; selImg.style.margin = '14px auto'; }
        else if (al === 'left') { selImg.style.float = 'left'; selImg.style.margin = '6px 16px 6px 0'; }
        else if (al === 'right') { selImg.style.float = 'right'; selImg.style.margin = '6px 0 6px 16px'; }
        if (w) selImg.style.width = w;
      }
      else if (b.dataset.alt) {
        var cur = selImg.getAttribute('alt') || '';
        var next = prompt('이미지 대체 텍스트 (ALT)\n검색엔진과 AI가 이미지의 내용과 의미를 이해하는 데 사용됩니다.\n예: 명함 4종 디자인 시안이 책상 위에 놓인 모습', cur);
        if (next !== null) { selImg.alt = next.trim(); updateAltBtn(); toast(next.trim() ? 'ALT 텍스트 저장됨' : 'ALT 텍스트 지워짐'); scheduleAutosave(); }
      }
      else if (b.dataset.del) { selImg.remove(); selectImg(null); return; }
      placeImgTool(selImg);
    });
    window.addEventListener('scroll', function () { if (selImg && !imgTool.classList.contains('hide')) placeImgTool(selImg); }, true);
  }
  // 자동 백업 / 복구 (localStorage)
  var DRAFT_KEY = 'firstd_col_autosave', autosaveT;
  function doAutosave() {
    if (!colEditor) return;
    var title = $('#colTitle').value, bodyTxt = colEditor.innerHTML;
    if (!title && !bodyTxt.replace(/<[^>]*>/g, '').trim()) return;
    localStorage.setItem(DRAFT_KEY, JSON.stringify({ editingCol: editingCol, title: title, cat: $('#colCat').value, excerpt: $('#colExcerpt').value, body: bodyTxt, cover: coverUrl }));
  }
  function scheduleAutosave() { clearTimeout(autosaveT); autosaveT = setTimeout(doAutosave, 1000); }
  function clearAutosave() { localStorage.removeItem(DRAFT_KEY); var n = $('#colDraftNote'); if (n) n.classList.add('hide'); }
  ['#colTitle', '#colCat', '#colExcerpt'].forEach(function (s) { var el = $(s); if (el) el.addEventListener('input', scheduleAutosave); });
  if (colEditor) colEditor.addEventListener('input', scheduleAutosave);
  function maybeShowDraftNote() { var n = $('#colDraftNote'); if (!n) return; if (editingCol) { n.classList.add('hide'); return; } n.classList.toggle('hide', !localStorage.getItem(DRAFT_KEY)); }
  if ($('#draftRestore')) $('#draftRestore').addEventListener('click', function () {
    var raw = localStorage.getItem(DRAFT_KEY); if (!raw) return; var d = JSON.parse(raw);
    editingCol = d.editingCol || null;
    $('#colTitle').value = d.title || ''; $('#colCat').value = d.cat || 'Column'; $('#colExcerpt').value = d.excerpt || '';
    if (colEditor) colEditor.innerHTML = d.body || ''; coverUrl = d.cover || ''; $('#coverPrev').style.backgroundImage = coverUrl ? "url('" + (window.API_BASE||'') + "/" +coverUrl + "')" : '';
    $('#colDraftNote').classList.add('hide');
    if (editingCol) { $('#colFormTitle').textContent = '글 수정'; $('#colSave').textContent = '수정 저장'; $('#colCancel').classList.remove('hide'); }
    toast('이어서 작성합니다');
  });
  if ($('#draftDiscard')) $('#draftDiscard').addEventListener('click', clearAutosave);
  function startEdit(id) {
    var c = (window.__cols || []).find(function (x) { return x.id === id; }); if (!c) return;
    editingCol = id;
    $('#colTitle').value = c.title; $('#colCat').value = c.category; $('#colExcerpt').value = c.excerpt;
    var body = c.body || '';
    if (/<[a-z][\s\S]*>/i.test(body)) colEditor.innerHTML = body;
    else colEditor.innerHTML = body.split(/\n{2,}/).map(function (p) { return '<p>' + esc(p).replace(/\n/g, '<br>') + '</p>'; }).join('') || '<p></p>';
    coverUrl = c.thumbnail || c.image || ''; $('#coverPrev').style.backgroundImage = coverUrl ? "url('" + (window.API_BASE||'') + "/" +coverUrl + "')" : '';
    $('#colFormTitle').textContent = '글 수정'; $('#colSave').textContent = '수정 저장'; $('#colCancel').classList.remove('hide');
    window.scrollTo(0, 0);
  }
  function resetColForm() {
    editingCol = null; coverUrl = '';
    $('#colTitle').value = ''; $('#colExcerpt').value = ''; $('#colCat').value = 'Column';
    if (colEditor) colEditor.innerHTML = '';
    $('#coverPrev').style.backgroundImage = ''; if ($('#coverFile')) $('#coverFile').value = '';
    $('#colFormTitle').textContent = '새 글 작성'; $('#colSave').textContent = '발행'; $('#colCancel').classList.add('hide');
  }
  $('#colCancel').addEventListener('click', resetColForm);
  function saveCol(status) {
    var title = $('#colTitle').value.trim(); if (!title) { toast('제목을 입력하세요'); return; }
    if (colEditor) { selectImg(null); $$('img', colEditor).forEach(function (im) { im.classList.remove('sel'); if (!im.className) im.removeAttribute('class'); }); }
    var data = { title: title, category: $('#colCat').value.trim() || 'Column', excerpt: $('#colExcerpt').value.trim(), body: colEditor ? colEditor.innerHTML.trim() : '', thumbnail: coverUrl, status: status };
    var req = editingCol ? api('/api/columns/' + editingCol, { method: 'PATCH', body: data }) : api('/api/columns', { method: 'POST', body: data });
    req.then(function () { toast(status === 'draft' ? '임시저장됨' : (editingCol ? '수정됨' : '발행됨')); clearAutosave(); resetColForm(); loadCol(); });
  }
  $('#colSave').addEventListener('click', function () { saveCol('published'); });
  $('#colDraft').addEventListener('click', function () { saveCol('draft'); });

  // ---------- 카피(문구) 편집 ----------
  var PAGE_LABEL = { 'index.html': '홈', 'about.html': '회사소개', 'portfolio.html': '포트폴리오', 'column.html': '칼럼 (목록)', 'logo.html': '로고·브랜딩', 'catalog.html': '카탈로그·브로슈어', 'leaflet.html': '팜플렛·리플렛', 'poster.html': '포스터', 'photo.html': '제품촬영', 'marketing.html': '마케팅', 'voucher.html': '정부지원사업' };
  function loadCopy() {
    api('/api/content').then(function (list) {
      var rows = list.map(function (c) {
        var status = c.edited ? '<span class="st done">수정됨 · ' + c.count + '곳</span>' : '<span style="color:#9aa093;font-size:13px">기본 문구</span>';
        var resetBtn = c.edited ? ' <button class="btn del sm" data-reset="' + esc(c.page) + '">기본값 복원</button>' : '';
        return '<tr><td><b>' + esc(PAGE_LABEL[c.page] || c.page) + '</b><br><span class="msg">' + esc(c.page) + '</span></td>' +
          '<td>' + status + '</td>' +
          '<td><button class="btn sm" data-edit="' + esc(c.page) + '">편집하기 ↗</button>' + resetBtn + '</td></tr>';
      }).join('');
      $('#copyWrap').innerHTML = '<table><thead><tr><th>페이지</th><th>상태</th><th></th></tr></thead><tbody>' + rows + '</tbody></table>';
      $$('#copyWrap [data-edit]').forEach(function (b) {
        b.addEventListener('click', function () { window.open('/' + b.getAttribute('data-edit') + '?edit=1', '_blank'); });
      });
      $$('#copyWrap [data-reset]').forEach(function (b) {
        b.addEventListener('click', function () {
          var p = b.getAttribute('data-reset');
          if (!confirm((PAGE_LABEL[p] || p) + ' 페이지의 모든 문구를 원래 기본값으로 되돌릴까요?')) return;
          api('/api/content/' + encodeURIComponent(p), { method: 'DELETE' }).then(function () { toast('기본값으로 복원됨'); loadCopy(); });
        });
      });
    }).catch(function () {});
  }

  // ---------- FAQ 관리 ----------
  var faqPage = null, faqItems = [];
  function loadFaqPages() {
    $('#faqPanel').classList.add('hide');
    api('/api/faq').then(function (list) {
      var rows = (list || []).map(function (c) {
        var badge = c.count > 0 ? '<span class="st done">추가 ' + c.count + '개</span>' : '<span style="color:#9aa093;font-size:13px">추가 없음</span>';
        return '<tr><td><b>' + esc(c.label) + '</b><br><span class="msg">' + esc(c.page) + '</span></td>' +
          '<td>' + badge + '</td>' +
          '<td><button class="btn sm" data-faqpage="' + esc(c.page) + '">문항 편집 ↗</button></td></tr>';
      }).join('');
      $('#faqPages').innerHTML = '<table><thead><tr><th>페이지</th><th>추가 문항</th><th></th></tr></thead><tbody>' + rows + '</tbody></table>';
      $$('#faqPages [data-faqpage]').forEach(function (b) {
        b.addEventListener('click', function () { openFaqPage(b.getAttribute('data-faqpage'), b.closest('tr').querySelector('b').textContent); });
      });
    }).catch(function () {});
  }
  function renderFaqItems() {
    $('#faqList').innerHTML = faqItems.map(function (f, i) {
      return '<div class="panel" data-fi="' + i + '" style="padding:14px 16px;margin-bottom:10px">' +
        '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px"><b>문항 ' + (i + 1) + '</b>' +
        '<button class="btn del sm" data-frm="' + i + '" type="button">삭제</button></div>' +
        '<div class="field"><label>질문 (Q)</label><input data-fq="' + i + '" value="' + esc(f.q) + '" placeholder="예: 최소 제작 수량이 있나요?"></div>' +
        '<div class="field" style="margin-bottom:0"><label>답변 (A)</label><textarea data-fa="' + i + '" rows="3" placeholder="고객이 이해하기 쉽게 답변을 작성하세요.">' + esc(f.a) + '</textarea></div>' +
        '</div>';
    }).join('') || '<p style="color:#6b6f66">추가된 문항이 없습니다. 아래 <b>＋ 문항 추가</b>로 시작하세요.</p>';
    $$('#faqList [data-fq]').forEach(function (el) { el.addEventListener('input', function () { faqItems[+el.getAttribute('data-fq')].q = el.value; }); });
    $$('#faqList [data-fa]').forEach(function (el) { el.addEventListener('input', function () { faqItems[+el.getAttribute('data-fa')].a = el.value; }); });
    $$('#faqList [data-frm]').forEach(function (b) { b.addEventListener('click', function () { faqItems.splice(+b.getAttribute('data-frm'), 1); renderFaqItems(); }); });
  }
  function openFaqPage(page, label) {
    faqPage = page;
    $('#faqPageTitle').textContent = (label || page) + ' — 추가 FAQ';
    $('#faqPanel').classList.remove('hide');
    $('#faqList').innerHTML = '불러오는 중…';
    api('/api/faq/' + encodeURIComponent(page)).then(function (list) {
      faqItems = (list || []).map(function (f) { return { q: f.q || '', a: f.a || '' }; });
      renderFaqItems();
    }).catch(function () { $('#faqList').innerHTML = '<p style="color:#c0392b">불러오기 실패</p>'; });
  }
  if ($('#faqAdd')) $('#faqAdd').addEventListener('click', function () { faqItems.push({ q: '', a: '' }); renderFaqItems(); });
  if ($('#faqBack')) $('#faqBack').addEventListener('click', loadFaqPages);
  if ($('#faqSave')) $('#faqSave').addEventListener('click', function () {
    if (!faqPage) return;
    var clean = faqItems.filter(function (f) { return (f.q || '').trim() && (f.a || '').trim(); });
    api('/api/faq/' + encodeURIComponent(faqPage), { method: 'PUT', body: { items: clean } }).then(function (r) {
      if (r && r.ok) { toast('저장됨 · ' + r.count + '개 (사이트·검색 반영)'); } else { toast((r && r.error) || '저장 실패'); }
    }).catch(function () { toast('저장 실패'); });
  });

  // ---------- 이미지 교체 ----------
  var IMG_PAGES = ['index.html', 'about.html', 'logo.html', 'catalog.html', 'leaflet.html', 'poster.html', 'photo.html', 'marketing.html', 'voucher.html', 'printguide.html', 'portfolio.html'];
  var IMG_LABEL = { 'index.html': '홈', 'about.html': '회사소개', 'portfolio.html': '포트폴리오', 'logo.html': '로고·브랜딩', 'catalog.html': '카탈로그·브로슈어', 'leaflet.html': '팜플렛·리플렛', 'poster.html': '포스터', 'photo.html': '제품촬영', 'marketing.html': '마케팅', 'voucher.html': '정부지원사업', 'printguide.html': '인쇄가이드' };
  function loadImagePages() {
    $('#imgPanel').classList.add('hide');
    var rows = IMG_PAGES.map(function (p) {
      return '<tr><td><b>' + esc(IMG_LABEL[p] || p) + '</b><br><span class="msg">' + esc(p) + '</span></td>' +
        '<td><button class="btn sm" data-imgpage="' + esc(p) + '">사진 관리 ↗</button></td></tr>';
    }).join('');
    $('#imgPages').innerHTML = '<table><thead><tr><th>페이지</th><th></th></tr></thead><tbody>' + rows + '</tbody></table>';
    $$('#imgPages [data-imgpage]').forEach(function (b) {
      b.addEventListener('click', function () { openImagePage(b.getAttribute('data-imgpage')); });
    });
  }
  function openImagePage(page) {
    $('#imgPageTitle').textContent = (IMG_LABEL[page] || page) + ' — 사진';
    $('#imgPanel').classList.remove('hide');
    $('#imgGrid').innerHTML = '불러오는 중…';
    api('/api/images/' + encodeURIComponent(page)).then(function (list) {
      if (!list.length) { $('#imgGrid').innerHTML = '<p style="color:#6b6f66">이 페이지에는 교체 가능한 사진이 없습니다.</p>'; return; }
      $('#imgGrid').innerHTML = '<div class="img-mgr">' + list.map(function (it, i) {
        var badge = it.overridden ? '<span class="st done" style="font-size:11px">변경됨</span>' : '';
        var revert = it.overridden ? '<button class="btn del sm" data-revert="' + esc(it.original) + '">되돌리기</button>' : '';
        return '<div class="img-cell">' +
          '<div class="img-thumb" style="background-image:url(\'' + (window.API_BASE||'') + '/' + esc(it.src) + '?t=' + Date.now() + '\')"></div>' +
          '<div class="img-meta">' + esc(it.alt || ('사진 ' + (i + 1))) + ' ' + badge + '</div>' +
          '<div class="img-act"><label class="btn sm">이미지 변경<input type="file" accept="image/*" data-up="' + esc(it.original) + '" hidden></label>' + revert + '</div>' +
          '</div>';
      }).join('') + '</div>';
      $$('#imgGrid [data-up]').forEach(function (inp) {
        inp.addEventListener('change', function () {
          var f = inp.files[0]; if (!f) return;
          var src = inp.getAttribute('data-up');
          var fd = new FormData(); fd.append('image', f); fd.append('src', src);
          var cell = inp.closest('.img-cell'); if (cell) cell.style.opacity = '.5';
          api('/api/images/' + encodeURIComponent(page), { method: 'POST', body: fd }).then(function (r) {
            if (r && r.ok) { toast('이미지 교체됨'); openImagePage(page); } else { toast((r && r.error) || '업로드 실패'); if (cell) cell.style.opacity = '1'; }
          }).catch(function () { toast('업로드 실패'); if (cell) cell.style.opacity = '1'; });
        });
      });
      $$('#imgGrid [data-revert]').forEach(function (b) {
        b.addEventListener('click', function () {
          var src = b.getAttribute('data-revert');
          api('/api/images/' + encodeURIComponent(page) + '?src=' + encodeURIComponent(src), { method: 'DELETE' }).then(function () { toast('기본 이미지로 복원'); openImagePage(page); });
        });
      });
    }).catch(function () { $('#imgGrid').innerHTML = '<p style="color:#c0392b">불러오기 실패</p>'; });
  }
  var _imgBack = $('#imgBack'); if (_imgBack) _imgBack.addEventListener('click', loadImagePages);

  // ---------- SEO ----------
  function loadSeo() {
    api('/api/seo').then(function (list) {
      $('#seoWrap').innerHTML = list.map(function (s) {
        var ogSrc = s.ogImage ? ('/' + s.ogImage.replace(/^\/+/, '')) : '/assets/mainbanner0001.jpg';
        return '<div style="padding:18px 0;border-bottom:1px solid var(--line)">' +
          '<div style="font-weight:800;margin-bottom:10px">' + esc(s.page) + (s.overridden ? ' <span class="st done">수정됨</span>' : '') + '</div>' +
          '<div class="field"><label>검색 제목 (title)</label><input class="seoT" data-p="' + esc(s.page) + '" value="' + esc(s.title) + '"></div>' +
          '<div class="field"><label>검색 설명 (description)</label><textarea class="seoD" data-p="' + esc(s.page) + '" rows="2">' + esc(s.description) + '</textarea></div>' +
          '<div class="field"><label>키워드 (keywords)</label><textarea class="seoK" data-p="' + esc(s.page) + '" rows="2" placeholder="비우면 사이트 기본 키워드 사용">' + esc(s.keywords) + '</textarea></div>' +
          '<div class="field"><label>대표 공유 이미지 (og:image — 비우면 사이트 기본 이미지)</label>' +
            '<div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap">' +
            '<img class="seoOgPrev" data-p="' + esc(s.page) + '" src="' + esc(ogSrc) + '" style="width:104px;height:55px;object-fit:cover;border:1px solid var(--line);border-radius:6px;background:#fff">' +
            '<input type="file" class="seoOgFile" data-p="' + esc(s.page) + '" accept="image/png,image/jpeg,image/webp">' +
            '<button class="btn sm ghost" data-ogup="' + esc(s.page) + '">이미지 업로드</button>' +
            (s.ogImage ? '<button class="btn sm ghost" data-ogclear="' + esc(s.page) + '">기본으로</button>' : '') +
            '</div></div>' +
          '<button class="btn sm" data-save="' + esc(s.page) + '">저장</button>' +
          '</div>';
      }).join('');
      $$('#seoWrap [data-save]').forEach(function (b) {
        b.addEventListener('click', function () {
          var p = b.getAttribute('data-save');
          var t = $('.seoT[data-p="' + p + '"]').value, d = $('.seoD[data-p="' + p + '"]').value, k = $('.seoK[data-p="' + p + '"]').value;
          api('/api/seo/' + p, { method: 'PATCH', body: { title: t, description: d, keywords: k } }).then(function () { toast(p + ' SEO 저장됨'); loadSeo(); });
        });
      });
      $$('#seoWrap [data-ogup]').forEach(function (b) {
        b.addEventListener('click', function () {
          var p = b.getAttribute('data-ogup');
          var f = $('.seoOgFile[data-p="' + p + '"]').files[0];
          if (!f) { toast('이미지를 선택하세요'); return; }
          var fd = new FormData(); fd.append('image', f);
          api('/api/seo/' + p + '/ogimage', { method: 'POST', body: fd }).then(function (r) { if (r.ogImage) { toast(p + ' 대표이미지 업로드됨'); loadSeo(); } });
        });
      });
      $$('#seoWrap [data-ogclear]').forEach(function (b) {
        b.addEventListener('click', function () {
          var p = b.getAttribute('data-ogclear');
          api('/api/seo/' + p, { method: 'PATCH', body: { ogImage: '' } }).then(function () { toast(p + ' 대표이미지 기본값으로'); loadSeo(); });
        });
      });
    }).catch(function () {});
  }

  // ---------- 사이트 설정 (도메인/Head/파비콘) ----------
  function loadSettings() {
    api('/api/settings').then(function (s) {
      $('#setDomain').value = s.domain || '';
      $('#setHead').value = s.headCode || '';
      if ($('#setSiteName')) $('#setSiteName').value = s.siteName || '';
      if ($('#setKeywords')) $('#setKeywords').value = s.keywords || '';
      if ($('#ogPrev')) $('#ogPrev').src = (s.ogImage ? '/' + s.ogImage.replace(/^\/+/, '') : '/assets/mainbanner0001.jpg') + '?t=' + Date.now();
      if (s.favicon) $('#favPrev').src = '/' + s.favicon.replace(/^\/+/, '') + '?t=' + Date.now();
      if ($('#mailEnabled')) {
        $('#mailEnabled').checked = !!s.mailEnabled;
        $('#mailUser').value = s.mailUser || '';
        $('#mailTo').value = s.mailTo || '';
        $('#mailPass').value = '';
        $('#mailPass').placeholder = s.mailPassSet ? '설정됨 ●●●●●● — 변경할 때만 입력' : '앱 비밀번호 16자리';
      }
    }).catch(function () {});
  }
  $('#setSave').addEventListener('click', function () {
    var body = { domain: $('#setDomain').value.trim(), headCode: $('#setHead').value };
    if ($('#setSiteName')) body.siteName = $('#setSiteName').value.trim();
    if ($('#setKeywords')) body.keywords = $('#setKeywords').value.trim();
    api('/api/settings', { method: 'PATCH', body: body }).then(function () { toast('설정 저장됨 (사이트 반영)'); });
  });
  if ($('#ogUp')) $('#ogUp').addEventListener('click', function () {
    var f = $('#ogFile').files[0];
    if (!f) { toast('대표 이미지 파일을 선택하세요'); return; }
    var fd = new FormData(); fd.append('image', f);
    api('/api/settings/ogimage', { method: 'POST', body: fd }).then(function (r) { if (r.ogImage) { $('#ogPrev').src = '/' + r.ogImage + '?t=' + Date.now(); toast('대표 이미지 업로드됨'); } });
  });
  if ($('#mailSave')) $('#mailSave').addEventListener('click', function () {
    var body = { mailEnabled: $('#mailEnabled').checked, mailUser: $('#mailUser').value.trim(), mailTo: $('#mailTo').value.trim() };
    var pw = $('#mailPass').value.trim(); if (pw) body.mailPass = pw;
    api('/api/settings', { method: 'PATCH', body: body }).then(function () { toast('메일 설정 저장됨'); loadSettings(); });
  });
  if ($('#mailTest')) $('#mailTest').addEventListener('click', function () {
    var b = $('#mailTest'); b.disabled = true; b.textContent = '보내는 중…';
    api('/api/settings/test-mail', { method: 'POST', body: {} }).then(function (r) {
      if (r && r.ok) toast('테스트 메일 발송됨 — 받는 메일함을 확인하세요'); else toast((r && r.error) || '발송 실패');
    }).catch(function () { toast('발송 실패'); }).then(function () { b.disabled = false; b.textContent = '테스트 메일 보내기'; });
  });
  $('#favUp').addEventListener('click', function () {
    var f = $('#favFile').files[0];
    if (!f) { toast('파비콘 파일을 선택하세요'); return; }
    var fd = new FormData(); fd.append('favicon', f);
    api('/api/settings/favicon', { method: 'POST', body: fd }).then(function (r) { if (r.favicon) { $('#favPrev').src = '/' + r.favicon + '?t=' + Date.now(); toast('파비콘 업로드됨'); } });
  });

  // ---------- 관리자 계정 ----------
  function loadAdmins() {
    api('/api/admins').then(function (list) {
      var rows = list.map(function (a) {
        return '<tr><td><b>' + esc(a.username) + '</b>' + (a.me ? ' <span class="st done" style="font-size:11px">나</span>' : '') + '</td><td>' + fmt(a.createdAt) + '</td><td>' + (a.me ? '<span style="color:#9aa093;font-size:12px">본인</span>' : '<button class="btn del sm" data-rmadmin="' + esc(a.username) + '">삭제</button>') + '</td></tr>';
      }).join('');
      $('#adminList').innerHTML = '<table><thead><tr><th>아이디</th><th>등록일</th><th></th></tr></thead><tbody>' + rows + '</tbody></table>';
      $$('#adminList [data-rmadmin]').forEach(function (b) { b.addEventListener('click', function () { var u = b.getAttribute('data-rmadmin'); if (!confirm('관리자 "' + u + '"를 삭제할까요?')) return; api('/api/admins/' + encodeURIComponent(u), { method: 'DELETE' }).then(function (r) { if (r.ok) { toast('삭제됨'); loadAdmins(); } else toast(r.error || '삭제 실패'); }); }); });
    }).catch(function () {});
  }
  if ($('#adminAdd')) $('#adminAdd').addEventListener('click', function () {
    var u = $('#newAdminU').value.trim(), p = $('#newAdminP').value;
    if (!u || !p) { toast('아이디·비밀번호를 입력하세요'); return; }
    api('/api/admins', { method: 'POST', body: { username: u, password: p } }).then(function (r) { if (r.ok) { toast('관리자 추가됨'); $('#newAdminU').value = ''; $('#newAdminP').value = ''; loadAdmins(); } else toast(r.error || '추가 실패'); });
  });
  if ($('#pwChange')) $('#pwChange').addEventListener('click', function () {
    var cur = $('#pwCur').value, nw = $('#pwNew').value;
    if (!cur || !nw) { toast('비밀번호를 입력하세요'); return; }
    api('/api/account/password', { method: 'POST', body: { current: cur, next: nw } }).then(function (r) { if (r.ok) { toast('비밀번호 변경됨'); $('#pwCur').value = ''; $('#pwNew').value = ''; } else toast(r.error || '변경 실패'); });
  });

  // ---------- 시작 ----------
  api('/api/me').then(function (r) { if (r.authed) showApp(); else showLogin(); }).catch(showLogin);
})();

<?php
namespace App\Controllers;

use CodeIgniter\Controller;
use CodeIgniter\HTTP\ResponseInterface;

/**
 * 퍼스트디자인 인천지사 관리자 API (CI4 + MySQL).
 * Flask 관리자(admin/server.py)를 그대로 이관 — admin.js·admin.css·index.html 무수정 재사용.
 * 정적 사이트 HTML은 public/ 에 두고, 편집 저장 시 Bake 라이브러리가 그 HTML을 직접 갱신.
 */
class Api extends Controller
{
    protected $db;
    protected $sess;
    protected $bake;
    protected $uiDir;   // 관리자 UI 파일 위치

    public function __construct()
    {
        $this->db   = \Config\Database::connect();
        $this->sess = session();
        $this->bake = new \App\Libraries\Bake();
        $this->uiDir = FCPATH . 'admin/';   // public/admin/index.html, admin.js, admin.css
    }

    // ---------- 헬퍼 ----------
    private function json($data, int $code = 200): ResponseInterface
    {
        return $this->response->setStatusCode($code)
            ->setContentType('application/json')
            ->setBody(json_encode($data, JSON_UNESCAPED_UNICODE));
    }
    private function body(): array
    {
        $j = json_decode($this->request->getBody() ?? '', true);
        return is_array($j) ? $j : [];
    }
    private function authed(): bool { return (bool) $this->sess->get('uid'); }
    private function guard(): ?ResponseInterface
    {
        return $this->authed() ? null : $this->json(['error' => 'unauthorized'], 401);
    }
    private function sha(string $s): string { return hash('sha256', $s); }

    // ====================================================================
    // 인증
    // ====================================================================
    public function login()
    {
        $d = $this->body();
        $u = $d['username'] ?? '';
        $h = $this->sha($d['password'] ?? '');
        $row = $this->db->table('admins')->where('username', $u)->where('password_hash', $h)->get()->getRowArray();
        if ($row) {
            $this->sess->set('uid', $u);
            return $this->json(['ok' => true, 'user' => $u]);
        }
        return $this->json(['error' => '아이디 또는 비밀번호가 올바르지 않습니다.'], 401);
    }
    public function logout() { $this->sess->destroy(); return $this->json(['ok' => true]); }
    public function me()     { return $this->json(['authed' => $this->authed(), 'user' => $this->sess->get('uid')]); }

    public function password()
    {
        if ($f = $this->guard()) return $f;
        $d = $this->body();
        $u = $this->sess->get('uid');
        $row = $this->db->table('admins')->where('username', $u)->get()->getRowArray();
        if (!$row || $row['password_hash'] !== $this->sha($d['current'] ?? '')) {
            return $this->json(['error' => '현재 비밀번호가 틀립니다'], 400);
        }
        if (strlen($d['next'] ?? '') < 4) return $this->json(['error' => '새 비밀번호는 4자 이상'], 400);
        $this->db->table('admins')->where('username', $u)->update(['password_hash' => $this->sha($d['next'])]);
        return $this->json(['ok' => true]);
    }

    // ====================================================================
    // 대시보드
    // ====================================================================
    public function stats()
    {
        if ($f = $this->guard()) return $f;
        $inqAll = $this->db->table('inquiries')->countAllResults();
        $inqNew = $this->db->table('inquiries')->where('status', 'new')->countAllResults();
        $recent = $this->db->table('inquiries')->orderBy('created_at', 'DESC')->limit(6)->get()->getResultArray();
        $rows = array_map(fn($q) => [
            'createdAt' => $q['created_at'], 'company' => $q['company'], 'name' => $q['name'],
            'field' => $q['field'], 'phone' => $q['phone'] ?: $q['email'], 'status' => $q['status'],
        ], $recent);
        return $this->json([
            'inquiries' => $inqAll, 'inquiriesNew' => $inqNew,
            'portfolio' => $this->db->table('portfolio')->countAllResults(),
            'columns'   => $this->db->table('columns')->countAllResults(),
            'recent'    => $rows,
        ]);
    }

    // ====================================================================
    // 포트폴리오
    // ====================================================================
    public function pfList()
    {
        if ($f = $this->guard()) return $f;
        $rows = $this->db->table('portfolio')->orderBy('sort_order', 'ASC')->get()->getResultArray();
        return $this->json(array_map(fn($r) => [
            'id' => (int)$r['id'], 'image' => $r['image'], 'title' => $r['title'],
            'type' => $r['type'], 'category' => $r['category'], 'order' => (int)$r['sort_order'],
        ], $rows));
    }

    public function pfSave()
    {
        if ($f = $this->guard()) return $f;
        $file = $this->request->getFile('image');
        if ($file && $file->isValid()) {                  // dfirst UI: 파일 업로드 + 생성
            $newsrc = $this->storeUpload($file, 'pf');
            $title = trim($this->request->getPost('title') ?? '');
            $cat   = $this->request->getPost('category') ?? '책자';
            $type  = '';
            if (strpos($title, ' · ') !== false) { [$title, $type] = explode(' · ', $title, 2); }
            // 맨 앞에 삽입 → 나머지 순번 +1
            $this->db->table('portfolio')->set('sort_order', 'sort_order+1', false)->update();
            $this->db->table('portfolio')->insert([
                'image' => $newsrc, 'title' => trim($title), 'type' => trim($type),
                'category' => $cat, 'sort_order' => 0,
            ]);
        } else {                                          // JSON 전체 저장
            $items = $this->body()['items'] ?? [];
            $this->db->table('portfolio')->truncate();
            foreach ($items as $i => $it) {
                $this->db->table('portfolio')->insert([
                    'image' => $it['image'] ?? '', 'title' => $it['title'] ?? '',
                    'type' => $it['type'] ?? '', 'category' => $it['category'] ?? '책자', 'sort_order' => $i,
                ]);
            }
        }
        $n = $this->bake->portfolio($this->pfRows());
        return $this->json(['ok' => true, 'count' => $n]);
    }

    public function pfDelete($id)
    {
        if ($f = $this->guard()) return $f;
        $this->db->table('portfolio')->delete(['id' => (int)$id]);
        $this->bake->portfolio($this->pfRows());
        return $this->json(['ok' => true]);
    }
    private function pfRows(): array
    {
        return $this->db->table('portfolio')->orderBy('sort_order', 'ASC')->get()->getResultArray();
    }

    // ====================================================================
    // 히어로
    // ====================================================================
    public function heroGet()
    {
        if ($f = $this->guard()) return $f;
        $rows = $this->db->table('hero')->orderBy('sort_order', 'ASC')->get()->getResultArray();
        return $this->json(array_map(fn($r) => [
            'title' => $r['title'], 'eyebrow' => $r['eyebrow'], 'subtitle' => $r['subtitle'],
            'image' => $r['image'], 'btn1Link' => $r['btn1_link'], 'textColor' => $r['text_color'],
        ], $rows));
    }
    public function heroSave()
    {
        if ($f = $this->guard()) return $f;
        $slides = $this->body()['slides'] ?? [];
        $this->db->table('hero')->truncate();
        foreach ($slides as $i => $s) {
            $this->db->table('hero')->insert([
                'sort_order' => $i, 'title' => $s['title'] ?? '', 'eyebrow' => $s['eyebrow'] ?? '',
                'subtitle' => $s['subtitle'] ?? '', 'image' => $s['image'] ?? '',
                'btn1_link' => $s['btn1Link'] ?? 'portfolio.html', 'text_color' => $s['textColor'] ?? 'light',
            ]);
        }
        $this->bake->hero($this->db->table('hero')->orderBy('sort_order')->get()->getResultArray());
        return $this->json(['ok' => true, 'count' => count($slides)]);
    }

    // ====================================================================
    // FAQ
    // ====================================================================
    public function faqPages()
    {
        if ($f = $this->guard()) return $f;
        $out = [];
        foreach ($this->bake->faqPages() as $pg => $label) {
            $cnt = $this->db->table('faq')->where('page', $pg)->countAllResults();
            $out[] = ['page' => $pg, 'label' => $label, 'count' => $cnt];
        }
        return $this->json($out);
    }
    public function faqGet($page)
    {
        if ($f = $this->guard()) return $f;
        $rows = $this->db->table('faq')->where('page', $page)->orderBy('sort_order')->get()->getResultArray();
        if ($rows) return $this->json(array_map(fn($r) => ['q' => $r['q'], 'a' => $r['a']], $rows));
        // 저장 이력 없으면 페이지의 기본 FAQ를 불러와 보여줌
        return $this->json($this->bake->extractDefaultFaq($page));
    }
    public function faqSave($page)
    {
        if ($f = $this->guard()) return $f;
        if (!array_key_exists($page, $this->bake->faqPages())) return $this->json(['error' => '알 수 없는 페이지'], 400);
        $items = [];
        foreach (($this->body()['items'] ?? []) as $x) {
            $q = trim($x['q'] ?? ''); $a = trim($x['a'] ?? '');
            if ($q && $a) $items[] = ['q' => $q, 'a' => $a];
        }
        $this->db->table('faq')->delete(['page' => $page]);
        foreach ($items as $i => $it) {
            $this->db->table('faq')->insert(['page' => $page, 'q' => $it['q'], 'a' => $it['a'], 'sort_order' => $i]);
        }
        [$n, $total] = $this->bake->faq($page, $items);
        return $this->json(['ok' => true, 'count' => $n, 'total' => $total]);
    }

    // ====================================================================
    // 칼럼(블로그)
    // ====================================================================
    public function colList()
    {
        if ($f = $this->guard()) return $f;
        $rows = $this->db->table('columns')->orderBy('date', 'DESC')->get()->getResultArray();
        return $this->json(array_map(fn($r) => [
            'id' => (int)$r['id'], 'title' => $r['title'], 'category' => $r['category'],
            'excerpt' => $r['excerpt'], 'body' => $r['body'], 'thumbnail' => $r['thumbnail'],
            'status' => $r['status'], 'date' => $r['date'],
        ], $rows));
    }
    public function colAdd()
    {
        if ($f = $this->guard()) return $f;
        $d = $this->body();
        $this->db->table('columns')->insert([
            'title' => $d['title'] ?? '', 'category' => $d['category'] ?? 'Column',
            'excerpt' => $d['excerpt'] ?? '', 'body' => $d['body'] ?? '',
            'thumbnail' => $d['thumbnail'] ?? '', 'status' => $d['status'] ?? 'published',
            'date' => date('Y-m-d'),
        ]);
        $this->bake->columns($this->colRows());
        return $this->json(['ok' => true, 'id' => $this->db->insertID()]);
    }
    public function colEdit($id)
    {
        if ($f = $this->guard()) return $f;
        $d = $this->body(); $set = [];
        foreach (['title','category','excerpt','body','thumbnail','status'] as $k) if (isset($d[$k])) $set[$k] = $d[$k];
        if ($set) $this->db->table('columns')->where('id', (int)$id)->update($set);
        $this->bake->columns($this->colRows());
        return $this->json(['ok' => true]);
    }
    public function colDelete($id)
    {
        if ($f = $this->guard()) return $f;
        $this->db->table('columns')->delete(['id' => (int)$id]);
        @unlink(FCPATH . "col-{$id}.html");
        $this->bake->columns($this->colRows());
        return $this->json(['ok' => true]);
    }
    private function colRows(): array
    {
        return $this->db->table('columns')->where('status !=', 'draft')->orderBy('date', 'DESC')->get()->getResultArray();
    }

    // ====================================================================
    // 카피(문구)
    // ====================================================================
    public function contentList()
    {
        if ($f = $this->guard()) return $f;
        $out = [];
        foreach ($this->bake->copyPages() as $pg => $label) {
            $cnt = $this->db->table('content_overrides')->where('page', $pg)->countAllResults();
            $out[] = ['page' => $pg . '.html', 'label' => $label, 'edited' => $cnt > 0, 'count' => $cnt];
        }
        return $this->json($out);
    }
    public function contentSave($page)
    {
        if ($f = $this->guard()) return $f;
        $key = preg_replace('/\.html$/', '', $page);
        $applied = $this->bake->contentApply($key, $this->body()['edits'] ?? [], $this->db);
        return $this->json(['ok' => true, 'count' => $applied]);
    }
    public function contentReset($page)
    {
        if ($f = $this->guard()) return $f;
        $key = preg_replace('/\.html$/', '', $page);
        $this->bake->contentReset($key, $this->db);
        return $this->json(['ok' => true]);
    }

    // ====================================================================
    // SEO
    // ====================================================================
    public function seoList()
    {
        if ($f = $this->guard()) return $f;
        $out = [];
        foreach ($this->bake->seoPages() as $pg => $label) {
            $cur = $this->bake->readMeta($pg);
            if ($cur === null) continue;
            $ov = $this->db->table('seo_overrides')->where('page', $pg)->get()->getRowArray();
            $out[] = [
                'page' => $pg, 'label' => $label,
                'title' => $ov['title'] ?? $cur['title'],
                'description' => $ov['description'] ?? $cur['description'],
                'keywords' => $ov['keywords'] ?? $cur['keywords'],
                'overridden' => (bool)$ov,
            ];
        }
        return $this->json($out);
    }
    public function seoSave($page)
    {
        if ($f = $this->guard()) return $f;
        if (!array_key_exists($page, $this->bake->seoPages())) return $this->json(['error' => '알 수 없는 페이지'], 400);
        $d = $this->body();
        $meta = ['title' => $d['title'] ?? '', 'description' => $d['description'] ?? '', 'keywords' => $d['keywords'] ?? ''];
        $this->db->table('seo_overrides')->replace(array_merge(['page' => $page], $meta));
        $this->bake->seo($page, $meta);
        return $this->json(['ok' => true]);
    }

    // ====================================================================
    // 설정
    // ====================================================================
    private function settingsAll(): array
    {
        $rows = $this->db->table('settings')->get()->getResultArray();
        $o = [];
        foreach ($rows as $r) $o[$r['k']] = $r['v'];
        return $o;
    }
    private function settingsSet(string $k, string $v): void
    {
        $this->db->table('settings')->replace(['k' => $k, 'v' => $v]);
    }
    public function settingsGet()
    {
        if ($f = $this->guard()) return $f;
        $st = $this->settingsAll();
        $st['mailPassSet'] = !empty($st['mailPass']);
        unset($st['mailPass']);
        if (empty($st['domain'])) $st['domain'] = 'https://incheondesign.co.kr';
        return $this->json($st);
    }
    public function settingsSave()
    {
        if ($f = $this->guard()) return $f;
        $d = $this->body();
        foreach (['domain','headCode','siteName','keywords','mailEnabled','mailUser','mailTo'] as $k) {
            if (array_key_exists($k, $d)) $this->settingsSet($k, is_bool($d[$k]) ? ($d[$k]?'1':'') : (string)$d[$k]);
        }
        if (!empty($d['mailPass'])) $this->settingsSet('mailPass', $d['mailPass']);
        $this->bake->settings($this->settingsAll());
        return $this->json(['ok' => true]);
    }
    public function settingsFavicon()
    {
        if ($f = $this->guard()) return $f;
        $file = $this->request->getFile('favicon');
        if (!$file || !$file->isValid()) return $this->json(['error' => 'no file'], 400);
        $ext = strtolower($file->getExtension() ?: 'png');
        $file->move(FCPATH . 'theme/assets/first', 'favicon.' . $ext, true);
        $rel = 'theme/assets/first/favicon.' . $ext;
        $this->settingsSet('favicon', $rel);
        $this->bake->settings($this->settingsAll());
        return $this->json(['ok' => true, 'favicon' => $rel]);
    }
    public function settingsOgimage()
    {
        if ($f = $this->guard()) return $f;
        $file = $this->request->getFile('image');
        if (!$file || !$file->isValid()) return $this->json(['error' => 'no file'], 400);
        $rel = $this->storeUpload($file, 'og');
        $this->settingsSet('ogImage', $rel);
        $this->bake->settings($this->settingsAll());
        return $this->json(['ok' => true, 'ogImage' => $rel]);
    }
    public function settingsTestMail()
    {
        if ($f = $this->guard()) return $f;
        return $this->json(['ok' => false, 'error' => '메일 발송은 서버 SMTP 설정 후 사용 가능합니다.']);
    }

    // ====================================================================
    // 이미지
    // ====================================================================
    private function storeUpload($file, string $prefix): string
    {
        $ext = strtolower($file->getExtension() ?: 'jpg');
        if (!in_array($ext, ['jpg','jpeg','png','webp','gif'])) $ext = 'jpg';
        $name = $prefix . '_' . substr(md5($file->getName() . microtime()), 0, 14) . '.' . $ext;
        $dir = FCPATH . 'theme/assets/first/pf2';
        if (!is_dir($dir)) mkdir($dir, 0775, true);
        $file->move($dir, $name, true);
        $this->bake->resize($dir . '/' . $name, 1400);
        return 'theme/assets/first/pf2/' . $name;
    }
    public function upload()
    {
        if ($f = $this->guard()) return $f;
        $file = $this->request->getFile('file');
        if (!$file || !$file->isValid()) return $this->json(['error' => 'no file'], 400);
        $rel = $this->storeUpload($file, 'up');
        return $this->json(['ok' => true, 'path' => $rel, 'url' => $rel]);
    }
    public function imageLibrary()
    {
        if ($f = $this->guard()) return $f;
        $dir = FCPATH . 'theme/assets/first/pf2';
        $out = [];
        foreach (glob($dir . '/*') ?: [] as $p) {
            if (preg_match('/\.(jpg|jpeg|png|webp|gif)$/i', $p)) {
                $out[] = ['path' => 'theme/assets/first/pf2/' . basename($p), 'name' => basename($p), 'size' => filesize($p)];
            }
        }
        usort($out, fn($a, $b) => $b['size'] <=> $a['size']);
        return $this->json(array_slice($out, 0, 400));
    }
    public function imagesPage($page)      { if ($f = $this->guard()) return $f; return $this->json($this->bake->imagesList($page, $this->db)); }
    public function imagesReplace($page)
    {
        if ($f = $this->guard()) return $f;
        $file = $this->request->getFile('image');
        $original = $this->request->getPost('src') ?? '';
        if (!$file || !$file->isValid() || !$original) return $this->json(['error' => '잘못된 요청'], 400);
        $newsrc = $this->storeUpload($file, 'rp');
        $this->bake->imageReplace($page, $original, $newsrc, $this->db);
        return $this->json(['ok' => true, 'src' => $newsrc]);
    }
    public function imagesRevert($page)
    {
        if ($f = $this->guard()) return $f;
        $this->bake->imageRevert($page, $this->request->getGet('src') ?? '', $this->db);
        return $this->json(['ok' => true]);
    }

    // ====================================================================
    // 계정
    // ====================================================================
    public function adminsList()
    {
        if ($f = $this->guard()) return $f;
        $rows = $this->db->table('admins')->get()->getResultArray();
        $me = $this->sess->get('uid');
        return $this->json(array_map(fn($r) => [
            'username' => $r['username'], 'createdAt' => $r['created_at'], 'me' => $r['username'] === $me,
        ], $rows));
    }
    public function adminsAdd()
    {
        if ($f = $this->guard()) return $f;
        $d = $this->body();
        $u = trim($d['username'] ?? ''); $pw = $d['password'] ?? '';
        if (!$u || strlen($pw) < 4) return $this->json(['error' => '아이디·비밀번호(4자+)를 확인하세요'], 400);
        if ($this->db->table('admins')->where('username', $u)->countAllResults()) return $this->json(['error' => '이미 있는 아이디'], 400);
        $this->db->table('admins')->insert(['username' => $u, 'password_hash' => $this->sha($pw), 'created_at' => date('Y-m-d')]);
        return $this->json(['ok' => true]);
    }
    public function adminsDelete($user)
    {
        if ($f = $this->guard()) return $f;
        if ($user === $this->sess->get('uid')) return $this->json(['error' => '본인 계정은 삭제 불가'], 400);
        $this->db->table('admins')->delete(['username' => $user]);
        return $this->json(['ok' => true]);
    }

    // ====================================================================
    // 문의
    // ====================================================================
    public function inqAdd()   // 공개
    {
        $d = $this->body();
        $this->db->table('inquiries')->insert([
            'company' => $d['company'] ?? '', 'name' => $d['name'] ?? '', 'phone' => $d['phone'] ?? '',
            'email' => $d['email'] ?? '', 'field' => $d['field'] ?? '', 'message' => $d['message'] ?? '',
            'status' => 'new', 'created_at' => date('Y-m-d H:i:s'),
        ]);
        return $this->json(['ok' => true]);
    }
    public function inqList()
    {
        if ($f = $this->guard()) return $f;
        $rows = $this->db->table('inquiries')->orderBy('created_at', 'DESC')->get()->getResultArray();
        foreach ($rows as &$r) { $r['id'] = (int)$r['id']; $r['ts'] = strtotime($r['created_at']); }
        return $this->json($rows);
    }
    public function inqDelete($id)
    {
        if ($f = $this->guard()) return $f;
        $this->db->table('inquiries')->delete(['id' => (int)$id]);
        return $this->json(['ok' => true]);
    }

    // ====================================================================
    // 관리자 UI 서빙
    // ====================================================================
    public function adminUi()
    {
        return $this->response->setBody(file_get_contents($this->uiDir . 'index.html'));
    }
    public function adminAsset($file)
    {
        $path = $this->uiDir . basename($file);
        if (!is_file($path)) return $this->response->setStatusCode(404)->setBody('not found');
        $ct = ['css' => 'text/css', 'js' => 'application/javascript', 'html' => 'text/html'];
        $ext = pathinfo($path, PATHINFO_EXTENSION);
        return $this->response->setContentType($ct[$ext] ?? 'text/plain')->setBody(file_get_contents($path));
    }

    /** 카피 편집모드 — 사이트 페이지 HTML에 편집 스크립트 주입해서 반환 */
    public function editMode($page)
    {
        if (!$this->authed()) return $this->response->redirect('/admin');
        $file = FCPATH . basename($page);
        if (!is_file($file)) return $this->response->setStatusCode(404)->setBody('not found');
        $html = file_get_contents($file);
        $html = str_replace('</body>', $this->bake->editModeScript() . '</body>', $html);
        return $this->response->setContentType('text/html')->setBody($html);
    }
}

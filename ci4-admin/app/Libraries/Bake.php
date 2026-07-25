<?php
namespace App\Libraries;

/**
 * 정적 HTML 굽기 (Flask admin/bake*.py 의 PHP 포팅).
 * 편집 저장 → public/ 의 정적 HTML을 직접 갱신. JS 렌더 0 = AI/검색이 소스를 그대로 읽음.
 * 사이트 페이지는 public/ 에 위치(웹서버가 직접 서빙).
 */
class Bake
{
    const DOMAIN = 'https://incheondesign.co.kr';
    const INIT = 60;   // 포트폴리오 첫 화면 노출 수

    private function site(string $file): string { return FCPATH . $file; }
    private function get(string $file): string { return @file_get_contents($this->site($file)) ?: ''; }
    private function put(string $file, string $s): void { file_put_contents($this->site($file), $s); }

    // ---------- 페이지 목록 ----------
    public function faqPages(): array
    {
        return [
            'svc-brand' => '브랜딩 · 로고', 'svc-ppt' => 'PPT · 제안서',
            'svc-web' => '홈페이지 · 웹', 'svc-studio' => '촬영 · 스튜디오',
            'catalog' => '카탈로그 · 카다로그', 'leaflet' => '리플렛 · 리플릿',
            'pamphlet' => '팜플렛 · 팜플릿', 'brochure' => '브로슈어 · 브로셔', 'poster' => '포스터',
        ];
    }
    public function seoPages(): array
    {
        return [
            'index' => '홈', 'about' => '회사소개', 'portfolio' => '포트폴리오',
            'column' => '블로그', 'contact' => '문의',
            'svc-brand' => '브랜딩·로고', 'svc-ppt' => 'PPT·제안서', 'svc-web' => '홈페이지·웹',
            'svc-studio' => '촬영·스튜디오', 'catalog' => '카탈로그', 'leaflet' => '리플렛',
            'pamphlet' => '팜플렛', 'brochure' => '브로슈어', 'poster' => '포스터',
        ];
    }
    public function copyPages(): array
    {
        return [
            'index' => '홈', 'about' => '회사소개', 'portfolio' => '포트폴리오', 'contact' => '문의',
            'catalog' => '카탈로그', 'leaflet' => '리플렛', 'pamphlet' => '팜플렛',
            'brochure' => '브로슈어', 'poster' => '포스터',
            'svc-brand' => '브랜딩·로고', 'svc-ppt' => 'PPT·제안서', 'svc-web' => '홈페이지·웹', 'svc-studio' => '촬영·스튜디오',
        ];
    }
    private function allPages(): array
    {
        $p = ['index','about','portfolio','column','contact','svc-brand','svc-ppt','svc-web','svc-studio',
              'catalog','leaflet','pamphlet','brochure','poster','column-design','column-catalog','column-logo','column-print'];
        $files = array_map(fn($x) => "$x.html", $p);
        foreach (glob(FCPATH . 'col-*.html') ?: [] as $f) $files[] = basename($f);
        return array_values(array_filter($files, fn($f) => is_file($this->site($f))));
    }

    // ---------- 이미지 리사이즈 ----------
    public function resize(string $path, int $max): void
    {
        if (!function_exists('imagecreatetruecolor')) return;
        [$w, $h] = @getimagesize($path) ?: [0, 0];
        if ($w <= $max && $h <= $max || $w == 0) return;
        $ratio = $max / max($w, $h); $nw = (int)($w * $ratio); $nh = (int)($h * $ratio);
        $ext = strtolower(pathinfo($path, PATHINFO_EXTENSION));
        $src = match ($ext) { 'png' => @imagecreatefrompng($path), 'webp' => @imagecreatefromwebp($path), 'gif' => @imagecreatefromgif($path), default => @imagecreatefromjpeg($path) };
        if (!$src) return;
        $dst = imagecreatetruecolor($nw, $nh);
        if (in_array($ext, ['png','gif'])) { imagealphablending($dst, false); imagesavealpha($dst, true); }
        imagecopyresampled($dst, $src, 0, 0, 0, 0, $nw, $nh, $w, $h);
        match ($ext) { 'png' => imagepng($dst, $path), 'webp' => imagewebp($dst, $path, 82), 'gif' => imagegif($dst, $path), default => imagejpeg($dst, $path, 82) };
        imagedestroy($src); imagedestroy($dst);
    }

    // ---------- 포트폴리오 ----------
    public function portfolio(array $rows): int
    {
        usort($rows, fn($a, $b) => $a['sort_order'] <=> $b['sort_order']);
        $html = '';
        foreach ($rows as $i => $it) {
            $more = $i >= self::INIT;
            $hide = $more ? ' style="display:none"' : '';
            $cls = $more ? ' pf-more' : '';
            $img = $it['image'];
            $html .= '<div class="pf-card' . $cls . '" data-cat="' . $it['category'] . '"' . $hide . '>'
                . '<div class="pf-card-thumb" data-modal="' . $img . '">'
                . '<div class="pf-card-img" style="background-image:url(\'' . $img . '\')"></div></div>'
                . '<h2 class="pf-card-name">' . $it['title'] . '</h2>'
                . '<p class="pf-card-type">' . $it['type'] . "</p></div>\n";
        }
        $s = $this->get('portfolio.html');
        $remain = max(0, count($rows) - self::INIT);
        $btn = '<div class="pf-morewrap"><button type="button" id="pfMore" class="pf-morebtn">작업물 더 보기 <span>(' . $remain . ')</span></button></div>';
        // pf-grid 내부 교체(morewrap 보존)
        if (preg_match('/(<div class="pf-grid"[^>]*>)(.*?)(<div class="pf-morewrap">.*?<\/div>\s*<\/div>\s*<\/section>|<\/div>\s*<\/div>\s*<\/section>)/s', $s, $m)) {
            $tail = $m[3];
            if (strpos($tail, 'pf-morewrap') !== false) {
                $tail = preg_replace('/<div class="pf-morewrap">.*?<\/div>\s*(<\/div>\s*<\/div>\s*<\/section>)/s', $btn . '$1', $tail);
            } else {
                $tail = preg_replace('/<\/div>/', $btn . '</div>', $tail, 1);
            }
            $s = str_replace($m[0], $m[1] . "\n" . $html . $tail, $s);
            $this->put('portfolio.html', $s);
        }
        return count($rows);
    }

    // ---------- FAQ ----------
    private function stripTags2(string $x): string { return trim(preg_replace('/\s+/', ' ', strip_tags($x))); }
    public function extractDefaultFaq(string $page): array
    {
        $s = $this->get("$page.html");
        if (!preg_match('/<section class="svc-faq">(.*?)<\/section>/s', $s, $m)) return [];
        $body = preg_replace('/<!--faq-extra-->.*?<!--\/faq-extra-->/s', '', $m[1]);
        $out = [];
        if (preg_match_all('/<details class="svc-faq-item"><summary>(.*?)<\/summary><div class="svc-faq-a"><p>(.*?)<\/p>/s', $body, $mm, PREG_SET_ORDER)) {
            foreach ($mm as $x) $out[] = ['q' => $this->stripTags2($x[1]), 'a' => $this->stripTags2($x[2])];
        }
        return $out;
    }
    public function faq(string $page, array $items): array
    {
        $s = $this->get("$page.html");
        $s = preg_replace('/<!--faq-extra-->.*?<!--\/faq-extra-->/s', '', $s);
        $s = preg_replace('/<!--faq-jsonld-->.*?<!--\/faq-jsonld-->/s', '', $s);
        if ($items) {
            $newitems = '';
            foreach ($items as $it) {
                $newitems .= '<details class="svc-faq-item"><summary>' . $it['q'] . '</summary>'
                    . '<div class="svc-faq-a"><p>' . $it['a'] . '</p></div></details>';
            }
            $s = preg_replace('/(<section class="svc-faq">.*?<\/p>)(.*?)(<\/section>)/s', '$1' . $this->pregSafe($newitems) . '$3', $s, 1);
            $allqa = $items;
        } else {
            $allqa = $this->extractDefaultFaq($page);
        }
        if ($allqa) {
            $entities = array_map(fn($x) => ['@type' => 'Question', 'name' => $x['q'],
                'acceptedAnswer' => ['@type' => 'Answer', 'text' => $x['a']]], $allqa);
            $ld = ['@context' => 'https://schema.org', '@type' => 'FAQPage', 'mainEntity' => $entities];
            $jsonld = '<!--faq-jsonld--><script type="application/ld+json">' . json_encode($ld, JSON_UNESCAPED_UNICODE) . '</script><!--/faq-jsonld-->';
            $s = preg_replace('/<\/head>/', $jsonld . "\n</head>", $s, 1);
        }
        $this->put("$page.html", $s);
        return [count($items), count($allqa)];
    }
    private function pregSafe(string $s): string { return str_replace(['\\', '$'], ['\\\\', '\\$'], $s); }

    // ---------- SEO ----------
    public function readMeta(string $page): ?array
    {
        if (!is_file($this->site("$page.html"))) return null;
        $s = $this->get("$page.html");
        $g = fn($re) => (preg_match($re, $s, $m) ? trim($m[1]) : '');
        return [
            'title' => $g('/<title>(.*?)<\/title>/s'),
            'description' => $g('/<meta\s+name="description"\s+content="([^"]*)"/'),
            'keywords' => $g('/<meta\s+name="keywords"\s+content="([^"]*)"/'),
        ];
    }
    public function seo(string $page, array $meta): void
    {
        $s = $this->get("$page.html");
        $ea = fn($v) => str_replace('"', '&quot;', $v);
        if (!empty($meta['title'])) {
            $t = $meta['title'];
            $s = preg_replace('/<title>.*?<\/title>/s', '<title>' . $this->pregSafe($t) . '</title>', $s, 1);
            $s = preg_replace('/(<meta\s+property="og:title"\s+content=")[^"]*(")/', '${1}' . $this->pregSafe($ea($t)) . '$2', $s);
            $s = preg_replace('/(<meta\s+name="twitter:title"\s+content=")[^"]*(")/', '${1}' . $this->pregSafe($ea($t)) . '$2', $s);
        }
        $setMeta = function (string $name, string $val) use (&$s, $ea) {
            if (preg_match('/<meta\s+name="' . $name . '"\s+content="[^"]*"/', $s)) {
                $s = preg_replace('/(<meta\s+name="' . $name . '"\s+content=")[^"]*(")/', '${1}' . $this->pregSafe($ea($val)) . '$2', $s, 1);
            } elseif ($val !== '') {
                $s = str_replace('</head>', '<meta name="' . $name . '" content="' . $ea($val) . "\">\n</head>", $s);
            }
        };
        if (array_key_exists('description', $meta)) {
            $setMeta('description', $meta['description']);
            $s = preg_replace('/(<meta\s+property="og:description"\s+content=")[^"]*(")/', '${1}' . $this->pregSafe($ea($meta['description'])) . '$2', $s);
        }
        if (array_key_exists('keywords', $meta)) $setMeta('keywords', $meta['keywords']);
        $this->put("$page.html", $s);
    }

    // ---------- 히어로 ----------
    private function titleToH2(string $t): string
    {
        $t = preg_replace('/\*([^*]+)\*/', '<b>$1</b>', $t);
        return str_replace("\n", '<br>', $t);
    }
    public function hero(array $rows): int
    {
        usort($rows, fn($a, $b) => $a['sort_order'] <=> $b['sort_order']);
        $html = '';
        foreach ($rows as $i => $sl) {
            $on = $i === 0 ? ' on' : '';
            $html .= '<div class="bw-slide' . $on . '"><h2>' . $this->titleToH2($sl['title']) . '</h2>'
                . '<a class="bw-bnr" href="' . ($sl['btn1_link'] ?: 'portfolio.html') . '">'
                . '<img src="' . $sl['image'] . '" alt="' . $sl['eyebrow'] . '" loading="lazy">'
                . '<div class="bw-txt"><div class="bw-cat">' . $sl['eyebrow'] . '</div>'
                . '<p>' . $sl['subtitle'] . '</p></div></a></div>';
        }
        $s = $this->get('index.html');
        if (preg_match_all('/<div class="bw-slide[^"]*">.*?<\/a><\/div>/s', $s, $m, PREG_OFFSET_CAPTURE)) {
            $first = $m[0][0][1];
            $lastM = end($m[0]);
            $end = $lastM[1] + strlen($lastM[0]);
            $s = substr($s, 0, $first) . $html . substr($s, $end);
            $this->put('index.html', $s);
        }
        return count($rows);
    }

    // ---------- 칼럼(블로그) ----------
    public function columns(array $rows): int
    {
        usort($rows, fn($a, $b) => strcmp($b['date'], $a['date']));
        $tpl = $this->get('column-design.html');
        foreach ($rows as $idx => $c) {
            $s = $this->buildColumn($tpl, $c, $rows, $idx);
            $this->put("col-{$c['id']}.html", $s);
        }
        // 목록 카드
        $ls = $this->get('column.html');
        $ls = preg_replace('/<!--adm-cols-->.*?<!--\/adm-cols-->/s', '', $ls);
        $cards = '<!--adm-cols-->';
        foreach ($rows as $c) {
            $thumb = $c['thumbnail'] ?: 'theme/assets/first/column-card.png';
            $cards .= '<article class="blog-item" data-cat="' . $c['category'] . '" data-title="' . $c['title'] . '">'
                . '<a class="blog-item-link" href="col-' . $c['id'] . '.html">'
                . '<div class="blog-item-img"><img src="' . $thumb . '" alt="' . $c['title'] . '" loading="lazy"></div>'
                . '<div class="blog-item-info"><span class="blog-item-cat">' . $c['category'] . '</span>'
                . '<h3 class="blog-item-tit">' . $c['title'] . '</h3>'
                . '<div class="blog-item-meta"><time class="blog-item-date">' . str_replace('-', '.', $c['date']) . '</time>'
                . '<span class="blog-item-readtime">' . $this->readTime($c['body']) . '분 분량</span></div></div></a></article>';
        }
        $cards .= '<!--/adm-cols-->';
        $ls = preg_replace('/(<div class="blog-list">)/', '$1' . $this->pregSafe($cards), $ls, 1);
        $this->put('column.html', $ls);
        return count($rows);
    }
    private function readTime(string $body): int { return max(1, (int)round(mb_strlen(strip_tags($body)) / 500)); }
    private function buildColumn(string $s, array $c, array $all, int $idx): string
    {
        $title = $c['title']; $cat = $c['category']; $date = $c['date'];
        $excerpt = $c['excerpt']; $thumb = $c['thumbnail'] ?: 'theme/assets/first/column-card.png';
        $url = self::DOMAIN . "/col-{$c['id']}.html";
        // 본문 h2 id + TOC
        $n = 0; $items = [];
        $body = preg_replace_callback('/<h2([^>]*)>(.*?)<\/h2>/s', function ($m) use (&$n, &$items) {
            $n++; $sid = "sec-$n"; $txt = trim(strip_tags($m[2]));
            $items[] = [$sid, $txt];
            return '<h2 id="' . $sid . '"' . $m[1] . '>' . $m[2] . '</h2>';
        }, $c['body']);
        $toc = ''; foreach ($items as $it) $toc .= '<li class="blog-toc-item"><a href="#' . $it[0] . '">' . $it[1] . '</a></li>';
        $rt = $this->readTime($c['body']);
        // head
        $s = preg_replace('/<title>.*?<\/title>/s', '<title>' . $this->pregSafe($title) . ' | 퍼스트디자인 인천지사</title>', $s, 1);
        $s = preg_replace('/(<meta name="description" content=")[^"]*(")/', '${1}' . $this->pregSafe($excerpt ?: $title) . '$2', $s);
        $s = preg_replace('/<link rel="canonical"[^>]*>/', '<link rel="canonical" href="' . $url . '">', $s);
        $s = preg_replace('/(<meta property="og:title" content=")[^"]*(")/', '${1}' . $this->pregSafe($title) . '$2', $s);
        $s = preg_replace('/(<meta property="og:url" content=")[^"]*(")/', '${1}' . $url . '$2', $s);
        // JSON-LD (Article + Breadcrumb + FAQ 자동감지)
        $s = preg_replace('/<!--col-jsonld-->.*?<!--\/col-jsonld-->/s', '', $s);
        $s = preg_replace('/<!--faq-jsonld-->.*?<!--\/faq-jsonld-->/s', '', $s);
        $article = ['@context' => 'https://schema.org', '@type' => 'BlogPosting', 'headline' => $title,
            'description' => $excerpt, 'image' => self::DOMAIN . '/' . $thumb,
            'datePublished' => $date, 'dateModified' => $date,
            'author' => ['@type' => 'Organization', 'name' => '퍼스트디자인 인천지사'],
            'publisher' => ['@type' => 'Organization', 'name' => '퍼스트디자인 인천지사',
                'logo' => ['@type' => 'ImageObject', 'url' => self::DOMAIN . '/theme/assets/first/favicon.png']],
            'mainEntityOfPage' => $url, 'articleSection' => $cat];
        $crumb = ['@context' => 'https://schema.org', '@type' => 'BreadcrumbList', 'itemListElement' => [
            ['@type' => 'ListItem', 'position' => 1, 'name' => '홈', 'item' => self::DOMAIN . '/'],
            ['@type' => 'ListItem', 'position' => 2, 'name' => '블로그', 'item' => self::DOMAIN . '/column.html'],
            ['@type' => 'ListItem', 'position' => 3, 'name' => $title, 'item' => $url]]];
        $faqScript = '';
        $faqPairs = $this->extractFaqFromBody($c['body']);
        if ($faqPairs) {
            $ent = array_map(fn($x) => ['@type' => 'Question', 'name' => $x[0], 'acceptedAnswer' => ['@type' => 'Answer', 'text' => $x[1]]], $faqPairs);
            $faqScript = '<script type="application/ld+json">' . json_encode(['@context' => 'https://schema.org', '@type' => 'FAQPage', 'mainEntity' => $ent], JSON_UNESCAPED_UNICODE) . '</script>';
        }
        $ld = '<!--col-jsonld--><script type="application/ld+json">' . json_encode($article, JSON_UNESCAPED_UNICODE)
            . '</script><script type="application/ld+json">' . json_encode($crumb, JSON_UNESCAPED_UNICODE) . '</script>' . $faqScript . '<!--/col-jsonld-->';
        $s = str_replace('</head>', $ld . "\n</head>", $s);
        // 콘텐츠 치환
        $s = preg_replace('/(<nav class="blog-breadcrumb">.*?<span>)(.*?)(<\/span><\/nav>)/s', '${1}' . $this->pregSafe($title) . '$3', $s, 1);
        $s = preg_replace('/(<a class="blog-single-cat"[^>]*>)(.*?)(<\/a>)/s', '${1}' . $this->pregSafe($cat) . '$3', $s, 1);
        $s = preg_replace('/(<h1 class="blog-single-tit">)(.*?)(<\/h1>)/s', '${1}' . $this->pregSafe($title) . '$3', $s, 1);
        $s = preg_replace('/(<ul class="blog-single-meta">).*?(<\/ul>)/s', '${1}' . '<li>' . str_replace('-', '.', $date) . '</li><li>' . $rt . '분 분량</li><li>퍼스트디자인 인천지사</li>' . '$2', $s, 1);
        $s = preg_replace('/(<div class="blog-single-thumb"><img src=")[^"]*(" alt=")[^"]*(">)/', '${1}' . $thumb . '${2}' . $this->pregSafe($title) . '$3', $s, 1);
        $s = preg_replace('/(<details class="blog-single-toc-mobile"><summary>목차 <span>▾<\/span><\/summary><ol>).*?(<\/ol><\/details>)/s', '${1}' . $this->pregSafe($toc) . '$2', $s, 1);
        $s = preg_replace('/(<ol class="blog-single-toc-list">).*?(<\/ol>)/s', '${1}' . $this->pregSafe($toc) . '$2', $s, 1);
        $s = preg_replace('/(<div class="blog-single-body">).*?(<\/div>\s*<div class="blog-single-cta">)/s', '${1}' . $this->pregSafe($body) . '</div>' . "\n" . '<div class="blog-single-cta">', $s, 1);
        // 이전/다음
        $nav = '';
        if ($idx + 1 < count($all)) { $p = $all[$idx + 1]; $nav .= '<a class="blog-single-nav-item" href="col-' . $p['id'] . '.html"><span class="blog-single-nav-label">이전 글</span><span class="blog-single-nav-tit">' . $p['title'] . '</span></a>'; }
        if ($idx > 0) { $nx = $all[$idx - 1]; $nav .= '<a class="blog-single-nav-item blog-single-nav-next" href="col-' . $nx['id'] . '.html"><span class="blog-single-nav-label">다음 글</span><span class="blog-single-nav-tit">' . $nx['title'] . '</span></a>'; }
        $s = preg_replace('/(<nav class="blog-single-nav">).*?(<\/nav>)/s', '${1}' . $this->pregSafe($nav) . '$2', $s, 1);
        return $s;
    }
    private function extractFaqFromBody(string $body): array
    {
        $out = [];
        if (preg_match_all('/<details[^>]*>\s*<summary[^>]*>(.*?)<\/summary>(.*?)<\/details>/is', $body, $m, PREG_SET_ORDER)) {
            foreach ($m as $x) { $q = $this->stripTags2($x[1]); $a = $this->stripTags2($x[2]); if ($q && $a) $out[] = [$q, $a]; }
            if ($out) return $out;
        }
        if (preg_match('/<h[23][^>]*>\s*(?:자주\s*묻는\s*질문|FAQ|Q\s*&\s*A)\s*<\/h[23]>/i', $body, $hm, PREG_OFFSET_CAPTURE)) {
            $region = substr($body, $hm[0][1] + strlen($hm[0][0]));
            $parts = preg_split('/(<h3[^>]*>.*?<\/h3>)/is', $region, -1, PREG_SPLIT_DELIM_CAPTURE);
            for ($i = 1; $i < count($parts); $i += 2) {
                if (preg_match('/<h2/i', $parts[$i])) break;
                $q = $this->stripTags2($parts[$i]); $a = isset($parts[$i + 1]) ? $this->stripTags2($parts[$i + 1]) : '';
                if ($q && $a) $out[] = [$q, $a];
            }
        }
        return $out;
    }

    // ---------- 설정(Head코드·파비콘·og) ----------
    public function settings(array $st): int
    {
        $head = trim($st['headCode'] ?? '');
        $favicon = $st['favicon'] ?? ''; $og = $st['ogImage'] ?? '';
        $n = 0;
        foreach ($this->allPages() as $f) {
            $s = $this->get($f);
            $s = preg_replace('/<!--head-code-->.*?<!--\/head-code-->/s', '', $s);
            if ($head) $s = str_replace('</head>', '<!--head-code-->' . $head . "<!--/head-code-->\n</head>", $s);
            if ($favicon) {
                if (preg_match('/<link[^>]*rel="(?:shortcut )?icon"[^>]*>/', $s))
                    $s = preg_replace('/<link[^>]*rel="(?:shortcut )?icon"[^>]*>/', '<link rel="icon" href="/' . $favicon . '">', $s, 1);
                else $s = str_replace('</head>', '<link rel="icon" href="/' . $favicon . "\">\n</head>", $s);
            }
            if ($og) $s = preg_replace('/(<meta property="og:image" content=")[^"]*(")/', '${1}' . self::DOMAIN . '/' . $og . '$2', $s);
            $this->put($f, $s); $n++;
        }
        return $n;
    }

    // ---------- 카피(문구) ----------
    public function contentApply(string $key, array $edits, $db): int
    {
        $file = "$key.html"; $s = $this->get($file); if ($s === '') return 0;
        $applied = 0;
        foreach ($edits as $e) {
            $orig = $e['orig'] ?? ''; $new = $e['new'] ?? '';
            if (!$orig || $orig === $new || strpos($s, $orig) === false) continue;
            $pos = strpos($s, $orig); $s = substr_replace($s, $new, $pos, strlen($orig));
            // 재편집(new==orig)면 갱신, 아니면 추가
            $row = $db->table('content_overrides')->where('page', $key)->where('new', $orig)->get()->getRowArray();
            if ($row) $db->table('content_overrides')->where('id', $row['id'])->update(['new' => $new]);
            else $db->table('content_overrides')->insert(['page' => $key, 'orig' => $orig, 'new' => $new]);
            $applied++;
        }
        $this->put($file, $s);
        return $applied;
    }
    public function contentReset(string $key, $db): void
    {
        $file = "$key.html"; $s = $this->get($file);
        $rows = $db->table('content_overrides')->where('page', $key)->orderBy('id', 'DESC')->get()->getResultArray();
        foreach ($rows as $o) { $pos = strpos($s, $o['new']); if ($pos !== false) $s = substr_replace($s, $o['orig'], $pos, strlen($o['new'])); }
        $this->put($file, $s);
        $db->table('content_overrides')->delete(['page' => $key]);
    }

    // ---------- 카피 편집모드 스크립트 ----------
    public function editModeScript(): string
    {
        return <<<'HTML'
<style>
#__cebar{position:fixed;left:0;right:0;bottom:0;background:#0f1f1c;color:#fff;padding:12px 20px;display:flex;gap:12px;align-items:center;z-index:99999;font-family:Pretendard,sans-serif;box-shadow:0 -6px 24px rgba(0,0,0,.3)}
#__cebar b{color:#2fd0bd}#__cebar .sp{flex:1}
#__cebar button{font:inherit;font-weight:700;border:none;border-radius:8px;padding:9px 18px;cursor:pointer}
#__cesave{background:#0C9384;color:#fff}#__ceclose{background:#2a2c26;color:#cfd3c8}
[data-ce]:hover{outline:2px dashed #0C9384;outline-offset:2px;cursor:text}
[data-ce]:focus{outline:2px solid #0C9384;outline-offset:2px;background:#eefaf7}
</style>
<script>
(function(){
  var INLINE={SPAN:1,B:1,STRONG:1,EM:1,I:1,A:1,BR:1,SUB:1,SUP:1,MARK:1,SMALL:1,U:1,TIME:1,DEL:1,INS:1};
  var SKIP={SCRIPT:1,STYLE:1,SVG:1,BUTTON:1,NAV:1,IMG:1,INPUT:1,SELECT:1,TEXTAREA:1};
  function isLeaf(el){if(!el.textContent.trim())return false;for(var i=0;i<el.children.length;i++){if(!INLINE[el.children[i].tagName])return false;}return true;}
  var roots=[].slice.call(document.querySelectorAll('main, .cta-section, .cta2, .ct-faq')),set=[];
  roots.forEach(function(root){[].slice.call(root.querySelectorAll('*')).forEach(function(el){
    if(SKIP[el.tagName]||el.closest('#__cebar')||el.closest('nav')||el.closest('svg'))return;
    if(el.parentElement&&isLeaf(el.parentElement))return;
    if(isLeaf(el)&&set.indexOf(el)<0)set.push(el);});});
  var els=set;
  els.forEach(function(el){el.setAttribute('data-ce','1');el.setAttribute('data-orig',el.innerHTML);el.setAttribute('contenteditable','true');});
  var bar=document.createElement('div');bar.id='__cebar';
  bar.innerHTML='<b>편집 모드</b> — 글자를 클릭해 수정하세요 <span class="sp"></span><button id="__cesave">저장 · 사이트 반영</button><button id="__ceclose">닫기</button>';
  document.body.appendChild(bar);
  document.getElementById('__ceclose').onclick=function(){location.href=location.pathname.replace('/editmode/','/');};
  document.getElementById('__cesave').onclick=function(){
    var edits=[];els.forEach(function(el){var o=el.getAttribute('data-orig'),n=el.innerHTML;if(o!==n)edits.push({orig:o,new:n});});
    if(!edits.length){alert('변경된 문구가 없습니다.');return;}
    var page=location.pathname.split('/').pop()||'index.html';
    fetch('/api/content/'+encodeURIComponent(page),{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json'},body:JSON.stringify({edits:edits})})
      .then(function(r){return r.json();}).then(function(r){if(r.ok){alert(r.count+'곳 저장·반영되었습니다.');location.reload();}else alert(r.error||'저장 실패');});
  };
})();
</script>
HTML;
    }

    // ---------- 이미지 교체 ----------
    public function imagesList(string $page, $db): array
    {
        $file = str_ends_with($page, '.html') ? $page : "$page.html";
        if (!is_file($this->site($file))) return [];
        $s = $this->get($file);
        $ovRows = $db->table('image_overrides')->where('page', $page)->get()->getResultArray();
        $rev = []; foreach ($ovRows as $r) $rev[$r['new_src']] = $r['original_src'];
        $seen = []; $out = [];
        if (preg_match_all('/(?:<img[^>]+src="|background-image:url\(\')(theme\/assets\/first\/[^"\')]+\.(?:jpg|jpeg|png|webp))/', $s, $m)) {
            foreach ($m[1] as $cur) {
                if (isset($seen[$cur]) || strpos($cur, '/svc/') !== false || strpos($cur, 'favicon') !== false) continue;
                $seen[$cur] = 1;
                $original = $rev[$cur] ?? $cur;
                $out[] = ['id' => count($out), 'original' => $original, 'src' => $cur, 'overridden' => isset($rev[$cur])];
            }
        }
        return array_slice($out, 0, 60);
    }
    public function imageReplace(string $page, string $original, string $newsrc, $db): void
    {
        $file = str_ends_with($page, '.html') ? $page : "$page.html";
        $row = $db->table('image_overrides')->where('page', $page)->where('original_src', $original)->get()->getRowArray();
        $cur = $row ? $row['new_src'] : $original;
        $s = str_replace($cur, $newsrc, $this->get($file));
        $this->put($file, $s);
        if ($row) $db->table('image_overrides')->where('id', $row['id'])->update(['new_src' => $newsrc]);
        else $db->table('image_overrides')->insert(['page' => $page, 'original_src' => $original, 'new_src' => $newsrc]);
    }
    public function imageRevert(string $page, string $original, $db): void
    {
        $file = str_ends_with($page, '.html') ? $page : "$page.html";
        $row = $db->table('image_overrides')->where('page', $page)->where('original_src', $original)->get()->getRowArray();
        if ($row) {
            $s = str_replace($row['new_src'], $original, $this->get($file));
            $this->put($file, $s);
            $db->table('image_overrides')->delete(['id' => $row['id']]);
        }
    }
}

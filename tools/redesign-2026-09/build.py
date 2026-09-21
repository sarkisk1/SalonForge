#!/usr/bin/env python3
"""Port the ChatGPT design preview onto the live daviana.app static site.

Base = preview page (design + copy). Restored from the live page: the whole
<head> SEO block (canonical, OG, hreflang, JSON-LD, analytics) and the body
scripts that make the forms work. Preview-only scaffolding is removed.
"""
import re, sys, json, shutil, pathlib, subprocess

SP = pathlib.Path(__file__).parent
PREV, DIST = SP / "preview", SP / "site" / "dist"
ORIGIN = "https://daviana.app"
BASE = "origin/main"

# preview file -> live dist dir ('' = root)
PAGES = {
    "index": "", "daviana": "diary", "colorlab": "colorlab",
    "ai-receptionist": "ai-receptionist", "pricing": "pricing", "trial": "trial",
    "demo": "demo", "blog": "blog", "compare": "compare", "tools": "tools",
    "faq": "faq", "privacy": "privacy", "other-software": "other-software",
}
URL = {k: ("/" if v == "" else f"/{v}/") for k, v in PAGES.items()}

# Pages whose copy is genuinely new get new titles/descriptions.
META = {
    "index": ("Daviana — salon software for booking, colour and the phone",
              "Salon software built inside working salons: Daviana Booking for the diary and till, ColorLab for colour formulas costed to the gram, and Aria, an AI receptionist that answers the phone. From £60 a month, no booking commission."),
    "daviana": ("Daviana Booking — salon booking system, till and client records",
                "A salon booking system built inside working salons: appointments by stylist, payments, client notes and visit history in one diary. £80 a month including VAT, no commission on bookings, first month free."),
    "other-software": ("More salon tools — team performance, salon bar and calculators | Daviana",
                       "Beyond booking, colour and the phone: Daviana tools for team performance, tips and targets, the salon bar, and free calculators for missed calls and colour cost."),
}


def rewrite_links(s):
    def fix(m):
        attr, q, v = m.group(1), m.group(2), m.group(3)
        if v.startswith(ORIGIN + "/") and "cdn-cgi" not in v:
            v = v[len(ORIGIN):]
        elif v == ORIGIN:
            v = "/"
        mm = re.match(r"^([a-z-]+)\.html(#.*)?$", v)
        if mm and mm.group(1) in URL:
            v = URL[mm.group(1)] + (mm.group(2) or "")
        elif v.startswith("assets/"):
            v = "/" + v
        return f"{attr}={q}{v}{q}"
    s = re.sub(r'\b(href|src|poster|content)=(["\'])(.*?)\2', fix, s)
    s = re.sub(r'srcset="([^"]*)"', lambda m: 'srcset="' + re.sub(r'(^|,\s*)assets/', r'\1/assets/', m.group(1)) + '"', s)
    return s


def cf_decode(h):
    k = int(h[:2], 16)
    return "".join(chr(int(h[i:i + 2], 16) ^ k) for i in range(2, len(h), 2))


def clean_body(s):
    # Artifacts of the preview having been scraped from behind Cloudflare.
    s = re.sub(r'<a class="__cf_email__" data-cfemail="([0-9a-f]+)"[^>]*>.*?</a>',
               lambda m: f'<a href="mailto:{cf_decode(m.group(1))}">{cf_decode(m.group(1))}</a>', s, flags=re.S)
    s = re.sub(r"<script>(?:(?!</script>).)*challenge-platform.*?</script>", "", s, flags=re.S)
    s = s.replace("<script></script>", "")
    s = re.sub(r'href="[^"]*/cdn-cgi/l/email-protection#([0-9a-f]+)"', lambda m: f'href="mailto:{cf_decode(m.group(1))}"', s)
    s = re.sub(r'<span class="__cf_email__" data-cfemail="([0-9a-f]+)">.*?</span>', lambda m: cf_decode(m.group(1)), s, flags=re.S)
    s = re.sub(r'<div class="local-review-note">.*?</div>', "", s, flags=re.S)
    s = re.sub(r'<div class="review">Design preview.*?</div>\s*', "", s, flags=re.S)
    s = re.sub(r'<p class="local-form-note">.*?</p>', "", s, flags=re.S)
    s = re.sub(r'\s+disabled=""(\s+title="Unavailable in this local design preview")', "", s)
    s = re.sub(r'\s+title="Unavailable in this local design preview"', "", s)
    return s


def head_styles(prev_head):
    out = []
    for m in re.finditer(r"<style[^>]*>.*?</style>|<link[^>]+rel=\"stylesheet\"[^>]*>", prev_head, re.S):
        t = m.group(0)
        t = re.sub(r"\.local-review-note\{[^}]*\}|\.local-form-note\{[^}]*\}", "", t)
        out.append(t)
    return "\n".join(out)


def git_live(rel):
    return subprocess.run(["git", "show", f"{BASE}:{rel}"], cwd=SP / "site", capture_output=True, text=True, check=True).stdout


def css_rules_matching(css, pat):
    """Top-level rules (and @media blocks, filtered inside) whose selector matches pat."""
    out, i, n = [], 0, len(css)
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    n = len(css)
    while i < n:
        j = css.find("{", i)
        if j < 0:
            break
        depth, k = 1, j + 1
        while depth and k < n:
            depth += {"{": 1, "}": -1}.get(css[k], 0)
            k += 1
        sel, block = css[i:j].strip(), css[j + 1:k - 1]
        if sel.startswith("@media"):
            inner = css_rules_matching(block, pat)
            if inner:
                out.append(f"{sel}{{{inner}}}")
        elif sel.startswith("@keyframes"):
            if re.search(r"ci-pulse", sel):
                out.append(f"{sel}{{{block}}}")
        elif re.search(pat, sel):
            out.append(f"{sel}{{{block}}}")
        i = k
    return "".join(out)


def callit_section():
    """The 'Aria rings you' live demo lived on the old home page (#call-it).
    The new home page drops it, so it moves to the Aria product page."""
    s = git_live("dist/index.html")
    i = s.index('id="call-it"')
    sec = s[s.rfind("<section", 0, i): s.index("</section>", i) + 10]
    sec = re.sub(r'<div class="chapter reveal">.*?</div>', "", sec, count=1, flags=re.S)
    css = "".join(re.findall(r"<style[^>]*>(.*?)</style>", s[: s.index("<body")], re.S))
    css = css_rules_matching(css, r"callit|\.cres")
    tail = ('<script src="/assets/formguard.js"></script>'
            '<script src="https://challenges.cloudflare.com/turnstile/v0/api.js?onload=sfTurnstileReady&render=explicit" async defer></script>')
    return f"<style>{css}</style>\n{sec}\n{tail}\n"


def build(name):
    prev = (PREV / f"{name}.html").read_text()
    prev = rewrite_links(clean_body(prev))
    p_head, p_body = prev[: prev.index("<body")], prev[prev.index("<body"):]

    # Always read the live page from the base commit, never from the working
    # tree: this script overwrites dist/, so the tree is not a stable input.
    rel = f"dist/{PAGES[name]}/index.html".replace("//", "/")
    r = subprocess.run(["git", "show", f"{BASE}:{rel}"], cwd=SP / "site", capture_output=True, text=True)
    is_new = r.returncode != 0
    live = r.stdout if not is_new else subprocess.run(
        ["git", "show", f"{BASE}:dist/tools/index.html"], cwd=SP / "site", capture_output=True, text=True, check=True).stdout
    l_head, l_body = live[: live.index("<body")], live[live.index("<body"):]

    # --- head: live SEO block + preview styles ------------------------------
    styles = head_styles(p_head)
    first = re.search(r"<style", l_head)
    l_head = re.sub(r"<style[^>]*>.*?</style>\s*", "", l_head, flags=re.S)
    l_head = l_head[: first.start()] + styles + "\n" + l_head[first.start():]
    l_head = l_head.replace(
        "</head>",
        '<script defer src="/assets/translations.js?v=1"></script>'
        '<script defer src="/assets/site.js?v=1"></script>\n</head>')
    l_head = re.sub(r"<html[^>]*>", f'<html lang="en" data-page="{name}">', l_head, 1)

    if name in META:
        title, desc = META[name]
        l_head = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", l_head, flags=re.S)
        l_head = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + desc, l_head)
        l_head = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + title, l_head)
        l_head = re.sub(r'(<meta property="og:description" content=")[^"]*', lambda m: m.group(1) + desc, l_head)
        l_head = re.sub(r'(<meta property="og:image:alt" content=")[^"]*', lambda m: m.group(1) + title, l_head)
    if is_new:  # brand-new URL built on a borrowed head
        u = ORIGIN + URL[name]
        l_head = re.sub(r'(<link rel="canonical" href=")[^"]*', lambda m: m.group(1) + u, l_head)
        l_head = re.sub(r'(<meta property="og:url" content=")[^"]*', lambda m: m.group(1) + u, l_head)
        l_head = re.sub(r'<link rel="alternate" hreflang[^>]*>\s*', "", l_head)
        l_head = re.sub(r'<script type="application/ld\+json">.*?</script>\s*', "", l_head, flags=re.S)
    ld = SP / "jsonld" / f"{name}.json"
    if ld.exists():
        l_head = re.sub(r'<script type="application/ld\+json">.*?</script>\s*', "", l_head, flags=re.S)
        blocks = json.loads(ld.read_text())
        tags = "".join(f'<script type="application/ld+json">{json.dumps(b, ensure_ascii=False)}</script>\n' for b in blocks)
        l_head = l_head.replace("</head>", tags + "</head>")

    # --- body: preview body + the live scripts that do real work ------------
    scripts = []
    if not is_new and name != "index":
        for m in re.finditer(r"<script[^>]*>.*?</script>", l_body, re.S):
            t = m.group(0)
            if "#hd .nav" in t:            # old header's language switch / hamburger
                continue
            t = t.replace("hd.classList.toggle", "hd&&hd.classList.toggle")
            scripts.append(t)
    marker = '<div data-site-shell="footer"'
    assert marker in p_body, name
    if name == "ai-receptionist":
        scripts.insert(0, callit_section())
    # The preview's header swap also ate in-page <header> heroes. FAQ lost its <h1>.
    if "<h1" not in p_body:
        hero = re.search(r'<header class="blog-hero">.*?</header>', l_body, re.S)
        assert hero, name
        p_body = p_body.replace('<div class="faq-list">', hero.group(0) + '<div class="faq-list">', 1)
    # The preview disabled form controls; restore the live state.
    if ' disabled' not in re.sub(r"<script.*?</script>", "", l_body, flags=re.S):
        p_body = re.sub(r'(<(?:button|input|select|textarea)\b[^>]*?)\s+disabled=""', r"\1", p_body)
    p_body = p_body.replace('href="/#call-it" target="_blank" rel="noopener noreferrer"', 'href="/ai-receptionist/#call-it"')
    p_body = p_body.replace('href="/#call-it"', 'href="/ai-receptionist/#call-it"')
    p_body = p_body.replace("live call demonstration on the current website.", "live call demonstration.")
    p_body = p_body.replace(marker, "\n".join(scripts) + "\n" + marker, 1)

    if name == "index":
        # Click-to-play hero film: a 1.7MB PNG poster + preload=auto on a 3MB mp4
        # was ~5MB before first paint. Poster is now a 120KB JPEG (it is the LCP
        # image, so it is preloaded) and the film loads when asked for.
        assert 'poster="/assets/salon-connected-thumbnail.png" preload="auto"' in p_body
        p_body = p_body.replace('poster="/assets/salon-connected-thumbnail.png" preload="auto"',
                                'poster="/assets/salon-connected-thumbnail.jpg" preload="none"')
        l_head = l_head.replace("</title>", '</title>\n<link rel="preload" as="image" href="/assets/salon-connected-thumbnail.jpg" fetchpriority="high">', 1)
    out = l_head + p_body
    assert not re.search(r"noindex|local design preview|Your live website|chatgpt\.site", out), name
    dest = DIST / PAGES[name]
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "index.html").write_text(out)
    print(f"{name:16} -> {URL[name]:20} {len(out):7} bytes, {len(scripts)} live scripts")


def site_files():
    today = "2026-09-21"
    sm = git_live("dist/sitemap.xml")
    for n in PAGES:
        loc = f"<loc>{ORIGIN}{URL[n]}</loc>"
        if loc in sm:
            sm = re.sub(re.escape(loc) + r"<lastmod>[^<]*</lastmod>", f"{loc}<lastmod>{today}</lastmod>", sm)
        else:
            sm = sm.replace("</urlset>", f"<url>{loc}<lastmod>{today}</lastmod><changefreq>monthly</changefreq><priority>0.6</priority></url>\n</urlset>")
    (DIST / "sitemap.xml").write_text(sm)

    ll = git_live("dist/llms.txt")
    old = "- [Daviana Diary](https://daviana.app/diary/): the booking spine"
    assert old in ll
    ll = ll.replace(old, "- [Daviana Booking, also called Daviana Diary](https://daviana.app/diary/): the salon booking system and booking spine")
    old2 = "## Key facts"
    ll = ll.replace(old2, "- [More tools](https://daviana.app/other-software/): team performance, the salon bar and the free calculators, in one place.\n\n" + old2, 1)
    (DIST / "llms.txt").write_text(ll)

    rd = git_live("dist/_redirects")
    rd += "\n# 2026-09-21 redesign: the diary product is sold as 'Daviana Booking'. The URL\n# stays /diary/ (it is the indexed one); these catch people typing the name.\n/booking /diary/ 301\n/booking/ /diary/ 301\n/booking-system /diary/ 301\n/booking-system/ /diary/ 301\n/aria-demo /ai-receptionist/#call-it 301\n"
    (DIST / "_redirects").write_text(rd)


if __name__ == "__main__":
    for n in PAGES:
        build(n)
    site_files()
    for f in (PREV / "assets").rglob("*"):
        if f.is_file():
            d = DIST / "assets" / f.relative_to(PREV / "assets")
            d.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, d)

#!/usr/bin/env python3
"""Move journal posts, comparison pages and calculators into the 2026-09 shell.

Same operation the product pages went through: the page's own body, head SEO, structured
data and analytics are untouched; only the old <header id="hd">/<footer> are swapped for the
new header/footer shell, and the shared assets are attached. Idempotent (skips converted pages).
"""
import re, sys, pathlib
DIST = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
REF = (DIST / "colorlab/index.html").read_text()          # an inner page already in the new shell
def take(pat, s):
    m = re.search(pat, s, re.S); assert m, pat; return m.group(0)
HEADER = take(r'<div data-site-shell="header".*?</template></div>', REF)
FOOTER = take(r'<div data-site-shell="footer".*?</template></div>', REF)
EXTRA_STYLE = take(r"<style>body\{padding-top:0!important\}.*?</style>", REF)
NOTICE = '<div class="locale-notice" hidden id="locale-notice" role="status"></div>'
n = 0
for f in sorted(list(DIST.glob("blog/*/index.html")) + list(DIST.glob("compare/*/index.html")) + list(DIST.glob("tools/*/index.html"))):
    s = f.read_text()
    if 'data-site-shell="header"' in s: continue
    head, body = s[: s.index("<body")], s[s.index("<body"):]
    body, k = re.subn(r'<header id="hd">.*?</header>', lambda m: HEADER + NOTICE, body, 1, flags=re.S); assert k == 1, f
    i = body.rfind("<footer"); j = body.index("</footer>", i) + len("</footer>")
    body = body[:i] + FOOTER + body[j:]
    body = re.sub(r"<script>(?:(?!</script>).)*#hd \.nav.*?</script>\s*", "", body, flags=re.S)   # old header's language switch / hamburger
    body = body.replace("hd.classList.toggle", "hd&&hd.classList.toggle")                         # old scroll-shadow script, header now gone
    page = f.parent.name
    head = re.sub(r"<html[^>]*>", f'<html lang="en" data-page="{page}">', head, 1)
    head = head.replace("</head>", EXTRA_STYLE + '<link href="/assets/mobile.css?v=w2" rel="stylesheet"/>'
                        '<script defer src="/assets/translations.js?v=1"></script><script defer src="/assets/site.js?v=3"></script>\n</head>', 1)
    f.write_text(head + body); n += 1
print("pages converted:", n)

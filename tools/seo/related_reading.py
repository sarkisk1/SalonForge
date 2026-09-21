#!/usr/bin/env python3
"""Add a 'Keep reading' block to the English product pages, linking to the journal
posts, calculators and comparisons that answer the same question. Titles are read
from each target page's <title>, so they never drift. Idempotent (class="xl")."""
import re, sys, pathlib, html
DIST = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
MAP = {
    "diary": ["/blog/live-commission-tracking/", "/blog/questions-before-switching-salon-software/", "/compare/daviana-vs-phorest/", "/compare/daviana-vs-fresha/", "/pricing/"],
    "colorlab": ["/blog/colour-cost-per-gram/", "/blog/hair-colour-waste/", "/blog/colour-formulas-when-stylist-leaves/", "/tools/colour-cost-calculator/"],
    "ai-receptionist": ["/blog/after-hours-salon-calls/", "/blog/ai-receptionist-real-diary/", "/tools/missed-call-calculator/", "/pricing/"],
    "pricing": ["/blog/questions-before-switching-salon-software/", "/compare/", "/faq/", "/tools/"],
    "faq": ["/blog/all-in-one-salon-software-meaning/", "/compare/", "/pricing/", "/blog/"],
}
KIND = [("/blog/", "Journal"), ("/compare/", "Comparison"), ("/tools/", "Free calculator"), ("/pricing/", "Pricing"), ("/faq/", "Questions")]
CSS = ('<style>.xl{padding:clamp(40px,5vw,64px) 0 clamp(48px,6vw,80px);border-top:1px solid var(--line,#e7e0d9)}'
       '.xl h2{font-size:clamp(1.3rem,2.2vw,1.7rem);margin-bottom:18px}'
       '.xl ul{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,260px),1fr));gap:14px}'
       '.xl a{display:flex;flex-direction:column;gap:6px;height:100%;padding:18px 20px;border:1px solid var(--line,#e7e0d9);border-radius:14px;text-decoration:none;color:inherit;transition:border-color .2s}'
       '.xl a:hover{border-color:var(--blue,var(--copper,#b84e2c))}'
       '.xl small{font-size:.8rem;font-weight:600;color:var(--blue,var(--copper,#b84e2c))}'
       '.xl span{font-weight:600;line-height:1.35}</style>')
def title(url):
    s = (DIST / url.strip("/") / "index.html").read_text()
    t = html.unescape(re.search(r"<title>(.*?)</title>", s, re.S).group(1))
    return re.sub(r"\s*[|—–-]\s*Daviana\s*$", "", t).strip()
n = 0
for page, targets in MAP.items():
    f = DIST / page / "index.html"; s = f.read_text()
    if 'class="xl' in s: continue
    items = "".join(f'<li><a href="{u}"><small>{next(k for p,k in KIND if u.startswith(p))}</small><span>{html.escape(title(u))}</span></a></li>' for u in targets if u.strip("/") != page)
    block = f'{CSS}<section class="xl wrap"><h2>Keep reading</h2><ul>{items}</ul></section>\n'
    marker = '<div data-site-shell="footer"'
    assert s.count(marker) == 1, page
    f.write_text(s.replace(marker, block + marker)); n += 1
print("blocks added:", n)

#!/usr/bin/env python3
"""Add contextual internal links from journal posts to product/tool pages.

Rules: only inside <div class="prose">, only in <p> text that is not already
inside an <a>, at most one new link per destination per post, at most MAX per
post, anchor text is the words already in the sentence (never rewritten).
Idempotent: a destination the post already links to in its body is skipped.
"""
import re, glob, sys, pathlib
DIST = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
MAX = 4
# destination -> anchor patterns, most specific first
RULES = [
    ("/tools/missed-call-calculator/", [r"missed[- ]call calculator", r"missed calls"]),
    ("/tools/colour-cost-calculator/", [r"colour[- ]cost calculator", r"cost per head", r"cost per gram"]),
    ("/ai-receptionist/", [r"AI receptionist", r"AI Receptionist"]),
    ("/colorlab/", [r"ColorLab", r"colour formulas?"]),
    ("/performance/", [r"live commission", r"commission tracking"]),
    ("/bar/", [r"back[- ]?bar"]),
    ("/diary/", [r"appointment diary", r"booking system"]),
    ("/pricing/", [r"pricing"]),
    ("/faq/", [r"frequently asked questions", r"common questions"]),
]
def link_text_segments(p, dest, pats):
    parts = re.split(r"(<a\b.*?</a>|<[^>]+>)", p, flags=re.S)
    for pat in pats:
        rx = re.compile(r"(?<![\w-])(" + pat + r")(?![\w-])")
        for i in range(0, len(parts), 2):          # even indexes = plain text
            m = rx.search(parts[i])
            if m:
                parts[i] = parts[i][:m.start()] + f'<a href="{dest}">{m.group(1)}</a>' + parts[i][m.end():]
                return "".join(parts), m.group(1)
    return None, None
total = 0
for f in sorted(DIST.glob("blog/*/index.html")):
    s = f.read_text()
    m = re.search(r'(<div class="prose">)(.*?)(?=<section\b)', s, re.S)      # body runs to the CTA section
    if not m: print("SKIP (no prose):", f); continue
    prose = m.group(2); added = []
    existing = set(re.findall(r'<a [^>]*href="([^"]+)"', prose))
    for dest, pats in RULES:
        if len(added) >= MAX: break
        if dest in existing or f"/{f.parent.name}/" in dest: continue
        paras = re.split(r"(<p\b[^>]*>.*?</p>)", prose, flags=re.S)
        for i in range(1, len(paras), 2):
            new, anchor = link_text_segments(paras[i], dest, pats)
            if new:
                paras[i] = new; prose = "".join(paras); added.append((dest, anchor)); break
    if added:
        f.write_text(s[:m.start(2)] + prose + s[m.end(2):]); total += len(added)
    print(f"{f.parent.name:48} +{len(added)}  " + ", ".join(f"{a!r}->{d}" for d, a in added))
print("links added:", total)

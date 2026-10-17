#!/usr/bin/env python3
"""Print one dist page as a markdown section for dist/llms-full.txt.

    python3 tools/seo/llms_full_section.py dist/compare/daviana-vs-vagaro/index.html
    python3 tools/seo/llms_full_section.py --check        # list pages missing from llms-full.txt

The section follows the existing llms-full.txt shape: "## <H1>", Source,
Published/Updated (from the page's JSON-LD), then the article body with page
H2s as ###, FAQ summaries as ####, tables as markdown tables and lists as "- ".
Site chrome (header, breadcrumb, related reading, CTA, footer) is skipped.
No copy is written here: everything comes from the live HTML.
"""
import html
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

SITE = "https://daviana.app"
SKIP_CLASSES = {"crumb", "art-cta", "related", "rr", "related-reading", "share", "toc"}
VOID = {"br", "img", "hr", "meta", "link", "source", "input", "wbr"}
SKIP_TAGS = {"sup", "script", "style", "svg", "noscript", "template", "nav", "footer", "form", "button", "figure"}


class Md(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.buf = [], []
        self.skip = 0
        self.stack = []
        self.in_body = False
        self.h1 = None
        self.mode = None  # current block tag
        self.row, self.rows, self.in_table = [], [], False
        self.cell = None

    def _cls(self, attrs):
        return set((dict(attrs).get("class") or "").split())

    def handle_starttag(self, tag, attrs):
        if tag == "body":
            self.in_body = True
        if not self.in_body or tag in VOID:
            return
        skipping = tag in SKIP_TAGS or bool(self._cls(attrs) & SKIP_CLASSES) or dict(attrs).get("data-site-shell")
        self.stack.append((tag, bool(skipping)))
        if skipping:
            self.skip += 1
            return
        if self.skip:
            return
        if tag == "table":
            self.in_table, self.rows = True, []
        elif tag == "tr":
            self.row = []
        elif tag in ("td", "th") and self.in_table:
            self.cell = []
        elif tag in ("h1", "h2", "h3", "h4", "p", "li", "summary", "blockquote"):
            self.flush()
            self.mode = tag

    def handle_endtag(self, tag):
        if not self.in_body or not self.stack or tag in VOID:
            return
        # pop to matching tag
        while self.stack:
            t, sk = self.stack.pop()
            if sk:
                self.skip -= 1
            if t == tag:
                break
        if self.skip:
            return
        if tag in ("td", "th") and self.cell is not None:
            self.row.append(clean(" ".join(self.cell)))
            self.cell = None
        elif tag == "tr":
            self.rows.append(self.row)
        elif tag == "table":
            self.in_table = False
            if self.rows:
                width = max(len(r) for r in self.rows)
                rows = [r + [""] * (width - len(r)) for r in self.rows]
                lines = ["| " + " | ".join(rows[0]) + " |", "| " + " | ".join(["---"] * width) + " |"]
                lines += ["| " + " | ".join(r) + " |" for r in rows[1:]]
                self.out.append("\n".join(lines))
        elif tag == self.mode:
            self.flush()

    def handle_data(self, data):
        if not self.in_body or self.skip:
            return
        if self.cell is not None:
            self.cell.append(data)
        elif self.mode:
            self.buf.append(data)

    def flush(self):
        text = clean("".join(self.buf))
        self.buf = []
        mode, self.mode = self.mode, None
        if not text:
            return
        if mode == "h1":
            self.h1 = text
        elif mode == "h2":
            self.out.append("### " + text)
        elif mode in ("h3", "summary"):
            self.out.append("#### " + text)
        elif mode == "h4":
            self.out.append("##### " + text)
        elif mode == "li":
            if self.out and self.out[-1].startswith("- "):
                self.out[-1] += "\n- " + text
            else:
                self.out.append("- " + text)
        else:
            self.out.append(text)


def clean(s):
    s = html.unescape(s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def dates(src):
    pub = mod = None
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', src, re.S):
        try:
            data = json.loads(block)
        except ValueError:
            continue
        nodes = data.get("@graph", [data]) if isinstance(data, dict) else data
        for n in nodes:
            if isinstance(n, dict) and n.get("datePublished"):
                pub = pub or n["datePublished"][:10]
                mod = mod or (n.get("dateModified") or "")[:10]
    return pub, mod


def section(path):
    path = Path(path)
    src = path.read_text()
    url = SITE + "/" + str(path.parent.relative_to("dist")).strip(".") + "/"
    url = url.replace("//", "/").replace("https:/", "https://")
    p = Md()
    p.feed(src)
    p.flush()
    pub, mod = dates(src)
    head = [f"## {p.h1}", "", f"Source: {url}"]
    if pub:
        head.append(f"Published: {pub}" + (f"  ·  Updated: {mod}" if mod and mod != pub else ""))
    body = [b for b in p.out if b]
    while body and body[-1] in ("### Keep reading", "### Related reading"):
        body.pop()
    # The page's "Sources" heading becomes a list of link texts; keep as is.
    return "\n".join(head) + "\n\n" + "\n\n".join(body) + "\n"


def check():
    full = Path("dist/llms-full.txt").read_text()
    missing = []
    for d in ("blog", "compare"):
        for p in sorted(Path("dist", d).glob("*/index.html")):
            url = f"{SITE}/{d}/{p.parent.name}/"
            if f"Source: {url}" not in full:
                missing.append(url)
    print("\n".join(missing) or "llms-full.txt covers every /blog/ and /compare/ page")
    return 1 if missing else 0


if __name__ == "__main__":
    if sys.argv[1:] == ["--check"]:
        sys.exit(check())
    for a in sys.argv[1:]:
        sys.stdout.write(section(a))

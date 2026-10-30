"""Link every sold product and legal page from the footer, and keep es/it CTAs on their own /trial/ page."""
import os, re, sys
root = sys.argv[1]
LOCALE = re.compile(r"^(es|it|ru|fr|de)(/|$)")
TERMS = {"": "Terms", "es": "Términos", "it": "Termini", "ru": "Условия"}
LOCAL_TRIAL = {"es", "it"}
CTA = re.compile(r'(<a\b[^>]*\bhref=")/trial/(["#?])')
ARIA = re.compile(r'(<a data-select="aria" href="(/(?:es|it|ru)/|/)ai-receptionist/">Daviana Aria</a>)')
PRIVACY = re.compile(r'(<span>© 2026 Daviana · <a href="/privacy/"([^>]*)>[^<]*</a>)(</span>)')
COL = '      <a href="/privacy/">Privacy</a>'
CALC = '<a href="/compare/">Compare software</a></div>'
BASE = re.compile(r'(<div class="foot-base">© 2026 Daviana · [^<]*)(</div>)')
done = []
for dp, _, fs in os.walk(root):
    if "index.html" not in fs:
        continue
    rel = os.path.relpath(dp, root)
    m = LOCALE.match(rel) if rel != "." else None
    lang = m.group(1) if m else ""
    if lang in ("fr", "de"):
        continue
    p = os.path.join(dp, "index.html")
    h = old = open(p, encoding="utf-8").read()
    if 'bar/">Daviana Bar</a><a href' not in h:
        h = ARIA.sub(lambda a: a.group(1) + f'<a href="{a.group(2)}bar/">Daviana Bar</a><a href="{a.group(2)}performance/">Daviana Performance</a>', h)
    if 'href="/terms/"' not in h and rel != "terms":
        h = PRIVACY.sub(lambda t: f'{t.group(1)} · <a href="/terms/"{t.group(2)}>{TERMS[lang]}</a>{t.group(3)}', h)
        h = h.replace(COL, COL + '\n      <a href="/terms/">Terms</a>')
        h = BASE.sub(r'\1 · <a href="/privacy/">Privacy</a> · <a href="/terms/">Terms</a>\2', h)
    if not lang and 'Questions</a></div>' not in h:
        h = h.replace(CALC, '<a href="/compare/">Compare software</a><a href="/faq/">Questions</a></div>')
    if lang in LOCAL_TRIAL:
        h = CTA.sub(lambda c: f"{c.group(1)}/{lang}/trial/{c.group(2)}", h)
    if h != old:
        open(p, "w", encoding="utf-8").write(h)
        done.append(rel)
print(len(done), "pages changed")

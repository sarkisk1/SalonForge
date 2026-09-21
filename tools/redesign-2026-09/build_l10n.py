#!/usr/bin/env python3
"""Bring the Italian, Spanish and Russian pages onto the 2026-09 redesign.

Home pages: the new English home, translated statically (crawlable HTML, not
the in-browser nav translation) from assets/translations.js plus EXTRA below.
Product pages: their existing translated body, moved into the new header/footer
shell - the same operation the English product pages went through.
"""
import re, json, html, subprocess, pathlib, sys

REPO = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parents[2]
DIST = REPO / "dist"
BASE = "origin/main"
ORIGIN = "https://daviana.app"
LANGS = ["it", "es", "ru"]
PRODUCT_PAGES = ["diary", "colorlab", "ai-receptionist", "bar", "performance", "trial"]

EXTRA = {
    "Booking Software": {"it": "Software di prenotazione", "es": "Software de reservas", "ru": "Система записи"},
    "AI Reception": {"it": "Reception AI", "es": "Recepción con IA", "ru": "ИИ-администратор"},
    "Other Software": {"it": "Altri strumenti", "es": "Otras herramientas", "ru": "Другие инструменты"},
    "Yes. Book a guided demo to see the diary, colour tools and receptionist in action. You can also try Aria’s live call demonstration.": {
        "it": "Sì. Prenota una demo guidata per vedere l’agenda, gli strumenti colore e la receptionist in azione. Puoi anche provare la dimostrazione dal vivo di Aria al telefono.",
        "es": "Sí. Reserva una demo guiada para ver la agenda, las herramientas de color y la recepcionista en acción. También puedes probar la demostración de llamada en directo de Aria.",
        "ru": "Да. Запишитесь на демонстрацию, чтобы увидеть расписание, инструменты для окрашивания и администратора в работе. Также можно попробовать живой демонстрационный звонок Aria."},
    "Main navigation": {"it": "Navigazione principale", "es": "Navegación principal", "ru": "Основная навигация"},
    "Language": {"it": "Lingua", "es": "Idioma", "ru": "Язык"},
    "Menu": {"it": "Menu", "es": "Menú", "ru": "Меню"},
}
HOME_META = {
    "it": ("Daviana — software per saloni: prenotazioni, colore e telefono",
           "Software per parrucchieri nato dentro saloni veri: Daviana Booking per agenda e cassa, ColorLab per le formule colore calcolate al grammo e Aria, la receptionist AI che risponde al telefono. Nessuna commissione sulle prenotazioni."),
    "es": ("Daviana — software para salones: reservas, color y teléfono",
           "Software de peluquería creado dentro de salones reales: Daviana Booking para la agenda y la caja, ColorLab para fórmulas de color calculadas al gramo y Aria, la recepcionista con IA que atiende el teléfono. Sin comisiones por reserva."),
    "ru": ("Daviana — программа для салонов: запись, окрашивание и телефон",
           "Программа для салонов красоты, созданная в работающих салонах: Daviana Booking для расписания и кассы, ColorLab для формул окрашивания с расчётом до грамма и Aria — ИИ-администратор, отвечающий на звонки. Без комиссии за записи."),
}


def git_show(rel):
    return subprocess.run(["git", "show", f"{BASE}:{rel}"], cwd=REPO, capture_output=True, text=True, check=True).stdout


def load_dict():
    raw = (DIST / "assets/translations.js").read_text()
    d = {}
    for m in re.finditer(r"(?:DAVIANA_TRANSLATIONS\s*=|Object\.assign\(window\.DAVIANA_TRANSLATIONS,)\s*(\{)", raw):
        o, _ = json.JSONDecoder().raw_decode(raw[m.start(1):])
        d.update(o)
    d.update(EXTRA)
    return d


D = None


def tr(text, lang):
    v = D.get(text.strip(), {}).get(lang)
    return text.replace(text.strip(), v) if v else text


def translate_html(s, lang):
    """Translate text nodes and a few human-facing attributes; leave script/style alone."""
    parts = re.split(r"(<script\b.*?</script>|<style\b.*?</style>)", s, flags=re.S)
    for i in range(0, len(parts), 2):
        p = parts[i]
        p = re.sub(r">([^<]+)<", lambda m: ">" + html.escape(tr(html.unescape(m.group(1)), lang), quote=False) + "<", p)
        p = re.sub(r'\b(aria-label|alt|title)="([^"]+)"',
                   lambda m: f'{m.group(1)}="{html.escape(tr(html.unescape(m.group(2)), lang))}"', p)
        parts[i] = p
    return "".join(parts)


def localise_links(s, lang):
    def fix(m):
        v = m.group(1)
        path, sep, frag = v.partition("#")
        if frag == "call-it":        # Aria's live call demo exists in English only
            return m.group(0)
        if path.startswith("/") and (DIST / lang / path.strip("/") / "index.html").exists() and not path.startswith(f"/{lang}/"):
            path = f"/{lang}{path}" if path != "/" else f"/{lang}/"
            return f'href="{path}{sep}{frag}"'
        return m.group(0)
    return re.sub(r'href="(/[^"]*)"', fix, s)


def press_language(s, lang):
    s = re.sub(r'(<button aria-pressed=")(?:true|false)(" data-language="([a-z]+)")',
               lambda m: m.group(1) + ("true" if m.group(3) == lang else "false") + m.group(2), s)
    return s


def shell(lang, part, source):
    m = re.search(rf'<div data-site-shell="{part}".*?</template></div>', source, re.S)
    assert m, part
    return press_language(localise_links(translate_html(m.group(0), lang), lang), lang)


def build_home(lang):
    en = (DIST / "index.html").read_text()
    old = git_show(f"dist/{lang}/index.html")
    head, body = en[: en.index("<body")], en[en.index("<body"):]
    body = press_language(localise_links(translate_html(body, lang), lang), lang)

    title, desc = HOME_META[lang]
    u = f"{ORIGIN}/{lang}/"
    head = re.sub(r"<html[^>]*>", f'<html lang="{lang}" data-page="index" data-static-lang="{lang}">', head, 1)
    head = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", head, flags=re.S)
    for pat, val in [(r'(<meta name="description" content=")[^"]*', desc), (r'(<meta property="og:title" content=")[^"]*', title),
                     (r'(<meta property="og:description" content=")[^"]*', desc), (r'(<meta property="og:image:alt" content=")[^"]*', title),
                     (r'(<link rel="canonical" href=")[^"]*', u), (r'(<meta property="og:url" content=")[^"]*', u)]:
        head, n = re.subn(pat, lambda m, val=val: m.group(1) + val, head)
        assert n == 1, (lang, pat)
    loc = re.search(r'<meta property="og:locale"[^>]*>', old)
    if loc and "og:locale" not in head:
        head = head.replace('<meta property="og:type"', loc.group(0) + '\n<meta property="og:type"', 1)

    def ld(m):
        def walk(o):
            if isinstance(o, dict):
                return {k: (lang if k == "inLanguage" else (u if k == "url" and v == ORIGIN + "/" and o.get("@type") == "WebSite" else walk(v))) for k, v in o.items()}
            if isinstance(o, list):
                return [walk(x) for x in o]
            return tr(o, lang) if isinstance(o, str) else o
        return '<script type="application/ld+json">' + json.dumps(walk(json.loads(m.group(1))), ensure_ascii=False) + "</script>"
    head = re.sub(r'<script type="application/ld\+json">(.*?)</script>', ld, head, flags=re.S)
    (DIST / lang / "index.html").write_text(head + body)
    left = [t for t in re.findall(r">([^<]+)<", re.sub(r"<(script|style)\b.*?</\1>", "", body, flags=re.S))
            if re.search(r"[A-Za-z]{4}", t) and html.unescape(t).strip() in D]
    print(f"/{lang}/ home: {len(left)} dictionary strings left in English")


def build_product(lang, page):
    rel = f"dist/{lang}/{page}/index.html"
    if not (DIST / lang / page / "index.html").exists():
        return
    old = git_show(rel)
    en = (DIST / "colorlab/index.html").read_text()      # any inner page carries the inner-page shell
    head, body = old[: old.index("<body")], old[old.index("<body"):]

    body, n = re.subn(r'<header id="hd">.*?</header>',
                      lambda m: shell(lang, "header", en) + '<div class="locale-notice" hidden id="locale-notice" role="status"></div>', body, 1, flags=re.S)
    assert n == 1, rel
    i = body.rfind("<footer")
    j = body.index("</footer>", i) + len("</footer>")
    body = body[:i] + shell(lang, "footer", en) + body[j:]
    body = re.sub(r"<script>(?:(?!</script>).)*#hd \.nav.*?</script>\s*", "", body, flags=re.S)
    body = body.replace("hd.classList.toggle", "hd&&hd.classList.toggle")
    body = re.sub(r'href="/#(?:system|connect|proof|everything)"', f'href="/{lang}/"', body)  # old-home anchors

    extra = re.findall(r"<style>body\{padding-top:0!important\}.*?</style>", en, re.S)[0]
    head = re.sub(r"<html[^>]*>", f'<html lang="{lang}" data-page="{page}" data-static-lang="{lang}">', head, 1)
    head = head.replace("</head>", extra + '<link href="/assets/mobile.css?v=align18" rel="stylesheet"/>'
                        '<script defer src="/assets/translations.js?v=1"></script><script defer src="/assets/site.js?v=2"></script>\n</head>')
    (DIST / lang / page / "index.html").write_text(head + body)
    print(f"/{lang}/{page}/ reshelled")


if __name__ == "__main__":
    D = load_dict()
    for lang in LANGS:
        build_home(lang)
        for page in PRODUCT_PAGES:
            build_product(lang, page)

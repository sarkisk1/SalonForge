"""Add a 'Guides' footer column linking the comparison and guide pages on every English page."""
import os, re, sys
root = sys.argv[1]
LINKS = [
    ("/blog/best-salon-software-uk/", "Best salon software UK"),
    ("/blog/best-ai-receptionist-for-salons-uk/", "Best AI receptionists for salons"),
    ("/blog/best-hair-colour-management-software/", "Best hair colour software"),
    ("/blog/best-booking-system-nail-salon-uk/", "Best nail salon booking systems"),
    ("/blog/best-booking-system-beauty-salon-uk/", "Best beauty salon booking systems"),
    ("/blog/how-much-does-salon-software-cost-uk/", "Salon software costs"),
    ("/blog/salon-no-show-policy/", "No-show policy template"),
    ("/compare/phorest-alternatives/", "Phorest alternatives"),
    ("/compare/booksy-alternatives/", "Booksy alternatives"),
    ("/compare/treatwell-alternatives/", "Treatwell alternatives"),
    ("/compare/daviana-vs-zenoti/", "Zenoti alternative"),
    ("/compare/daviana-vs-vish/", "Vish alternative"),
]
LOCALE = re.compile(r"^(es|it|ru|fr|de)(/|$)")
NEW_ANCHOR = '<a href="/compare/">Compare software</a></div>'
OLD_ANCHOR = re.compile(r'(<a href="/compare/">Compare</a>.*?</div>)', re.S)
# Last stylesheet in the footer shadow root, so it wins over the earlier !important layers.
GUIDES_CSS = ('<style data-footer-guides="true">'
    '.footer-grid{grid-template-columns:1.1fr 1fr 1fr 1.25fr 1fr!important}'
    '@media(max-width:900px){.footer-grid{grid-template-columns:repeat(3,minmax(0,1fr))!important}'
    '.footer-guides{order:9;grid-column:1/-1!important;columns:2;column-gap:20px}'
    '.footer-guides strong{column-span:all}.footer-guides a{break-inside:avoid}}'
    '</style>')
new_col = '<div class="footer-col footer-guides"><strong>Guides</strong>' + "".join(f'<a href="{h}">{t}</a>' for h, t in LINKS) + "</div>"
old_col = ' <div class="cols">' + "".join(f' <a href="{h}">{t}</a>' for h, t in LINKS) + " </div>"
done = []
for dp, _, fs in os.walk(root):
    rel = os.path.relpath(dp, root)
    if rel != "." and LOCALE.match(rel):
        continue
    if "index.html" not in fs:
        continue
    p = os.path.join(dp, "index.html")
    h = open(p, encoding="utf-8").read()
    if "<strong>Guides</strong>" in h or "/blog/best-salon-software-uk/\">Best salon software UK" in h:
        continue
    if NEW_ANCHOR in h and h.find("</template>", h.find("<footer")) > 0:
        h = h.replace(NEW_ANCHOR, NEW_ANCHOR + new_col, 1)
        j = h.find("</template>", h.find("<footer"))
        h = h[:j] + GUIDES_CSS + h[j:]
    elif "<footer" in h and OLD_ANCHOR.search(h[h.find("<footer"):]):
        i = h.find("<footer")
        h = h[:i] + OLD_ANCHOR.sub(lambda m: m.group(1) + old_col, h[i:], count=1)
    else:
        continue
    open(p, "w", encoding="utf-8").write(h)
    done.append(rel)
print(len(done)); print(" ".join(sorted(done)))

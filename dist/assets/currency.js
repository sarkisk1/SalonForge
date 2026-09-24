/* Show Daviana's own prices in euros to visitors in Europe (EU, EEA,
   Switzerland and euro-using microstates). Same figures, € instead of £.
   Country comes from Cloudflare (/cdn-cgi/trace, same origin, no cookie).
   Only our own list prices are swapped (£80, £60, £220) plus the live total
   on /pricing/. Not loaded on /compare/ pages: those set our prices against
   competitors' UK £ prices, and a mixed €/£ table would mislead. Also
   on /pricing/. Worked examples, calculators and competitor prices stay £.
   Test with ?currency=eur or ?currency=gbp. */
(function () {
  var EU = 'AT BE BG HR CY CZ DK EE FI FR DE GR HU IE IT LV LT LU MT NL PL PT RO SK SI ES SE IS LI NO CH AD MC SM VA ME XK'.split(' ');
  var OWN = /£(80|60|220)(?![\d.,]*\d)/g;
  var KEY = 'dv_cur';

  function swap(root) {
    var w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
      acceptNode: function (n) {
        var p = n.parentNode && n.parentNode.nodeName;
        return p === 'SCRIPT' || p === 'STYLE' || n.nodeValue.indexOf('£') < 0 ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT;
      }
    });
    var n;
    while ((n = w.nextNode())) {
      var inTotal = n.parentNode.closest && n.parentNode.closest('#pr-total-n');
      var v = inTotal ? n.nodeValue.replace(/£/g, '€') : n.nodeValue.replace(OWN, '€$1');
      if (v !== n.nodeValue) n.nodeValue = v;
    }
  }

  function apply() {
    document.documentElement.setAttribute('data-currency', 'eur');
    swap(document.body);
    new MutationObserver(function (ms) {
      ms.forEach(function (m) {
        if (m.type === 'characterData') swap(m.target.parentNode || document.body);
        else m.addedNodes.forEach(function (a) { swap(a.nodeType === 3 ? a.parentNode : a); });
      });
    }).observe(document.body, { childList: true, subtree: true, characterData: true });
  }

  function decide(cur) {
    try { sessionStorage.setItem(KEY, cur); } catch (e) {}
    if (cur !== 'eur') return;
    if (document.body) apply(); else document.addEventListener('DOMContentLoaded', apply);
  }

  var q = (location.search.match(/[?&]currency=(eur|gbp)/i) || [])[1];
  if (q) return decide(q.toLowerCase());
  var cached = null;
  try { cached = sessionStorage.getItem(KEY); } catch (e) {}
  if (cached) return decide(cached);
  fetch('/cdn-cgi/trace').then(function (r) { return r.text(); }).then(function (t) {
    var loc = (t.match(/^loc=([A-Z]{2})$/m) || [])[1];
    decide(EU.indexOf(loc) >= 0 ? 'eur' : 'gbp');
  }).catch(function () {});
})();

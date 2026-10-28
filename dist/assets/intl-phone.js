/*!
 * Daviana trial phone boxes — 28 Oct 2026.
 *
 * The /trial pages only had a bare UK-style box, so an Italian owner typing
 * "333 123 4567" was read as a UK number and never got the code (Gennaro,
 * 28 Oct). Every phone box marked data-sf-phone now gets a country-code picker
 * (the page's own country by default: UK on the English page, Italy on
 * /it/, Spain on /es/, France on /fr/, Germany on /de/) and the page reads the number through sfPhone.value(),
 * which always gives the server a full international number (+39 333…).
 *
 * Typing or pasting "+39…" / "0039…" still works: the picker follows it.
 * The country table (dial code, national trunk prefix, shortest and longest
 * national number) is generated from libphonenumber-js 1.12.10 metadata.
 * Country names come from the browser in the page's own language.
 */
(function () {
  var RAW = 'AC:247::5:6,AD:376::6:9,AE:971:0:5:12,AF:93:0:9:9,AG:1:1:10:10,AI:1:1:10:10,AL:355:0:6:9,AM:374:0:8:8,AO:244::9:9,AR:54:0:10:11,AS:1:1:10:10,AT:43:0:4:13,AU:61:0:5:12,AW:297::7:7,AX:358:0:5:12,AZ:994:0:9:9,BA:387:0:8:9,BB:1:1:10:10,BD:880:0:6:10,BE:32:0:8:9,BF:226::8:8,BG:359:0:6:12,BH:973::8:8,BI:257::8:8,BJ:229::8:10,BL:590:0:9:9,BM:1:1:10:10,BN:673::7:7,BO:591:0:8:9,BQ:599::7:7,BR:55:0:8:11,BS:1:1:10:10,BT:975::7:8,BW:267::7:10,BY:375:8:6:11,BZ:501::7:11,CA:1:1:7:10,CC:61:0:6:12,CD:243:0:7:10,CF:236::8:8,CG:242::9:9,CH:41:0:9:12,CI:225::10:10,CK:682::5:5,CL:56::9:11,CM:237::8:9,CN:86:0:7:12,CO:57:0:8:11,CR:506::8:10,CU:53:0:6:10,CV:238::7:7,CW:599::7:8,CX:61:0:6:12,CY:357::8:8,CZ:420::9:12,DE:49:0:4:15,DJ:253::8:8,DK:45::8:8,DM:1:1:10:10,DO:1:1:10:10,DZ:213:0:8:9,EC:593:0:8:11,EE:372::7:10,EG:20:0:8:10,EH:212:0:9:9,ER:291:0:7:7,ES:34::9:9,ET:251:0:9:9,FI:358:0:5:12,FJ:679::7:11,FK:500::5:5,FM:691::7:7,FO:298::6:6,FR:33:0:9:9,GA:241::7:8,GB:44:0:7:10,GD:1:1:10:10,GE:995:0:9:9,GF:594:0:9:9,GG:44:0:7:10,GH:233:0:8:9,GI:350::8:8,GL:299::6:6,GM:220::7:7,GN:224::8:9,GP:590:0:9:9,GQ:240::9:9,GR:30::10:12,GT:502::8:11,GU:1:1:10:10,GW:245::7:9,GY:592::7:7,HK:852::5:11,HN:504::8:11,HR:385:0:7:9,HT:509::8:8,HU:36:06:8:9,ID:62:0:7:17,IE:353:0:7:10,IL:972:0:7:12,IM:44:0:10:10,IN:91:0:8:13,IO:246::7:7,IQ:964:0:8:10,IR:98:0:4:10,IS:354::7:9,IT:39::6:12,JE:44:0:10:10,JM:1:1:10:10,JO:962:0:8:9,JP:81:0:8:17,KE:254:0:7:10,KG:996:0:9:10,KH:855:0:8:10,KI:686:0:5:8,KM:269::7:7,KN:1:1:10:10,KP:850:0:8:10,KR:82:0:5:14,KW:965::7:8,KY:1:1:10:10,KZ:7:8:10:14,LA:856:0:8:10,LB:961:0:7:8,LC:1:1:10:10,LI:423:0:7:9,LK:94:0:9:9,LR:231:0:7:9,LS:266::8:8,LT:370:0:8:8,LU:352::4:11,LV:371::8:8,LY:218:0:9:9,MA:212:0:9:9,MC:377:0:8:9,MD:373:0:8:8,ME:382:0:8:9,MF:590:0:9:9,MG:261:0:9:9,MH:692:1:7:7,MK:389:0:8:8,ML:223::8:8,MM:95:0:6:10,MN:976:0:8:10,MO:853::7:8,MP:1:1:10:10,MQ:596:0:9:9,MR:222::8:8,MS:1:1:10:10,MT:356::8:8,MU:230::7:10,MV:960::7:10,MW:265:0:7:9,MX:52::10:10,MY:60:0:8:10,MZ:258::8:9,NA:264:0:8:9,NC:687::6:6,NE:227::8:8,NF:672::6:6,NG:234:0:10:14,NI:505::8:8,NL:31:0:5:11,NO:47::5:8,NP:977:0:8:11,NR:674::7:7,NU:683::4:7,NZ:64:0:5:10,OM:968::7:9,PA:507::7:11,PE:51:0:8:9,PF:689::6:9,PG:675::7:8,PH:63:0:6:13,PK:92:0:8:12,PL:48::6:10,PM:508:0:6:9,PR:1:1:10:10,PS:970:0:8:10,PT:351::9:9,PW:680::7:7,PY:595:0:6:11,QA:974::7:11,RE:262:0:9:9,RO:40:0:6:9,RS:381:0:6:12,RU:7:8:10:14,RW:250:0:8:9,SA:966:0:9:10,SB:677::5:7,SC:248::7:7,SD:249:0:9:9,SE:46:0:6:12,SG:65::8:11,SH:290::4:5,SI:386:0:5:8,SJ:47::5:8,SK:421:0:6:9,SL:232:0:8:8,SM:378::8:10,SN:221::9:9,SO:252:0:6:9,SR:597::6:7,SS:211:0:9:9,ST:239::7:7,SV:503::7:11,SX:1:1:10:10,SY:963:0:8:9,SZ:268::8:9,TA:290::4:4,TC:1:1:10:10,TD:235::8:8,TG:228::8:8,TH:66:0:8:13,TJ:992::9:9,TK:690::4:7,TL:670::7:8,TM:993:8:8:8,TN:216::8:8,TO:676::5:7,TR:90:0:7:13,TT:1:1:10:10,TV:688::5:7,TW:886:0:7:11,TZ:255:0:9:9,UA:380:0:9:10,UG:256:0:9:9,US:1:1:10:10,UY:598:0:6:13,UZ:998::9:9,VA:39::6:12,VC:1:1:10:10,VE:58:0:10:10,VG:1:1:10:10,VI:1:1:10:10,VN:84:0:7:10,VU:678::5:7,WF:681::6:9,WS:685::5:10,XK:383:0:8:12,YE:967:0:7:9,YT:262:0:9:9,ZA:27:0:5:10,ZM:260:0:9:9,ZW:263:0:5:10';
  var C = {};
  RAW.split(',').forEach(function (r) {
    var p = r.split(':');
    C[p[0]] = {iso: p[0], dial: p[1], np: p[2], min: +p[3], max: +p[4]};
  });
  // Where one dial code is shared, the country people mean by it.
  var MAIN = {'1': 'US', '7': 'RU', '39': 'IT', '44': 'GB', '47': 'NO', '61': 'AU', '212': 'MA', '262': 'RE', '290': 'SH', '358': 'FI', '590': 'GP', '599': 'CW'};
  var TOP = ['GB', 'IE', 'IT', 'ES', 'FR', 'DE', 'PT', 'NL', 'BE', 'CH', 'US', 'CA', 'AU', 'NZ', 'AE'];
  var MOBILE_EG = {GB: '07700 900123', IE: '085 123 4567', IT: '333 123 4567', ES: '612 34 56 78', FR: '06 12 34 56 78',
    DE: '01512 3456789', PT: '912 345 678', NL: '06 12345678', BE: '0470 12 34 56', CH: '078 123 45 67',
    US: '(415) 555-0123', CA: '(416) 555-0123', AU: '0412 345 678', NZ: '021 123 4567', AE: '050 123 4567'};
  var LANG = (document.documentElement.lang || 'en').slice(0, 2);
  // 28 Oct 2026 (Sarkis): the Italian page starts on Italy, not the UK.
  var HOME = {it: 'IT', es: 'ES', fr: 'FR', de: 'DE'}[LANG] || 'GB';
  TOP = [HOME].concat(TOP.filter(function (iso) { return iso !== HOME; }));
  var MSG = {
    en: ['Country code', 'Please check this number. It looks too short or too long for the country picked.'],
    it: ['Prefisso internazionale', 'Controlla il numero: sembra troppo corto o troppo lungo per il paese scelto.'],
    es: ['Prefijo del país', 'Revisa el número: parece demasiado corto o largo para el país elegido.'],
    fr: ['Indicatif du pays', 'Vérifiez le numéro : il semble trop court ou trop long pour le pays choisi.'],
    de: ['Ländervorwahl', 'Bitte prüfen Sie die Nummer: Sie ist für das gewählte Land zu kurz oder zu lang.']
  }[LANG] || null;
  if (!MSG) MSG = ['Country code', 'Please check this number. It looks too short or too long for the country picked.'];

  var names = null;
  try { names = new Intl.DisplayNames([LANG, 'en'], {type: 'region'}); } catch (e) {}
  function nameOf(iso) { try { return (names && names.of(iso)) || iso; } catch (e) { return iso; } }
  function flag(iso) {
    try { return String.fromCodePoint(127397 + iso.charCodeAt(0), 127397 + iso.charCodeAt(1)); } catch (e) { return ''; }
  }
  function digits(s) { return String(s || '').replace(/\D/g, ''); }

  // "+393331234567" -> {iso: 'IT', national: '3331234567'}. Longest dial code wins.
  function split(e164, prefer) {
    var d = digits(e164);
    for (var n = 3; n >= 1; n--) {
      var dial = d.slice(0, n), iso = null;
      if (prefer && C[prefer] && C[prefer].dial === dial) iso = prefer;
      else if (MAIN[dial]) iso = MAIN[dial];
      else for (var k in C) if (C[k].dial === dial) { iso = k; break; }
      if (iso) return {iso: iso, national: d.slice(n)};
    }
    return null;
  }

  function isIntl(raw) { return /^\s*(\+|00)/.test(raw); }

  // The full international number for what is in the box, or '' when empty.
  function value(input) {
    var raw = String(input.value || '').trim();
    if (!raw) return '';
    if (isIntl(raw)) return '+' + digits(raw).replace(/^00/, '');
    var c = C[(input.__sfSel && input.__sfSel.value) || HOME] || C[HOME];
    var nat = digits(raw);
    // Someone picked Italy and still typed the 39 in front.
    if (nat.indexOf(c.dial) === 0 && nat.length - c.dial.length >= c.min && nat.length > c.max) nat = nat.slice(c.dial.length);
    if (c.np && nat.indexOf(c.np) === 0 && nat.length - c.np.length >= c.min) nat = nat.slice(c.np.length);
    return '+' + c.dial + nat;
  }

  function plausible(input) {
    var v = value(input);
    if (!v) return true;
    var s = split(v, input.__sfSel && input.__sfSel.value);
    if (!s || !C[s.iso]) return /^\+[1-9]\d{7,14}$/.test(v);
    return s.national.length >= C[s.iso].min && s.national.length <= C[s.iso].max && v.length <= 16;
  }

  function choose(input, iso) {
    var sel = input.__sfSel;
    if (!sel || !C[iso]) return;
    sel.value = iso;
    paint(input);
  }

  function paint(input) {
    var sel = input.__sfSel, c = C[sel.value] || C[HOME];
    input.__sfFace.textContent = flag(c.iso) + ' +' + c.dial;
    if (input.getAttribute('data-sf-phone') === 'mobile') input.placeholder = MOBILE_EG[c.iso] || '';
    else input.placeholder = c.iso === HOME ? (input.__sfUkEg || '') : '';
  }

  // A stored "+39…" back into the boxes: pick the country, show the local number.
  function set(input, e164) {
    if (!input || !e164 || input.value) return;
    var s = isIntl(e164) && split(e164, input.__sfSel && input.__sfSel.value);
    if (!s || !input.__sfSel) { input.value = e164; return; }
    choose(input, s.iso);
    var c = C[s.iso];
    input.value = (c.np && c.np.length === 1 ? c.np : '') + s.national;
  }

  function check(input) {
    if (!input.setCustomValidity) return;
    input.setCustomValidity(plausible(input) ? '' : MSG[1]);
  }

  // After a "+39 …" is typed or pasted, move the code into the picker.
  function absorb(input) {
    var raw = String(input.value || '').trim();
    if (!isIntl(raw)) return;
    var s = split(raw, input.__sfSel.value);
    if (!s || !C[s.iso]) return;
    choose(input, s.iso);
    var c = C[s.iso];
    input.value = (c.np && c.np.length === 1 ? c.np : '') + s.national;
  }

  var css = '.sf-tel{display:flex;gap:8px;align-items:stretch;min-width:0}.sf-tel>input{flex:1;min-width:0}' +
    '.sf-cc{position:relative;flex:none;display:flex;align-items:center;gap:6px;padding:0 12px;border:1px solid var(--line,#ddd);' +
    'border-radius:10px;background:var(--bg,#fff);font-size:1rem;white-space:nowrap;cursor:pointer;color:var(--ink,inherit)}' +
    '.sf-cc:after{content:"";width:7px;height:7px;border-right:1.5px solid currentColor;border-bottom:1.5px solid currentColor;transform:translateY(-2px) rotate(45deg);opacity:.55}' +
    '.sf-cc select{position:absolute;inset:0;width:100%;height:100%;opacity:0;cursor:pointer;font-size:16px}' +
    '.sf-cc:focus-within{outline:2px solid var(--g,#c96f4a);outline-offset:1px}';

  function attach(input) {
    if (!input || input.__sfSel) return;
    if (!document.getElementById('sf-tel-css')) {
      var st = document.createElement('style'); st.id = 'sf-tel-css'; st.textContent = css; document.head.appendChild(st);
    }
    input.__sfUkEg = input.placeholder;
    var wrap = document.createElement('div'); wrap.className = 'sf-tel';
    var box = document.createElement('label'); box.className = 'sf-cc';
    var face = document.createElement('span'); face.setAttribute('aria-hidden', 'true');
    var sel = document.createElement('select'); sel.setAttribute('aria-label', MSG[0]);
    var list = Object.keys(C).map(function (k) { return {iso: k, name: nameOf(k)}; });
    list.sort(function (a, b) { return a.name.localeCompare(b.name, LANG); });
    function opt(o) { var e = document.createElement('option'); e.value = o.iso; e.textContent = flag(o.iso) + ' ' + o.name + ' (+' + C[o.iso].dial + ')'; return e; }
    TOP.forEach(function (iso) { sel.appendChild(opt({iso: iso, name: nameOf(iso)})); });
    var hr = document.createElement('option'); hr.disabled = true; hr.textContent = '──────────'; sel.appendChild(hr);
    list.forEach(function (o) { if (TOP.indexOf(o.iso) === -1) sel.appendChild(opt(o)); });
    sel.value = HOME;
    box.appendChild(face); box.appendChild(sel);
    input.parentNode.insertBefore(wrap, input);
    wrap.appendChild(box); wrap.appendChild(input);
    input.__sfSel = sel; input.__sfFace = face;
    paint(input);
    sel.addEventListener('change', function () {
      sel.__sfPicked = true;
      paint(input); check(input);
      // The salon's own number is almost always in the same country as the owner's mobile.
      if (input.getAttribute('data-sf-phone') === 'mobile') {
        document.querySelectorAll('input[data-sf-phone="landline"]').forEach(function (o) {
          if (o.__sfSel && !o.__sfSel.__sfPicked) { o.__sfSel.value = sel.value; paint(o); }
        });
      }
    });
    input.addEventListener('input', function () { input.setCustomValidity && input.setCustomValidity(''); });
    input.addEventListener('blur', function () { absorb(input); check(input); });
    input.addEventListener('change', function () { absorb(input); check(input); });
  }

  function init() { document.querySelectorAll('input[data-sf-phone]').forEach(attach); }
  window.sfPhone = {value: value, set: set, attach: attach, plausible: plausible, _split: split};
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();

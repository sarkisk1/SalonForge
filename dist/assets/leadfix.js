/*!
 * Daviana lead fixes, 24 Sep 2026.
 *
 * Gennaro's funnel export (25 Aug to 24 Sep) showed signups lost before or at
 * the worker. Two emails were typed as "gamil.com" / "gmai.com", so the opt-in
 * email never arrived. Mobiles typed with spaces, dashes or a local trunk "0"
 * were refused, and 5 people gave up after 38 attempts between them.
 *
 * Runs in the CAPTURE phase on document, so it goes before the page's own submit
 * handler:
 *   1. Tidies the mobile in place: strips formatting, turns 00 into +, and adds
 *      the country code for this page's language when the number is clearly a
 *      local mobile.
 *   2. Catches common email-domain typos. The first submit is held and the
 *      visitor gets a one-tap fix. Submitting again keeps what they typed.
 *      Nobody is ever blocked twice.
 * Fails OPEN: any error here lets the page's handler run untouched.
 */
(function () {
  var LANG = (location.pathname.match(/^\/(es|fr|de|it)\//) || [])[1] || 'en';

  var TYPO = {
    'gamil.com': 'gmail.com', 'gmai.com': 'gmail.com', 'gmial.com': 'gmail.com',
    'gmal.com': 'gmail.com', 'gnail.com': 'gmail.com', 'gmaill.com': 'gmail.com',
    'gmail.co': 'gmail.com', 'gmail.con': 'gmail.com', 'gmail.cm': 'gmail.com',
    'gmail.om': 'gmail.com', 'gmali.com': 'gmail.com', 'gmsil.com': 'gmail.com',
    'hotmial.com': 'hotmail.com', 'hotmal.com': 'hotmail.com', 'hotmai.com': 'hotmail.com',
    'hotmail.con': 'hotmail.com', 'hotmil.com': 'hotmail.com', 'hotamil.com': 'hotmail.com',
    'hotmail.co': 'hotmail.co.uk', 'hotmail.co.k': 'hotmail.co.uk',
    'outlok.com': 'outlook.com', 'outloo.com': 'outlook.com', 'outlook.con': 'outlook.com',
    'yahoo.con': 'yahoo.com', 'yaho.com': 'yahoo.com', 'yahooo.com': 'yahoo.com',
    'yahoo.co.k': 'yahoo.co.uk',
    'iclod.com': 'icloud.com', 'icloud.co': 'icloud.com', 'icoud.com': 'icloud.com',
    'icluod.com': 'icloud.com', 'icloud.con': 'icloud.com',
    'libero.i': 'libero.it', 'liber.it': 'libero.it'
  };

  var MSG = {
    en: ['Did you mean ', '? Tap to fix it, or press the button again to keep what you typed.'],
    es: ['¿Querías decir ', '? Toca para corregirlo, o pulsa el botón otra vez para dejarlo como está.'],
    fr: ['Vouliez-vous dire ', ' ? Touchez pour corriger, ou appuyez à nouveau sur le bouton pour garder votre saisie.'],
    de: ['Meinten Sie ', '? Tippen zum Korrigieren, oder den Button erneut drücken, um die Eingabe zu behalten.'],
    it: ['Intendevi ', '? Tocca per correggere, oppure premi di nuovo il pulsante per lasciarlo così.']
  }[LANG];

  // Local mobile → E.164, only when the shape is unambiguous for this page.
  function tidyMobile(v) {
    var raw = (v || '').trim();
    if (!raw) return raw;
    var plus = raw.charAt(0) === '+';
    var d = raw.replace(/\D/g, '');
    if (!d) return raw;
    if (plus) return '+' + d;
    if (d.indexOf('00') === 0) return '+' + d.slice(2);
    if (LANG === 'en') {
      if (/^07\d{9}$/.test(d)) return '+44' + d.slice(1);           // UK mobile
      if (/^08[35679]\d{7}$/.test(d)) return '+353' + d.slice(1);    // Irish mobile
      if (/^447\d{9}$/.test(d)) return '+' + d;
    } else if (LANG === 'es') {
      if (/^[67]\d{8}$/.test(d)) return '+34' + d;
      if (/^34[67]\d{8}$/.test(d)) return '+' + d;
    } else if (LANG === 'fr') {
      if (/^0[67]\d{8}$/.test(d)) return '+33' + d.slice(1);
      if (/^33[67]\d{8}$/.test(d)) return '+' + d;
    } else if (LANG === 'de') {
      if (/^01[5-7]\d{7,9}$/.test(d)) return '+49' + d.slice(1);
      if (/^491[5-7]\d{7,9}$/.test(d)) return '+' + d;
    } else if (LANG === 'it') {
      if (/^3\d{8,9}$/.test(d)) return '+39' + d;
      if (/^393\d{8,9}$/.test(d)) return '+' + d;
    }
    return raw; // not sure → leave exactly as typed; the worker decides
  }

  function suggest(email) {
    var m = (email || '').trim().toLowerCase().match(/^([^@\s]+)@([^@\s]+)$/);
    if (!m) return '';
    var fix = TYPO[m[2]];
    return fix ? m[1] + '@' + fix : '';
  }

  document.addEventListener('submit', function (e) {
    try {
      var form = e.target;
      if (!form || !form.querySelector) return;
      var email = form.querySelector('#tr-email');
      var mobile = form.querySelector('#tr-mobile');
      if (!email) return;
      if (mobile) mobile.value = tidyMobile(mobile.value);

      var s = suggest(email.value);
      if (!s || form.__sfTypoShown === email.value) return;
      form.__sfTypoShown = email.value;          // second submit with the same value goes through
      e.preventDefault();
      e.stopImmediatePropagation();

      var err = document.getElementById('tr-err');
      if (!err) return;
      err.textContent = '';
      err.appendChild(document.createTextNode(MSG[0]));
      var a = document.createElement('a');
      a.href = '#';
      a.textContent = s;
      a.style.fontWeight = '700';
      a.style.textDecoration = 'underline';
      a.addEventListener('click', function (ev) {
        ev.preventDefault();
        email.value = s;
        form.__sfTypoShown = '';
        err.classList.remove('on');
        email.focus();
      });
      err.appendChild(a);
      err.appendChild(document.createTextNode(MSG[1]));
      err.classList.add('on');
      try { if (window.gtag) gtag('event', 'email_typo_suggested', { event_category: 'trial' }); } catch (_) {}
    } catch (ex) { /* fail open: the page handler runs as normal */ }
  }, true);
})();

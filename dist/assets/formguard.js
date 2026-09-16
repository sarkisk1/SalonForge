/*!
 * SalonForge form guard — 5 Sep 2026.
 *
 * Two junk submissions made Aria telephone Jerusalem landlines: "gaerh"
 * +97222207493 (3 Sep) and the Faker-generated "Littel, Dooley and Walker"
 * +97222902015 (4 Sep), which spent 145s on a recorded horoscope line and
 * raised a false "ENGAGED" alert to the team.
 *
 * This decorates the existing forms from the OUTSIDE — it does not touch their
 * handlers — so a mistake here cannot stop a real salon signing up. It adds:
 *   1. a honeypot field real people never see,
 *   2. the time the form was rendered (scripts submit instantly, humans don't),
 *   3. a Cloudflare Turnstile token.
 * and merges those three into the JSON body of any POST to the trial worker.
 *
 * Fails silent and OPEN by design: if Turnstile is blocked or slow, the form
 * still submits with an empty token and the worker decides what to do.
 */
(function () {
  var WORKER = 'salonforge-trial.long-moon-952c.workers.dev';
  var SITEKEY = '0x4AAAAAAEoUo5YIwZgZ3VcH';
  var RENDERED_AT = Date.now();
  var token = '';

  // ── 1 + 2: hidden fields on every form that talks to the worker.
  function decorate(form) {
    if (form.__sfGuarded) return;
    form.__sfGuarded = true;
    var pot = document.createElement('input');
    pot.type = 'text';
    pot.name = 'company_website_url';
    pot.tabIndex = -1;
    pot.autocomplete = 'off';
    pot.setAttribute('aria-hidden', 'true');
    // Off-screen rather than display:none — some bots skip hidden inputs.
    pot.style.cssText = 'position:absolute;left:-9999px;width:1px;height:1px;opacity:0';
    form.appendChild(pot);
  }
  // Any filled honeypot anywhere on the page condemns the submission.
  function potValue() {
    try {
      var ps = document.querySelectorAll('input[name="company_website_url"]');
      for (var i = 0; i < ps.length; i++) {
        var v = (ps[i].value || '').trim();
        if (v) return v;
      }
    } catch (e) {}
    return '';
  }
  function decorateAll() {
    var fs = document.getElementsByTagName('form');
    for (var i = 0; i < fs.length; i++) decorate(fs[i]);
  }

  // ── 3: Turnstile, rendered invisibly. Managed mode only interrupts a visitor
  //      it actively distrusts, so a real salon owner sees nothing.
  window.sfTurnstileReady = function () {
    try {
      var host = document.createElement('div');
      host.style.cssText = 'position:absolute;left:-9999px;top:-9999px';
      document.body.appendChild(host);
      window.turnstile.render(host, {
        sitekey: SITEKEY,
        callback: function (t) { token = t || ''; },
        'error-callback': function () { token = ''; },
        'expired-callback': function () { token = ''; if (window.turnstile) try { window.turnstile.reset(); } catch (e) {} }
      });
    } catch (e) { /* never block the form */ }
  };

  // ── Merge the three into any JSON POST heading for the worker.
  var origFetch = window.fetch;
  if (typeof origFetch === 'function') {
    window.fetch = function (input, init) {
      try {
        var url = typeof input === 'string' ? input : (input && input.url) || '';
        if (url.indexOf(WORKER) > -1 && init && init.method &&
            String(init.method).toUpperCase() === 'POST' && typeof init.body === 'string') {
          var b = JSON.parse(init.body);
          if (b && typeof b === 'object') {
            // Read the honeypot's REAL value — hardcoding '' would defeat it.
            // The page's own handlers build their JSON from named fields and never
            // include this one, so we have to carry it across ourselves.
            b.company_website_url = potValue();
            b.form_rendered_at = RENDERED_AT;
            b['cf-turnstile-response'] = token;
            init = Object.assign({}, init, { body: JSON.stringify(b) });
          }
        }
      } catch (e) { /* fall through with the original body */ }
      return origFetch.call(this, input, init);
    };
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', decorateAll);
  } else {
    decorateAll();
  }
})();

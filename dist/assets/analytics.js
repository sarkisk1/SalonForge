/* Daviana marketing-site analytics: PostHog EU, same project as the client portal (223925).
   Publishable write-only project key (same trust model as a Stripe pk_). No cookies:
   state lives in sessionStorage and is gone when the tab closes. No session recording
   (Clarity already does that). Form values are never sent - only that a form was submitted. */
(function () {
  var KEY = "phc_BqD4S9B2Poy5pTsCaYkABG3tkTcqHDsrXV78K3ePGGjc";
  var q = [];                                         // events raised before the library has loaded
  function cap(name, props) { if (window.posthog && posthog.__loaded) posthog.capture(name, props); else q.push([name, props]); }

  // The existing forms already announce a successful submit to Google/Meta. Piggy-back on
  // that instead of editing five form handlers: same trigger, so counts line up with Ads.
  var g = window.gtag;
  window.gtag = function () {
    try { if (arguments[0] === "event" && arguments[1] === "generate_lead") cap("lead_submitted", { form: (arguments[2] || {}).event_category }); } catch (e) {}
    return g && g.apply(this, arguments);
  };

  var s = document.createElement("script");
  s.async = true; s.src = "https://eu-assets.i.posthog.com/static/array.js";
  s.onload = function () {
    if (!window.posthog || !posthog.init) return;
    posthog.init(KEY, {
      api_host: "https://eu.i.posthog.com", ui_host: "https://eu.posthog.com",
      defaults: "2025-05-24", persistence: "sessionStorage", person_profiles: "identified_only",
      disable_session_recording: true, respect_dnt: true, capture_pageview: true, capture_pageleave: true,
      autocapture: { dom_event_allowlist: ["click", "submit"], capture_copied_text: false },
      loaded: function (ph) {
        ph.register({ site: "marketing", page_lang: document.documentElement.lang || "en" });
        while (q.length) { var e = q.shift(); ph.capture(e[0], e[1]); }
      }
    });
  };
  document.head.appendChild(s);
})();

/*
 * daviana.app/api/demo-call: same-origin relay for the demo-call picker on /trial/.
 *
 * 18 Nov 2026. A salon owner (Samrah, 17 Nov) emailed that booking a demo kept failing.
 * The page loaded, but her browser could not reach my.daviana.app/api/public/demo-call:
 * she saw the "Online booking is busy" fallback, and the failure was never recorded,
 * because the only failure signal went through PostHog in the same browser, and that
 * was blocked too. Ad blockers, privacy DNS, antivirus and work networks that intercept
 * TLS (one device rejected my.daviana.app's certificate the same afternoon) all cause this.
 *
 * The page still calls my.daviana.app directly first. Only when that fails does it come
 * here. This function runs on daviana.app itself, so a browser that loaded the page can
 * reach it, and it forwards the request server-to-server, where nothing on the visitor's
 * side can block it.
 *
 *   GET  /api/demo-call?why=...      free slots (relayed)
 *   POST /api/demo-call              book a slot (relayed, same JSON body as upstream)
 *   POST /api/demo-call?report=1     the page gave up: record it, nothing else
 *
 * Every relay use and every give-up becomes a PostHog event sent from here, so it is
 * visible even when the visitor's own browser blocks PostHog:
 *   demo_relay_used, demo_relay_failed, demo_booking_unreachable.
 *
 * Upstream rate limits are per IP, and relayed calls share Cloudflare's IPs. That is
 * fine for a fallback path that should be rare; if demo_relay_used gets frequent, the
 * upstream needs a signed relay header instead.
 */

const UPSTREAM = 'https://my.daviana.app/api/public/demo-call';
// Public project key, the same one served to every visitor in /assets/analytics.js.
const PH_KEY = 'phc_BqD4S9B2Poy5pTsCaYkABG3tkTcqHDsrXV78K3ePGGjc';
const ALLOWED_ORIGIN = /^https:\/\/((www\.)?daviana\.app|([a-z0-9-]+\.)?daviana-5l6\.pages\.dev)$/;
const MAX_BODY = 4096;
const TIMEOUT_MS = 12000;

function json(body, status) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' },
  });
}

function visitor(request) {
  const cf = request.cf || {};
  return {
    ua: (request.headers.get('user-agent') || '').slice(0, 200),
    country: cf.country || '',
    asn_org: (cf.asOrganization || '').slice(0, 80),
  };
}

function capture(ctx, event, props) {
  const body = JSON.stringify({
    api_key: PH_KEY,
    event,
    distinct_id: 'demo-relay',
    properties: Object.assign({ site: 'marketing', $process_person_profile: false }, props),
  });
  ctx.waitUntil(
    fetch('https://eu.i.posthog.com/capture/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body,
    }).catch(() => {})
  );
}

function originOk(request) {
  const o = request.headers.get('origin');
  // Browsers always send Origin on POST (fetch and sendBeacon alike), so a missing one is a
  // script, not a visitor. This does not make the relay private: my.daviana.app's endpoint
  // is public anyway. It just keeps scripts from draining the shared relay rate limit.
  return !!o && ALLOWED_ORIGIN.test(o);
}

async function upstream(method, body) {
  const ac = new AbortController();
  const t = setTimeout(() => ac.abort(), TIMEOUT_MS);
  try {
    return await fetch(UPSTREAM, {
      method,
      headers: Object.assign(
        { Origin: 'https://daviana.app', Accept: 'application/json' },
        body ? { 'Content-Type': 'application/json' } : {}
      ),
      body: body || undefined,
      signal: ac.signal,
    });
  } finally {
    clearTimeout(t);
  }
}

async function relay(ctx, method, body, stage, why) {
  let res;
  try {
    res = await upstream(method, body);
  } catch (e) {
    capture(ctx, 'demo_relay_failed', Object.assign({ stage, why, error: String((e && e.name) || e).slice(0, 80) }, visitor(ctx.request)));
    return json({ error: 'Could not reach us. Please try again.' }, 502);
  }
  const text = await res.text();
  capture(ctx, 'demo_relay_used', Object.assign({ stage, why, status: res.status }, visitor(ctx.request)));
  return new Response(text, {
    status: res.status,
    headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' },
  });
}

export async function onRequestGet(ctx) {
  const why = (new URL(ctx.request.url).searchParams.get('why') || '').slice(0, 80);
  return relay(ctx, 'GET', null, 'slots', why);
}

export async function onRequestPost(ctx) {
  const { request } = ctx;
  if (!originOk(request)) return json({ error: 'Forbidden.' }, 403);
  const url = new URL(request.url);
  const text = await request.text();
  if (text.length > MAX_BODY) return json({ error: 'Invalid request.' }, 400);

  if (url.searchParams.get('report')) {
    let r = {};
    try { r = JSON.parse(text) || {}; } catch (_) {}
    capture(ctx, 'demo_booking_unreachable', Object.assign({
      stage: String(r.stage || '').slice(0, 40),
      detail: String(r.detail || '').slice(0, 120),
      page: String(r.page || '').slice(0, 120),
    }, visitor(request)));
    return new Response(null, { status: 204 });
  }

  const why = (url.searchParams.get('why') || '').slice(0, 80);
  return relay(ctx, 'POST', text, 'book', why);
}

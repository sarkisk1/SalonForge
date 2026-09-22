#!/usr/bin/env python3
"""Create/update the 'Website — Traffic & Leads' PostHog dashboard (project 223925, EU).

Idempotent: insights are matched by name and PATCHed, missing ones are created.
Reads the personal API key from the macOS keychain (service posthog-personal-api-key);
the key is never printed or written anywhere. Only touches this dashboard's insights.
"""
import json, subprocess, sys, urllib.request, urllib.error

PROJECT, HOST = 223925, "https://eu.posthog.com"
DASH_NAME = "Website — Traffic & Leads"
KEY = subprocess.run(["security", "find-generic-password", "-s", "posthog-personal-api-key", "-w"],
                     capture_output=True, text=True, check=True).stdout.strip()
assert len(KEY) >= 30, "empty key in keychain"

def api(method, path, body=None):
    req = urllib.request.Request(f"{HOST}/api/projects/{PROJECT}/{path}", method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"{method} {path} -> {e.code}: {e.read().decode()[:400]}")

def prop(key, value, op="exact", typ="event"):
    return {"key": key, "type": typ, "value": value if isinstance(value, list) else [value], "operator": op}

SITE_VALUES = [prop("$host", "daviana.app"), prop("site", "marketing")]   # real marketing site only: not localhost, not the old booking-app traffic that once used this host
SITE = {"type": "AND", "values": [{"type": "AND", "values": SITE_VALUES}]}
PV = lambda extra=None: {"kind": "EventsNode", "event": "$pageview", "name": "$pageview", "math": "total", **({"properties": extra} if extra else {})}

def trends(series, display="ActionsLineGraph", breakdown=None, interval="day", date_from="-30d", props=SITE, limit=None):
    s = {"kind": "TrendsQuery", "series": series, "dateRange": {"date_from": date_from}, "interval": interval,
         "filterTestAccounts": True, "properties": props, "trendsFilter": {"display": display}}
    if breakdown: s["breakdownFilter"] = {"breakdown": breakdown, "breakdown_type": "event", **({"breakdown_limit": limit} if limit else {})}
    return {"kind": "InsightVizNode", "source": s}

def funnel(steps, name_steps):
    series = [{"kind": "EventsNode", "event": ev, "name": nm, "properties": pr} for (ev, pr), nm in zip(steps, name_steps)]
    return {"kind": "InsightVizNode", "source": {"kind": "FunnelsQuery", "series": series, "dateRange": {"date_from": "-30d"},
            "filterTestAccounts": True, "properties": SITE,
            "funnelsFilter": {"funnelVizType": "steps", "funnelWindowInterval": 1, "funnelWindowIntervalUnit": "day", "layout": "horizontal"}}}

path_is = lambda p: [prop("$pathname", p)]
INSIGHTS = {
 "Visitors and page views (daily)": trends([
     {"kind": "EventsNode", "event": "$pageview", "name": "Page views", "custom_name": "Page views", "math": "total"},
     {"kind": "EventsNode", "event": "$pageview", "name": "Visitors", "custom_name": "Visitors", "math": "dau"}]),
 "Demo funnel: visit → Book a demo page → submitted": funnel(
     [("$pageview", None), ("$pageview", path_is("/demo/")), ("lead_submitted", [prop("form", "demo")])],
     ["Any page", "Opened Book a demo", "Submitted demo form"]),
 "Trial funnel: visit → Trial page → submitted": funnel(
     [("$pageview", None), ("$pageview", path_is("/trial/")), ("lead_submitted", [prop("form", "trial")])],
     ["Any page", "Opened trial page", "Submitted trial"]),
 "Trial quiz, step by step (any /trial/ page)": funnel(
     [("$pageview", [prop("$pathname", "/trial/", "icontains")]), ("quiz_start", None), ("quiz_step", None), ("lead_submitted", [prop("form", "trial")])],
     ["Opened a trial page", "Started the quiz", "Answered a question", "Submitted trial"]),
 "Quiz steps reached (daily)": trends([{"kind": "EventsNode", "event": "quiz_step", "name": "quiz_step", "math": "total"}], breakdown="label"),
 "Pricing funnel: visit → Pricing page → plan submitted": funnel(
     [("$pageview", None), ("$pageview", path_is("/pricing/")), ("lead_submitted", [prop("form", "pricing")])],
     ["Any page", "Opened pricing", "Submitted plan"]),
 "Leads by form (daily)": trends([{"kind": "EventsNode", "event": "lead_submitted", "name": "lead_submitted", "math": "total"}],
                                display="ActionsBar", breakdown="form"),
 "Form errors (daily) — a submit that never reached the worker": trends([{"kind": "EventsNode", "event": "lead_submit_failed", "name": "lead_submit_failed", "math": "total"}], breakdown="form"),
 "Top pages (30 days)": trends([PV()], display="ActionsTable", breakdown="$pathname", limit=25),
 "Where visitors come from (referrer)": trends(
     [PV()], display="ActionsTable", breakdown="$referring_domain", limit=20,
     props={"type": "AND", "values": [{"type": "AND", "values": [*SITE_VALUES,
            prop("$referring_domain", ["daviana.app", "$direct"], "is_not")]}]}),
 "Ad and campaign source (utm_source)": trends(
     [PV()], display="ActionsTable", breakdown="utm_source", limit=20,
     props={"type": "AND", "values": [{"type": "AND", "values": [*SITE_VALUES, prop("utm_source", "is_set", "is_set")]}]}),
 "Page views by language": trends([PV()], display="ActionsPie", breakdown="page_lang"),
 "What people click (top buttons and links)": trends(
     [{"kind": "EventsNode", "event": "$autocapture", "name": "Clicks", "math": "total"}], display="ActionsTable", breakdown="$el_text", limit=25,
     props={"type": "AND", "values": [{"type": "AND", "values": [*SITE_VALUES, prop("$event_type", "click")]}]}),
 "Site deploys (what shipped, when)": trends(
     [{"kind": "EventsNode", "event": "site_deployed", "name": "Deploys", "math": "total"}], display="ActionsBar",
     props={"type": "AND", "values": [{"type": "AND", "values": [prop("site", "marketing")]}]}),
 "Device types": trends([PV()], display="ActionsPie", breakdown="$device_type"),
}

dash = next((d for d in api("GET", "dashboards/?limit=100")["results"] if d["name"] == DASH_NAME), None)
if not dash:
    dash = api("POST", "dashboards/", {"name": DASH_NAME, "description": "Daviana marketing site (daviana.app). Built by tools/analytics/build_dashboard.py — edit the script, not the tiles.",
                                        "tags": ["website", "managed-by-script"]})
    print("created dashboard", dash["id"])
existing = {}
for t in api("GET", f"dashboards/{dash['id']}/")["tiles"]:
    if t.get("insight"): existing[t["insight"]["name"]] = t["insight"]["id"]
for name, query in INSIGHTS.items():
    if name in existing:
        api("PATCH", f"insights/{existing[name]}/", {"query": query}); print("updated ", name)
    else:
        api("POST", "insights/", {"name": name, "query": query, "dashboards": [dash["id"]], "saved": True, "tags": ["website"]}); print("created ", name)
print(f"\n{HOST}/project/{PROJECT}/dashboard/{dash['id']}")

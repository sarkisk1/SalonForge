#!/usr/bin/env python3
"""Daily email of the 'Website — Traffic & Leads' dashboard (idempotent by title + recipient)."""
import json, subprocess, sys, urllib.request, urllib.error
EMAIL = sys.argv[1] if len(sys.argv) > 1 else sys.exit("usage: subscribe.py <email>")
KEY = subprocess.run(["security", "find-generic-password", "-s", "posthog-personal-api-key", "-w"], capture_output=True, text=True, check=True).stdout.strip()
B = "https://eu.posthog.com/api/projects/223925"
def call(m, p, b=None):
    r = urllib.request.Request(f"{B}/{p}", method=m, data=json.dumps(b).encode() if b is not None else None,
                               headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    try: return json.load(urllib.request.urlopen(r, timeout=60))
    except urllib.error.HTTPError as e: sys.exit(f"{m} {p} -> {e.code}: {e.read().decode()[:400]}")
dash = next(d for d in call("GET", "dashboards/?limit=100")["results"] if d["name"] == "Website — Traffic & Leads")
ids = {t["insight"]["name"]: t["insight"]["id"] for t in call("GET", f"dashboards/{dash['id']}/")["tiles"] if t.get("insight")}
PICK = ["Visitors and page views (daily)", "Demo funnel: visit → Book a demo page → submitted", "Trial funnel: visit → Trial page → submitted",
        "Pricing funnel: visit → Pricing page → plan submitted", "Leads by form (daily)", "Top pages (30 days)"]
title = "Daviana website — daily summary"
body = {"dashboard": dash["id"], "dashboard_export_insights": [ids[n] for n in PICK], "target_type": "email", "target_value": EMAIL,
        "frequency": "daily", "interval": 1, "start_date": "2026-09-23T07:00:00Z", "title": title}
have = [s for s in call("GET", "subscriptions/")["results"] if s["title"] == title and s["target_value"] == EMAIL and not s.get("deleted")]
if have: call("PATCH", f"subscriptions/{have[0]['id']}/", body); print("updated subscription", have[0]["id"])
else:
    s = call("POST", "subscriptions/", body); print("created subscription", s["id"], "next delivery:", s.get("next_delivery_date"))

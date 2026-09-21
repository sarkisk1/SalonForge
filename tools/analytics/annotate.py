#!/usr/bin/env python3
"""Deploy markers: one PostHog annotation per merged PR on SalonForge main.

  annotate.py            add markers for every merged PR (last 30 days) that has none yet
  annotate.py "text"     add one marker for right now

Idempotent (matched by the '#<PR number>' in the text). Key comes from the macOS keychain;
GitHub data from the gh CLI. Only creates annotations; never edits or deletes.
"""
import json, subprocess, sys, urllib.request, urllib.error, datetime
KEY = subprocess.run(["security", "find-generic-password", "-s", "posthog-personal-api-key", "-w"], capture_output=True, text=True, check=True).stdout.strip()
B = "https://eu.posthog.com/api/projects/223925"
def call(m, p, b=None):
    r = urllib.request.Request(f"{B}/{p}", method=m, data=json.dumps(b).encode() if b is not None else None,
                               headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    try: return json.load(urllib.request.urlopen(r, timeout=60))
    except urllib.error.HTTPError as e: sys.exit(f"{m} {p} -> {e.code}: {e.read().decode()[:400]}")
def add(text, when):
    call("POST", "annotations/", {"content": text, "date_marker": when, "scope": "project", "creation_type": "USR"}); print("marked", when[:16], text)
if len(sys.argv) > 1:
    add(" ".join(sys.argv[1:]), datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")); sys.exit()
have = " ".join(a["content"] for a in call("GET", "annotations/?limit=500").get("results", []) if a.get("content"))
since = max((datetime.date.today() - datetime.timedelta(days=30)).isoformat(), "2026-09-21")   # the site only sends analytics from 2026-09-21
prs = json.loads(subprocess.run(["gh", "pr", "list", "--repo", "sarkisk1/SalonForge", "--state", "merged", "--base", "main", "--limit", "60",
                                 "--search", f"merged:>={since}", "--json", "number,title,mergedAt"], capture_output=True, text=True, check=True).stdout)
n = 0
for pr in sorted(prs, key=lambda x: x["mergedAt"]):
    if f"#{pr['number']}" in have: continue
    add(f"Site deployed: {pr['title']} (#{pr['number']})", pr["mergedAt"]); n += 1
print(f"{n} new markers")

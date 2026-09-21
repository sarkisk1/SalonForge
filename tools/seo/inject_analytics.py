#!/usr/bin/env python3
"""Add the PostHog loader to every built page (idempotent)."""
import sys, pathlib
DIST = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
TAG = '<script defer src="/assets/analytics.js?v=2"></script>'
n = 0
for f in DIST.rglob("index.html"):
    s = f.read_text()
    if "/assets/analytics.js" in s or "</head>" not in s: continue
    f.write_text(s.replace("</head>", TAG + "\n</head>", 1)); n += 1
print("pages tagged:", n)

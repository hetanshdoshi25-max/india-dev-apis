#!/usr/bin/env python3
"""
check.py — fires one real request at every API in apis.yaml and records what
actually happened.

This is the point of the whole repo. Published API docs go stale, aggregator
sites copy each other's mistakes, and nobody notices when a free endpoint
quietly dies. So instead of trusting anyone's claims, we measure:

  - is it up
  - how slow is it
  - does it really send Access-Control-Allow-Origin (docs are often wrong)

Results land in data/status.json, which build_readme.py renders into the table.

    python scripts/check.py
"""
import json
import os
import sys
import time
from datetime import datetime, timezone

import requests
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TIMEOUT = 15
UA = "india-dev-apis-checker/1.0 (+https://github.com/hetanshdoshi25-max/india-dev-apis)"

# A browser-ish Origin, so CORS detection reflects what a real frontend sees.
HEADERS = {"User-Agent": UA, "Accept": "application/json", "Origin": "https://example.com"}


def probe(entry):
    p = entry.get("probe")
    if not p:
        return {"state": "unchecked", "reason": "no probe defined"}

    expect = p.get("expect_status", [200])
    if isinstance(expect, int):
        expect = [expect]

    started = time.perf_counter()
    try:
        r = requests.get(p["url"], headers=HEADERS, timeout=TIMEOUT)
    except requests.RequestException as e:
        return {"state": "down", "reason": type(e).__name__}
    ms = int((time.perf_counter() - started) * 1000)

    result = {
        "ms": ms,
        "http": r.status_code,
        "cors": bool(r.headers.get("Access-Control-Allow-Origin")),
    }

    if r.status_code not in expect:
        result["state"] = "down"
        result["reason"] = f"HTTP {r.status_code}"
        return result

    needle = p.get("expect_contains")
    if needle and needle not in r.text:
        # 200 OK with the wrong body is the failure mode that kills these lists:
        # the endpoint "works" but now returns a login page or an error envelope.
        result["state"] = "changed"
        result["reason"] = f"missing {needle!r} in response"
        return result

    result["state"] = "up"
    return result


def main():
    with open(os.path.join(ROOT, "apis.yaml"), encoding="utf-8") as f:
        entries = yaml.safe_load(f)

    previous = {}
    path = os.path.join(ROOT, "data", "status.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            previous = json.load(f).get("results", {})

    results = {}
    for e in entries:
        r = probe(e)
        # keep the last date this entry was seen healthy, so the README can show
        # "last verified" rather than only a live snapshot
        was = previous.get(e["id"], {})
        r["last_ok"] = (datetime.now(timezone.utc).date().isoformat()
                        if r["state"] == "up" else was.get("last_ok"))
        results[e["id"]] = r
        print(f"{e['id']:24} {r['state']:10} {r.get('ms', '-')}ms "
              f"cors={r.get('cors')} {r.get('reason', '')}")

    os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                   "results": results}, f, indent=1)
        f.write("\n")

    broken = [k for k, v in results.items() if v["state"] in ("down", "changed")]
    if broken:
        # Don't fail the build — a dead API is data, not an error. The README
        # should ship saying "this one is down", which is exactly the value.
        print(f"\nnote: {len(broken)} entr{'y' if len(broken) == 1 else 'ies'} "
              f"unhealthy: {', '.join(broken)}", file=sys.stderr)


if __name__ == "__main__":
    main()

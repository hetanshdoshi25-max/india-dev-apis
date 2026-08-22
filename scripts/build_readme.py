#!/usr/bin/env python3
"""
build_readme.py — apis.yaml + data/status.json -> README.md

README.md is a build artifact. Edit apis.yaml instead.

    python scripts/build_readme.py
"""
import json
import os
from collections import OrderedDict
from datetime import datetime, timezone

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STATE = {
    "up":        "🟢 up",
    "down":      "🔴 down",
    "changed":   "🟠 changed",
    "unchecked": "⚪ unchecked",
}
AUTH = {
    "none":  "none",
    "key":   "API key",
    "oauth": "OAuth",
}

HEAD = """# India dev APIs

APIs you actually need when you're building for India — postal, banking,
government data — with one thing no other list gives you: **every endpoint is
pinged by a robot every day.**

Status, latency and CORS support in the table below are measured, not copied
from documentation. Published docs are wrong often enough that measuring is the
only honest option.

<!-- This file is generated. Edit apis.yaml, not this. -->

**Last checked: {checked}** · {up} up · {down} down · {other} other

## What the checking actually caught

Not a hypothetical. On day one, the checker found that
**PincodeAPI.in's published documentation is wrong in three separate ways**:

| Docs say | Actually |
|---|---|
| Base path `/api/v1/` | `/v1/` |
| Results in a flat `data` array | Nested under `data.post_offices` |
| Fields like `officename` | snake_case — `post_offices`, `circle_slug` |

And the part that will cost you an afternoon: **a wrong path does not 404.** It
returns `HTTP 200` with the API's index document. So if you follow those docs,
your request succeeds, your status check passes, and your parser silently finds
nothing. There is no error to search for.

The fix is a habit worth stealing regardless of which API you're using: **assert
on a field you expect, never on `200` alone.** That's exactly what this repo's
probes do — see `expect_contains` in [apis.yaml](apis.yaml).

None of this is in any other list, because no other list checks.

"""

FOOT = """
## What the columns mean

| Column | |
|---|---|
| **Status** | Result of a real GET request, run daily by [GitHub Actions](.github/workflows/check.yml). 🟠 *changed* means it returned 200 but the body no longer looks right — usually the sign an API went behind a login. |
| **Auth** | `none` means no signup, no key, no header. |
| **CORS** | Detected from the `Access-Control-Allow-Origin` header on a real cross-origin request. If this says no, you need a backend proxy — you cannot call it from the browser. |
| **Latency** | Single sample from a GitHub Actions runner in the US. Treat as a rough signal, not a benchmark. From India it will usually be faster. |

## Adding an API

Open a PR editing `apis.yaml`. Every entry needs a `probe` block so the checker
can verify it — entries without one show as ⚪ unchecked and won't be merged.
See [CONTRIBUTING.md](CONTRIBUTING.md).

## Deliberately not here

- **Scraped endpoints** (NSE, BSE, IRCTC internal JSON). They break constantly,
  and using them likely violates the site's terms.
- **RapidAPI resellers** wrapping a free upstream. Linked to the upstream instead.
- **Anything requiring KYC or a business entity to even see the docs.**

## Licence

[MIT](LICENSE). The list is a set of links and facts — the APIs themselves are
owned by their respective providers and carry their own terms.
"""


def main():
    with open(os.path.join(ROOT, "apis.yaml"), encoding="utf-8") as f:
        entries = yaml.safe_load(f)

    status_path = os.path.join(ROOT, "data", "status.json")
    status, checked = {}, "never"
    if os.path.exists(status_path):
        with open(status_path, encoding="utf-8") as f:
            blob = json.load(f)
        status = blob.get("results", {})
        checked = blob.get("checked_at", "never")[:10]

    counts = {"up": 0, "down": 0, "other": 0}
    for e in entries:
        s = status.get(e["id"], {}).get("state", "unchecked")
        counts[s if s in ("up", "down") else "other"] += 1

    out = [HEAD.format(checked=checked, **counts)]

    groups = OrderedDict()
    for e in entries:
        groups.setdefault(e["category"], []).append(e)

    for category, items in groups.items():
        out.append(f"## {category}\n")
        out.append("| API | What you get | Status | Auth | CORS | Latency |")
        out.append("|---|---|---|---|---|---|")
        for e in items:
            s = status.get(e["id"], {})
            state = STATE.get(s.get("state", "unchecked"), "⚪ unchecked")
            cors = {True: "yes", False: "no"}.get(s.get("cors"), "—")
            ms = f'{s["ms"]} ms' if s.get("ms") else "—"
            out.append(f'| [{e["name"]}]({e["docs"]}) | {e["what"]} | {state} '
                       f'| {AUTH.get(e["auth"], e["auth"])} | {cors} | {ms} |')
        out.append("")

        for e in items:
            out.append(f'### {e["name"]}\n')
            out.append(f'{e["what"]}\n')
            out.append(f'**Free tier —** {e["free"]}\n')
            if e.get("licence"):
                out.append(f'**Licence —** {e["licence"]}\n')
            if e.get("notes"):
                out.append(f'{e["notes"].strip()}\n')
            out.append("```bash")
            out.append(e["example"].strip())
            out.append("```\n")
            if e.get("probe", {}).get("note"):
                out.append(f'<sub>⚠ Status check: {e["probe"]["note"].strip()}</sub>\n')
            last_ok = status.get(e["id"], {}).get("last_ok")
            if last_ok:
                out.append(f"<sub>Last seen working: {last_ok}</sub>\n")

    out.append(FOOT)

    with open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print(f"wrote README.md — {len(entries)} entries, "
          f"{counts['up']} up / {counts['down']} down")


if __name__ == "__main__":
    main()

# Contributing

One rule: **if a robot can't verify it, it doesn't go in.**

## Adding an API

Edit `apis.yaml` only. `README.md` is generated and your changes to it will be
overwritten by the next daily run.

```yaml
- id: my-api                  # stable slug, never change it once merged
  name: My API
  category: Location & postal # reuse an existing category if one fits
  what: One line. What comes back, in plain language.
  docs: https://example.com/docs   # real docs, not an aggregator page
  auth: none                  # none | key | oauth
  free: Be specific. "10k requests/month, then paid" beats "generous free tier".
  notes: >                    # optional: gotchas, when to pick something else
    Anything that cost you an afternoon to find out.
  probe:
    url: https://api.example.com/v1/thing/400001
    expect_contains: some_field_name
  example: |
    curl -s https://api.example.com/v1/thing/400001
```

Then run it locally before opening the PR:

```bash
pip install -r scripts/requirements.txt
python scripts/check.py          # your entry must come back 🟢 up
python scripts/build_readme.py
```

## Picking a good probe

- Use a **boring, permanent** example, such as Mumbai GPO (`400001`) or a large
  bank branch. Not something seasonal or user-specific.
- `expect_contains` should be a **field name from the response body**, not a
  value. Values change; schemas mostly don't.
- If the API needs a key, probe an unauthenticated URL that still proves the
  service is alive (docs root, health endpoint) and set
  `expect_status: [200, 401, 403]`.
- Never put a real API key in `apis.yaml`. The checker runs on a public repo
  with no secrets, by design.

## What gets rejected

- **Scraped internal endpoints.** NSE, BSE, IRCTC and friends. They break
  weekly and using them probably violates the site's terms.
- **RapidAPI resellers** of something already free upstream. Link the upstream.
- **Entries with no probe.** These show as ⚪ unchecked and can't be merged.
- **Dead or paywalled APIs.** If the free tier disappeared, it leaves the list.

## Wanted

Entries we'd like but haven't been able to verify. A PR with a working `probe`
is the whole contribution:

- **[data.gov.in](https://data.gov.in)**, the government open-data platform.
  Genuinely useful, but it needs an API key, and this repo holds no secrets by
  design. If you can find an unauthenticated URL that reliably proves the
  service is alive, open a PR. It was in the list briefly and removed for
  exactly this reason.
- **UPI / NPCI**, **GSTIN verification**, **vehicle registration**. All seem
  to be paywalled or KYC-gated. Happy to be proven wrong.

## Reporting a broken API

Open an issue with the `id` and what you saw. If the daily check already caught
it the table will show 🔴 or 🟠 , a PR removing it, or a `notes:` line
explaining the change, is very welcome.

# India dev APIs

APIs you actually need when you're building for India: postal, banking and
government data, with one thing no other list gives you. **Every endpoint is
pinged by a robot every day.**

Status, latency and CORS support in the table below are measured, not copied
from documentation. Published docs are wrong often enough that measuring is the
only honest option.

<!-- This file is generated. Edit apis.yaml, not this. -->

**Last checked: 2026-08-31** · 4 up · 0 down · 0 other

## What the checking actually caught

Not a hypothetical. On day one, the checker found that
**PincodeAPI.in's published documentation is wrong in three separate ways**:

| Docs say | Actually |
|---|---|
| Base path `/api/v1/` | `/v1/` |
| Results in a flat `data` array | Nested under `data.post_offices` |
| Fields like `officename` | snake_case: `post_offices`, `circle_slug` |

And the part that will cost you an afternoon: **a wrong path does not 404.** It
returns `HTTP 200` with the API's index document. So if you follow those docs,
your request succeeds, your status check passes, and your parser silently finds
nothing. There is no error to search for.

The fix is a habit worth stealing regardless of which API you're using: **assert
on a field you expect, never on `200` alone.** That's exactly what this repo's
probes do. See `expect_contains` in [apis.yaml](apis.yaml).

None of this is in any other list, because no other list checks.


## Location & postal

| API | What you get | Status | Auth | CORS | Latency |
|---|---|---|---|---|---|
| [Postal PIN Code](http://www.postalpincode.in/Api-Details) | Post office name, district, state, delivery status for any 6-digit PIN. | 🟢 up | none | yes | 332 ms |
| [PincodeAPI.in](https://api.pincodeapi.in/) | Same postal dataset, nested under data.post_offices, plus search and district listing. | 🟢 up | none | yes | 524 ms |
| [India Pincode API (static)](https://aniket-thapa.github.io/india-pincode-api/) | Every PIN as a flat JSON file on GitHub Pages. No server, so nothing to rate-limit. | 🟢 up | none | yes | 62 ms |

### Postal PIN Code

Post office name, district, state, delivery status for any 6-digit PIN.

**Free tier:** No published quota. Treat as best-effort, cache aggressively.

```bash
curl -s https://api.postalpincode.in/pincode/400001
```

<sub>Last seen working: 2026-08-31</sub>

### PincodeAPI.in

Same postal dataset, nested under data.post_offices, plus search and district listing.

**Free tier:** Unmetered at time of writing. Paginated for large states.

The published docs are stale in three separate ways, all found by this repo's daily checker, none of them mentioned upstream. (1) The live base path is /v1/, not /api/v1/. (2) Results are nested under data.post_offices, not a flat data array. (3) Fields are snake_case (post_offices, circle_slug), not the flat lowercase names the docs show. Worst of all, an unknown path does not 404: it returns HTTP 200 with the API index document, so a wrong URL looks like a successful request while your parser silently gets nothing. Always assert on a field you expect, never on status 200 alone.

```bash
curl -s https://api.pincodeapi.in/v1/pincode/110001
curl -s "https://api.pincodeapi.in/v1/search?q=Connaught%20Place"
```

<sub>Last seen working: 2026-08-31</sub>

### India Pincode API (static)

Every PIN as a flat JSON file on GitHub Pages. No server, so nothing to rate-limit.

**Free tier:** Unlimited. It is static hosting, not an API server.

**Licence:** CC BY-NC 4.0

Non-commercial licence. Check this before you ship it in a paid product; the other two entries here have no such restriction. Best choice for bulk or offline lookups. Worst choice when you need freshness: it only updates when the maintainer regenerates the files.

```bash
curl -s https://aniket-thapa.github.io/india-pincode-api/pincodes/400001.json
```

<sub>Last seen working: 2026-08-31</sub>

## Banking & finance

| API | What you get | Status | Auth | CORS | Latency |
|---|---|---|---|---|---|
| [Razorpay IFSC](https://github.com/razorpay/ifsc/wiki/API) | Bank, branch, address, MICR/SWIFT, and NEFT/RTGS/IMPS/UPI flags for an IFSC code. | 🟢 up | none | yes | 774 ms |

### Razorpay IFSC

Bank, branch, address, MICR/SWIFT, and NEFT/RTGS/IMPS/UPI flags for an IFSC code.

**Free tier:** Public and unmetered. Razorpay runs it for the community.

Built from RBI's own datasets, MIT licensed, and downloadable in bulk if you would rather not hit the network at all. BANK/BANKCODE reflect the sublet branch, so they may not match the bank name you expect.

```bash
curl -s https://ifsc.razorpay.com/HDFC0000001
```

<sub>Last seen working: 2026-08-31</sub>


## What the columns mean

| Column | |
|---|---|
| **Status** | Result of a real GET request, run daily by [GitHub Actions](.github/workflows/check.yml). 🟠 *changed* means it returned 200 but the body no longer looks right, usually the sign an API went behind a login. |
| **Auth** | `none` means no signup, no key, no header. |
| **CORS** | Detected from the `Access-Control-Allow-Origin` header on a real cross-origin request. If this says no, you need a backend proxy. You cannot call it from the browser. |
| **Latency** | Single sample from a GitHub Actions runner in the US. Treat as a rough signal, not a benchmark. From India it will usually be faster. |

## Adding an API

Open a PR editing `apis.yaml`. Every entry needs a `probe` block so the checker
can verify it. Entries without one show as ⚪ unchecked and won't be merged.
See [CONTRIBUTING.md](CONTRIBUTING.md).

## Deliberately not here

- **Scraped endpoints** (NSE, BSE, IRCTC internal JSON). They break constantly,
  and using them likely violates the site's terms.
- **RapidAPI resellers** wrapping a free upstream. Linked to the upstream instead.
- **Anything requiring KYC or a business entity to even see the docs.**

## Licence

[MIT](LICENSE). The list is a set of links and facts. The APIs themselves are
owned by their respective providers and carry their own terms.

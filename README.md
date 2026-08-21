# India dev APIs

APIs you actually need when you're building for India — postal, banking,
government data — with one thing no other list gives you: **every endpoint is
pinged by a robot every day.**

Status, latency and CORS support in the table below are measured, not copied
from documentation. Published docs are wrong often enough that measuring is the
only honest option.

<!-- This file is generated. Edit apis.yaml, not this. -->

**Last checked: 2026-08-21** · 3 up · 1 down · 1 other


## Location & postal

| API | What you get | Status | Auth | CORS | Latency |
|---|---|---|---|---|---|
| [Postal PIN Code](http://www.postalpincode.in/Api-Details) | Post office name, district, state, delivery status for any 6-digit PIN. | 🟢 up | none | yes | 372 ms |
| [PincodeAPI.in](https://api.pincodeapi.in/) | Same postal dataset, plus search-as-you-type and state/district listing. | 🟠 changed | none | yes | 826 ms |
| [India Pincode API (static)](https://aniket-thapa.github.io/india-pincode-api/) | Every PIN as a flat JSON file on GitHub Pages. No server, so nothing to rate-limit. | 🟢 up | none | yes | 44 ms |

### Postal PIN Code

Post office name, district, state, delivery status for any 6-digit PIN.

**Free tier —** No published quota. Treat as best-effort, cache aggressively.

```bash
curl -s https://api.postalpincode.in/pincode/400001
```

<sub>Last seen working: 2026-08-21</sub>

### PincodeAPI.in

Same postal dataset, plus search-as-you-type and state/district listing.

**Free tier —** Unmetered at time of writing. Paginated for large states.

```bash
curl -s "https://api.pincodeapi.in/api/v1/search?q=Connaught%20Place"
```

### India Pincode API (static)

Every PIN as a flat JSON file on GitHub Pages. No server, so nothing to rate-limit.

**Free tier —** Unlimited — it is static hosting, not an API server.

Best choice when you need bulk lookups or offline data. Worst choice when you need freshness: it updates only when the maintainer regenerates it.

```bash
curl -s https://aniket-thapa.github.io/india-pincode-api/pincodes/400001.json
```

<sub>Last seen working: 2026-08-21</sub>

## Banking & finance

| API | What you get | Status | Auth | CORS | Latency |
|---|---|---|---|---|---|
| [Razorpay IFSC](https://github.com/razorpay/ifsc/wiki/API) | Bank, branch, address, MICR/SWIFT, and NEFT/RTGS/IMPS/UPI flags for an IFSC code. | 🟢 up | none | yes | 718 ms |

### Razorpay IFSC

Bank, branch, address, MICR/SWIFT, and NEFT/RTGS/IMPS/UPI flags for an IFSC code.

**Free tier —** Public and unmetered. Razorpay runs it for the community.

Built from RBI's own datasets, MIT licensed, and downloadable in bulk if you would rather not hit the network at all. BANK/BANKCODE reflect the sublet branch, so they may not match the bank name you expect.

```bash
curl -s https://ifsc.razorpay.com/HDFC0000001
```

<sub>Last seen working: 2026-08-21</sub>

## Government & open data

| API | What you get | Status | Auth | CORS | Latency |
|---|---|---|---|---|---|
| [data.gov.in OGD Platform](https://data.gov.in/help/how-use-datasets-apis) | Thousands of government datasets as REST resources — crops, fuel prices, census, more. | 🔴 down | API key | no | 426 ms |

### data.gov.in OGD Platform

Thousands of government datasets as REST resources — crops, fuel prices, census, more.

**Free tier —** Free key after signup. Per-key rate limits apply.

Dataset quality is uneven and resource IDs change without warning. Pin the resource ID you use and check it on every deploy.

```bash
# Sign up at data.gov.in, then:
curl -s "https://api.data.gov.in/resource/RESOURCE_ID?api-key=YOUR_KEY&format=json&limit=5"
```

<sub>⚠ Status check: Liveness only. The API itself needs a key, which this public repo has no business holding, so we check the platform is reachable and no more.</sub>


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

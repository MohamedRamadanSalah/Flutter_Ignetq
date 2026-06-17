# Day 2 — Tasks · Networking & API Client

**Layer:** Data · **Goal:** A reusable, intercepted Dio client hitting a real API.

## 🧠 Theory (60–90 min)
- [ ] HTTP request/response lifecycle, headers, status codes (200/4xx/5xx).
- [ ] REST verbs: GET/POST/PUT/PATCH/DELETE — when each is used.
- [ ] Auth: JWT vs Bearer token vs refresh token (just the concepts today).

## 🛠️ Build (3–3.5 hr) — `lib/core/network/dio_client.dart`
- [ ] Pick a free test API (reqres.in / jsonplaceholder) and set `baseUrl`.
- [ ] Configure `BaseOptions`: timeouts, default headers.
- [ ] Add a **logging interceptor**.
- [ ] Add an **auth interceptor** that injects `Authorization: Bearer <token>` (token can be a stub for now).
- [ ] Add an **error interceptor** that detects 401 / timeout / connection errors.
- [ ] Add basic **retry** on timeout (max 2 retries).
- [ ] Make a real GET call from `TaskRemoteDataSource` and print the result.

## 📝 Document — copy `_TEMPLATES/daily_doc_template.md` → `day 2/`
- [ ] Interceptor order + why order matters.
- [ ] The auth header flow diagram.

## ✅ Definition of Done
- [ ] A real API call succeeds and logs. [ ] 401/timeout handled. [ ] Doc done.

## 🔁 Recall test
- [ ] Explain what an interceptor is and give 3 real uses.

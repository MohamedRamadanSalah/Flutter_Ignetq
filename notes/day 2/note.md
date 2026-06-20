# Day 2 Notes — Networking & the API Client

> The day the app learned to talk to the outside world — through **one configured front door**.

---

## 1. The Core Idea: One Front Door 🚪

Instead of scattering `Dio().get(...)` calls all over the app, you build **one** configured `Dio` instance that the whole app shares. Every request walks through the same hallway of **interceptors**.

**Why it matters:** headers, auth, logging, timeouts, retries, and error translation are all **cross-cutting concerns**. Handle them **once**, in one place. If the API adds a required header tomorrow, you edit **one file** — not 30.

> **Mental model:** An interceptor is a *security guard standing in a hallway*. Every request leaving the building, and every response coming in, must walk past the guards. They stamp passports (add token), write in the logbook (logging), and turn away troublemakers (errors).

---

## 2. HTTP in 30 Seconds 📡

Every network call is a **request → response** round trip. On every response you read two things:

- **Status code** (a number)
- **Body** (usually JSON)

### Status code cheat sheet
| Code | Meaning | Who's to blame |
|---|---|---|
| 200 / 201 | OK / Created | nobody — celebrate |
| 400 | Bad Request | you sent garbage |
| 401 | Unauthorized | no/expired token → **refresh** |
| 403 | Forbidden | logged in, but not allowed |
| 404 | Not Found | wrong URL or deleted resource |
| 422 | Unprocessable | validation failed |
| 500 | Server Error | backend crashed |

**Rule of thumb:** `2xx` = success · `4xx` = YOUR fault · `5xx` = SERVER's fault.

### REST verbs (the grammar of talking to a server)
| Verb | Job | Idempotent? |
|---|---|---|
| GET | read | ✅ yes (safe to retry) |
| POST | create | ❌ no (retrying may duplicate) |
| PUT | replace | ✅ yes |
| PATCH | partial update | usually |
| DELETE | remove | ✅ yes |

---

## 3. Interceptors — The Heart of Day 2

An interceptor has **three hooks**. Knowing *when* each fires is everything:

```
onRequest  →  fires BEFORE the request leaves the phone   (add headers/token)
   🌐 network call happens here  (this is where 401/timeout/reset occur)
onResponse →  fires on SUCCESS, on the way back            (unwrap data)
onError    →  fires on FAILURE, on the way back            (translate / retry)
```

> ⚠️ **Biggest lesson of the day:** A network error (401, timeout, connection reset) can **only** be caught in `onError` — **never** in `onRequest`, because at `onRequest` time the request hasn't even been sent yet. (I made this mistake — put error handling in `onRequest`; it was dead code.)

### The two rules every interceptor MUST follow
1. **Always signal the handler.** Every hook you override must call `handler.next(...)`, `handler.resolve(...)`, or `handler.reject(...)`. If you override a hook and do nothing → the request **hangs forever** (or the error vanishes into a black hole).
2. **Call the signal exactly once.** Calling `handler.next()` twice throws *"Cannot add new event after closing."* (I hit this when I called `handler.next()` inside an `if` AND `super.onRequest()` afterward — `super` calls `next` again.)

### Why order matters
```
Request → 1️⃣ Auth (add token) → 2️⃣ Log (print the STAMPED request) → 🌐
Response ← 4️⃣ Error (translate) ← 3️⃣ Retry (re-send on timeout) ← 🌐
```
- **Auth before Log** → so the log shows the *final* request **with** the `Authorization` header. Log first = you'd log the request before the token was attached (misleading debugging).

---

## 4. The Four Interceptors I Built

### 1️⃣ AuthInterceptor — stamps the token (`onRequest`)
```dart
class AuthInterceptor extends Interceptor {
  AuthInterceptor(this._tokenProvider);
  final String Function() _tokenProvider;   // injected — DI, not hardcoded

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    final token = _tokenProvider();
    if (token.isNotEmpty) {
      options.headers['Authorization'] = 'Bearer $token';  // add header conditionally
    }
    handler.next(options);  // ALWAYS wave through — even with no token (login needs to pass)
  }
}
```
**Key insight:** the **header is optional**, but the **"GO" signal (`handler.next`) is not.** Adding the header lives inside the `if`; `handler.next` lives outside it.

### 2️⃣ LogInterceptor — built into Dio
```dart
LogInterceptor(requestBody: true, responseBody: true)
```
⚠️ **Trap:** never log tokens/bodies in **production** — strip in release builds (security leak).

### 3️⃣ RetryInterceptor — retries transient timeouts (`onError`)
```dart
class RetryInterceptor extends Interceptor {
  RetryInterceptor(this._dio, {this.maxRetries = 2});  // Dio injected so it can RE-SEND
  final Dio _dio;
  final int maxRetries;

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    final options = err.requestOptions;
    final retries = options.extra['retries'] ?? 0;   // count stored in the request's scratchpad

    if (_shouldRetry(err) && retries < maxRetries) {  // GUARD: only safe, transient failures
      try {
        final response = await _dio.fetch(options..extra['retries'] = retries + 1); // re-send
        handler.resolve(response);   // success → hand back the good Response
      } catch (e) {
        handler.next(e is DioException ? e : DioException(requestOptions: options, error: e));
      }
    } else {
      handler.next(err);  // give up → forward the error
    }
  }

  bool _shouldRetry(DioException err) =>
      err.type == DioExceptionType.connectionTimeout ||
      err.type == DioExceptionType.sendTimeout ||
      err.type == DioExceptionType.receiveTimeout;
}
```
**Three things I learned the hard way:**
- **`_dio.fetch(requestOptions)` re-sends the request and returns a `Response`.** You can't fake a `Response` by casting an `Options` — they are different types.
- **Count attempts in `options.extra`** (a per-request scratchpad that travels with the request) — the interceptor itself has no memory between fires.
- **Never retry blindly.** Only retry **idempotent + transient** failures (timeouts, 5xx on GET). **Never retry a POST** — if the server *created* the resource but the *response* timed out, retrying creates a **duplicate**. Never retry a 4xx — your request is wrong; retrying sends the same garbage.

### 4️⃣ ErrorInterceptor — observes + forwards (`onError`)
```dart
class ErrorInterceptor extends Interceptor {
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    final code = err.response?.statusCode;
    print('🔴 [ErrorInterceptor] type=${err.type} status=$code uri=${err.requestOptions.uri}');
    handler.next(err);  // forward — the data source still does the real translation
  }
}
```
**Design decision:** translation into typed exceptions stays in the **data source** (single source of truth). The interceptor just gives **one central place to observe every failure** — no duplicated translation logic.

### Wiring it all together — `buildDio()`
```dart
dio.interceptors.add(AuthInterceptor(() => 'fake-jwt-token-123'));
dio.interceptors.add(LogInterceptor(requestBody: true, responseBody: true));
dio.interceptors.add(RetryInterceptor(dio, maxRetries: 2));
dio.interceptors.add(ErrorInterceptor());
```

---

## 5. The Auth + Refresh Flow (the 401 dance) 🔐

When a request gets a **401**, a smart client doesn't just fail — it silently refreshes and retries:

```
Code → GET /tasks (with token)
API  → 401 Unauthorized 🔴
App  → POST /refresh (refresh token)
API  → new access token ✅  → save to secure storage
App  → retry GET /tasks → 200 + data ✅  (user never noticed!)
```

**Senior details (interview gold):**
- Add an **infinite-loop guard flag** so a 401 *on the refresh call itself* doesn't loop forever.
- **Queue concurrent requests** during refresh so they all retry once with the new token.

**Where to store tokens:** `flutter_secure_storage` → Keychain (iOS) / Keystore / EncryptedSharedPreferences (Android). **Never** `SharedPreferences` or a plain DB — those are plain text and readable on rooted/jailbroken devices.

---

## 6. Error Translation at the Border 🛂

Raw library errors must **not** leak inward (Day 1 rule). The data source converts `DioException` into our typed exceptions immediately:

```dart
on DioException catch (e) {
  if (e.response?.statusCode == 401) throw UnauthorizedException();
  if (e.type == DioExceptionType.connectionError) throw NetworkException();
  throw ServerException(e.message ?? 'Request failed');
}
```

**The full chain:** `DioException → your Exception → Failure → friendly UI message.`
Each layer speaks its own language. This is why my app showed a polite *"Error:"* text instead of **crashing** when the network died — the error was *caught and translated at every border*, never left unhandled. **A crash = an error nobody caught.**

---

## 7. Real-World Lessons From Today 🌍

### Lesson A — The API shape changed, and only the data layer cared
`jsonplaceholder` (bare array, field `title`) vs `dummyjson` (wrapped in `{ "todos": [...] }`, field `todo`):
- I only edited the **DTO** and the **data source**. My `Task` entity, repository, providers, and UI stayed **untouched**.
- **Why?** The UI depends on the **`Task` entity** (a stable contract), *not* on the API's JSON. The **mapper** absorbs the difference. *"The API's shape never escapes the data layer."* Karim (raw JSON in widgets) edits 20 files; I edited 2.

### Lesson B — `int` vs `String` at the DTO border
`dummyjson` sends `"id": 1` (an **int**), but my entity wants `id` as a **String** (business decision). The fix:
```dart
id: (json['id'] as int).toString(),   // CONVERT, don't cast
```
**`as` casts (and crashes on type mismatch); `.toString()` converts.**

### Lesson C — "Connection reset by peer" was the network, not my code
My request log was perfect (right URL, method, all 3 timeouts), but every call to `jsonplaceholder` got `Connection reset by peer`. Running `curl` from the dev machine reproduced it → **DNS resolved fine, but TLS handshake was reset** = classic **SNI-based filtering** by the network/ISP. The browser dodged it (encrypted DNS / different route); direct clients (curl, Flutter) got reset. **Fix: switch to an unblocked host (`dummyjson.com`).** Lesson: when one app fails but the browser works on the same network, suspect **proxy / SNI filtering**, not your code.

---

## 8. Common Traps ⚠️
- Creating a **new Dio per request** → lose interceptors, config, connection reuse.
- **No timeouts** → app hangs forever on bad network. (Set all 3: connect/send/receive.)
- **Logging tokens in production** → security leak.
- **Infinite refresh loop** → 401 on the refresh call retries forever → add a guard flag.
- **Letting `DioException` reach the UI** → translate at the border, always.
- **Retrying a POST** → duplicate creation.
- **Overriding a hook without signalling the handler** → request hangs / error vanishes.

---

## 9. Interview Vault 🏢
- **Q: Token refresh on 401?** Auth interceptor catches 401 → refresh → store new token → retry original request, transparently. Add **loop guard** + **queue concurrent requests**.
- **Q: Where store tokens / why not SharedPreferences?** `flutter_secure_storage` (Keychain/Keystore). SharedPreferences is plain text → readable on rooted devices.
- **Q: connect vs send vs receive timeout?** connect = establish TCP/TLS · send = upload body · receive = download response.
- **Q: Why interceptors over per-call handling?** DRY + single source of truth for cross-cutting concerns.
- **Q: When to retry?** Only idempotent + transient (timeouts, 5xx on GET), capped + backoff. Never POST, never 4xx.
- **Q: How to make networking testable?** Depend on the data-source interface, inject Dio, use a mock Dio / `http_mock_adapter` — no real network in tests.

---

## 10. The One Sentence To Remember 🧠

> **"All traffic flows through one configured client, where interceptors add the token, log the call, retry on failure, and translate every raw error into a typed one — so the rest of the app never touches networking details."**

➡️ **Next (Day 3):** the data arrives as messy JSON → build **DTOs and mappers** (with `freezed` + `json_serializable`) to turn it into clean, type-safe entities.

---
---

# 📦 IMPORTANT — Classes & Their Uses in Day 2

> A reference of every class/type touched today, what it is, and why it exists.

## Classes I wrote

| Class | File | Extends / Type | Job | Key method |
|---|---|---|---|---|
| `AuthInterceptor` | `core/network/interceptors/auth_interceptor.dart` | `Interceptor` | Adds `Authorization: Bearer <token>` to every outgoing request | `onRequest()` |
| `RetryInterceptor` | `core/network/interceptors/retry_interceptor.dart` | `Interceptor` | Re-sends the request (max 2×) on transient timeouts | `onError()` + `_shouldRetry()` |
| `ErrorInterceptor` | `core/network/interceptors/error_interceptor.dart` | `Interceptor` | Centrally observes/logs every failure, then forwards it | `onError()` |

## Dio classes/types I used (provided by the `dio` package)

| Type | What it is | Why it matters |
|---|---|---|
| `Dio` | The HTTP client itself. **One shared, configured instance.** | The "front door." `dio.get/post/fetch(...)` send requests. `dio.interceptors.add(...)` registers guards. |
| `BaseOptions` | Default config for every request | `baseUrl`, `connectTimeout`, `sendTimeout`, `receiveTimeout`, default `headers`. |
| `Interceptor` | Base class for all interceptors | Override `onRequest` / `onResponse` / `onError`. **You extend this.** |
| `RequestOptions` | Description of a single outgoing request | Mutable: `headers`, `method`, `uri`, and **`extra`** (per-request scratchpad — I stored the retry count here). |
| `Options` | A lighter request-config object | ⚠️ **NOT** a `Response`. Don't confuse them — casting one to the other crashes. |
| `Response<T>` | The server's reply | What `dio.fetch()` returns; what `handler.resolve(response)` needs. Read `response.data`, `response.statusCode`. |
| `DioException` | Dio's error type | Read `err.type` (e.g. `connectionTimeout`, `receiveTimeout`, `connectionError`) and `err.response?.statusCode`. **Translate it — don't let it leak to UI.** |
| `DioExceptionType` | Enum of failure kinds | `connectionTimeout` / `sendTimeout` / `receiveTimeout` / `connectionError` / `badResponse` … used in `_shouldRetry`. |
| `RequestInterceptorHandler` | The "traffic controller" for `onRequest` | `handler.next(options)` = proceed · `handler.reject(err)` = abort · `handler.resolve(response)` = short-circuit with a fake success. |
| `ErrorInterceptorHandler` | The "traffic controller" for `onError` | `handler.next(err)` = forward error · `handler.resolve(response)` = recover (used after a successful retry) · `handler.reject(err)` = stop. |
| `LogInterceptor` | Built-in interceptor | Logs request/response. Strip in production. |

## The handler methods — the single most important concept

Every interceptor hook receives a **handler**. You **must** call exactly **one** of these, exactly **once**:

| Method | Meaning | When I used it |
|---|---|---|
| `handler.next(x)` | "Continue down the chain." | Auth: proceed after stamping. Error/Retry: forward the error when giving up. |
| `handler.resolve(response)` | "Stop — pretend it succeeded, here's the response." | Retry: after `_dio.fetch()` succeeds. |
| `handler.reject(err)` | "Stop — fail with this error." | (Not used today, but the way to abort a request from inside an interceptor.) |

> 🔑 **Golden rule:** override a hook → you OWN the flow → you MUST signal the handler once. Forget it → hang. Do it twice → crash.

## Dependency Injection pattern (repeated today)
Both `AuthInterceptor` (token provider) and `RetryInterceptor` (the `Dio` instance) take their dependencies through the **constructor** instead of hardcoding them. This is the **Dependency Inversion** muscle from Day 1 — the interceptor doesn't care *where* the token comes from, so I can swap the stub for real secure storage later **without touching the interceptor**.

# 📖 Day 2 — Networking & the API Client
### *The chapter where your app learns to talk to the outside world*

---

## 1. The Story 🌐

Your TaskFlow app is a brilliant brain in a sealed jar. It has entities, contracts, use cases — but it has never spoken to anyone. Today we give it a **mouth and ears**.

But here's the trap most beginners fall into. **Karim** writes `Dio().get('https://api.com/tasks')` directly in every data source. Then the API adds a required header. He edits 30 files. Then the token needs to be attached to every request. 30 more edits. Then the API starts returning 401 when the token expires. He has no central place to catch it. His networking is **30 separate mouths all shouting differently**.

The professional move: build **one** configured front door — an **API client** — that every request passes through. Headers, auth, logging, timeouts, retries, error translation: all handled **once**, in one place. That front door is what we build today.

---

## 2. The Big Picture: HTTP in 30 Seconds 📡

Before the client, understand the conversation it manages. Every network call is a **request → response** round trip.

```mermaid
sequenceDiagram
    participant App as 📱 Your App
    participant Server as 🖥️ Server
    App->>Server: REQUEST<br/>(method + URL + headers + body)
    Note over Server: processes,<br/>checks auth,<br/>queries DB
    Server-->>App: RESPONSE<br/>(status code + headers + body)
    Note over App: read status,<br/>parse body
```

**The two things you read on every response:**

```mermaid
flowchart TD
    R["HTTP Response"] --> S["Status Code (a number)"]
    R --> B["Body (usually JSON)"]
    S --> S2["2xx ✅ success"]
    S --> S4["4xx 🙋 YOUR fault (bad request, no auth)"]
    S --> S5["5xx 💥 SERVER's fault"]

    style S2 fill:#d4edda
    style S4 fill:#fff3cd
    style S5 fill:#f8d7da
```

**The status-code cheat sheet you must memorize:**

| Code | Meaning | Who's to blame |
|---|---|---|
| 200 / 201 | OK / Created | nobody — celebrate |
| 400 | Bad Request | you sent garbage |
| 401 | Unauthorized | no/expired token → **refresh** |
| 403 | Forbidden | logged in, but not allowed |
| 404 | Not Found | wrong URL or deleted resource |
| 422 | Unprocessable | validation failed |
| 500 | Server Error | backend crashed |

**The REST verbs** — the "grammar" of talking to a server:

```mermaid
flowchart LR
    GET["GET<br/>read"] -.-> DB[(Resource)]
    POST["POST<br/>create"] --> DB
    PUT["PUT<br/>replace"] --> DB
    PATCH["PATCH<br/>partial update"] --> DB
    DELETE["DELETE<br/>remove"] --> DB
```

---

## 3. The Critical Idea: One Front Door 🚪

Instead of scattered `Dio()` calls, you build **one** configured `Dio` instance that the whole app shares. Every request walks through the same hallway of **interceptors**.

```mermaid
flowchart LR
    Code["Your data source<br/>dio.get('/tasks')"] --> I1
    subgraph HALL["The Interceptor Hallway"]
        direction LR
        I1["1️⃣ Auth<br/>add token"] --> I2["2️⃣ Logging<br/>print request"] --> I3["3️⃣ Retry<br/>on timeout"]
    end
    I3 --> NET["🌐 Network"]
    NET --> I4["4️⃣ Error<br/>map 401/timeout"]
    I4 --> Back["Response or typed error<br/>back to your code"]

    style HALL fill:#d1ecf1,stroke:#0c5460
```

> **Mental model 🚪:** An interceptor is a *security guard standing in a hallway*. Every request that wants to leave the building, and every response that wants to come in, must walk past the guards. The guards stamp passports (add token), write in the logbook (logging), and turn away troublemakers (errors).

---

## 4. Interceptors — The Heart of Today

An interceptor has three hooks. Understanding *when* each fires is everything:

```mermaid
sequenceDiagram
    participant C as Your Code
    participant I as Interceptor
    participant N as Network
    C->>I: dio.get()
    I->>I: 🔵 onRequest<br/>(add headers/token)
    I->>N: send
    N-->>I: response
    alt success
        I->>I: 🟢 onResponse<br/>(unwrap data)
        I-->>C: data
    else failure
        I->>I: 🔴 onError<br/>(map to typed exception,<br/>maybe retry/refresh)
        I-->>C: typed error
    end
```

**The order of interceptors matters.** Think about it logically:

```mermaid
flowchart TD
    A["Auth interceptor FIRST"] --> B["because the request needs<br/>a token before anything else"]
    C["Logging AFTER auth"] --> D["so the log shows the<br/>final request with headers"]
    E["Error interceptor catches"] --> F["the response on the way back<br/>— translate 401 → refresh"]
```

### The auth + refresh flow (the trickiest part)

When a request gets a **401**, a smart client doesn't just fail — it silently gets a fresh token and retries:

```mermaid
sequenceDiagram
    participant C as Code
    participant A as Auth Interceptor
    participant API as API
    participant S as Secure Storage
    C->>A: GET /tasks
    A->>S: read access token
    A->>API: GET /tasks (Bearer token)
    API-->>A: 401 Unauthorized 🔴
    A->>API: POST /refresh (refresh token)
    API-->>A: new access token ✅
    A->>S: save new token
    A->>API: retry GET /tasks
    API-->>A: 200 + data ✅
    A-->>C: data (user never noticed!)
```

> **Critical idea 💡:** Good networking is *invisible*. The user should never see "session expired" for a recoverable problem. The refresh dance happens behind the curtain.

---

## 5. Translate Errors at the Border 🛂

Dio throws `DioException`. But remember Day 1's rule: **raw library errors must not leak inward.** So the error interceptor / data source converts them into *your* typed exceptions immediately.

```mermaid
flowchart LR
    DE["DioException"] --> Q{type?}
    Q -->|401| UE["UnauthorizedException"]
    Q -->|connection/timeout| NE["NetworkException"]
    Q -->|4xx/5xx| SE["ServerException"]

    style UE fill:#fff3cd
    style NE fill:#f8d7da
    style SE fill:#f8d7da
```

These exceptions later become `Failure`s at the repository (Day 6). The chain is: **DioException → your Exception → Failure → friendly UI message.** Each layer speaks its own language.

---

## 6. How This Maps to TaskFlow 🧩

Today you grow `lib/core/network/dio_client.dart` from a stub into a real client:

```mermaid
flowchart TD
    BD["buildDio()"] --> BO["BaseOptions<br/>baseUrl, timeouts, headers"]
    BD --> IA["AuthInterceptor<br/>onRequest: add Bearer"]
    BD --> IL["LogInterceptor"]
    BD --> IR["RetryInterceptor<br/>on timeout, max 2"]
    BD --> IE["ErrorInterceptor<br/>onError: map exceptions"]
    BD --> USE["TaskRemoteDataSource uses it"]

    style BD fill:#d4edda
```

Pick a free practice API today: **reqres.in** or **jsonplaceholder.typicode.com** — point `baseUrl` at it and make a real GET succeed.

---

## 7. Common Traps ⚠️

```mermaid
mindmap
  root((Day 2 Traps))
    Creating a new Dio per request
      Lose interceptors, config, connection reuse
    No timeouts
      App hangs forever on bad network
    Logging tokens in production
      Security leak — strip in release
    Infinite refresh loop
      401 on the refresh call retries forever → add a guard flag
    Letting DioException reach the UI
      Translate at the border, always
```

---

## 8. What You Must Be Able To Do By Tonight ✅

- [ ] Explain request/response + read any status code's meaning.
- [ ] Explain what an interceptor is and give the 4 you built.
- [ ] Draw the 401 → refresh → retry sequence from memory.
- [ ] Make a real GET call through your client and see it logged.
- [ ] Explain why a single shared Dio beats scattered `Dio()` calls.

---

## 9. 🏢 Interview Vault — Questions From Top Middle East Companies
> *Networking + auth questions are heavy at delivery/fintech companies — Careem, Talabat, Noon, Tabby, Tamara, Jahez — because their apps live or die on flaky mobile networks.*

```mermaid
mindmap
  root((What they probe<br/>on Day 2 topics))
    Token lifecycle
      refresh, storage, 401 handling
    Resilience
      timeouts, retries, offline
    Interceptors
      do you know what runs when
    Security
      where do you store tokens
```

**Q1. How do you handle token refresh on a 401?**
> **A:** An auth interceptor catches the 401, calls the refresh endpoint with the refresh token, stores the new access token securely, and retries the original request — transparently to the user. I add a guard flag so a 401 on the refresh call itself doesn't cause an infinite loop, and I queue concurrent requests during refresh so they all retry once with the new token.
> *🎯 Really testing:* the **infinite-loop guard** and **concurrent-request queueing** — that's the senior-level detail juniors miss.

**Q2. Where do you store the access and refresh tokens, and why not SharedPreferences?**
> **A:** In `flutter_secure_storage` (Keychain on iOS, Keystore/EncryptedSharedPreferences on Android). SharedPreferences is plain text and readable on rooted/jailbroken devices, so storing tokens there is a security risk.
> *🎯 Really testing:* security awareness.

**Q3. What's the difference between `connectTimeout`, `sendTimeout`, and `receiveTimeout`?**
> **A:** `connectTimeout` = time to establish the TCP/TLS connection; `sendTimeout` = time to upload the request body; `receiveTimeout` = time to download the response. Setting all three prevents the app from hanging indefinitely on a bad network.
> *🎯 Really testing:* practical Dio depth.

**Q4. Why use interceptors instead of handling headers/errors in each call?**
> **A:** DRY and a single source of truth. Auth, logging, retry, and error translation are cross-cutting concerns — putting them in one interceptor chain means one place to change, consistent behavior everywhere, and data sources that stay clean.
> *🎯 Really testing:* cross-cutting-concern thinking.

**Q5. A request fails. How do you decide whether to retry?**
> **A:** Retry only *idempotent, transient* failures — timeouts and 5xx on GETs — with capped attempts and backoff. Never blindly retry a POST (could double-create) or a 4xx (your request is wrong; retrying won't help).
> *🎯 Really testing:* understanding idempotency and not retrying the wrong things.

**Q6. How would you make networking testable?**
> **A:** Depend on an abstraction (the data source interface), inject the Dio instance, and in tests use a mock Dio or `http_mock_adapter` so no real network is hit. The repository can then be tested against fake responses including error cases.
> *🎯 Really testing:* testability of the network layer.

---

## 10. The One Sentence To Remember 🧠

> **"All traffic flows through one configured client, where interceptors add the token, log the call, retry on failure, and translate every raw error into a typed one — so the rest of the app never touches networking details."**

➡️ **Next chapter (Day 3):** the data arrives as messy JSON. We build **DTOs and mappers** to turn it into clean, type-safe business entities.

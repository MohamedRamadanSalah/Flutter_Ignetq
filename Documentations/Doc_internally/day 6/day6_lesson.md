# 📖 Day 6 — Error Handling & Authentication
### *The chapter where failures become polite messages, and your app learns who you are*

---

## 1. The Story 💥🔐

Two stories today, because they're deeply linked.

**Story 1 — the crash.** A user taps "refresh" in a tunnel. **Tarek's** app throws a raw `DioException` all the way up to the widget. The screen shows a red error overlay with a stack trace. The user thinks the app is broken. It wasn't broken — it just had no internet. Tarek never *translated* the failure into something human.

**Story 2 — the locked door.** TaskFlow needs to know *who* you are before showing your tasks. That means login, storing a token safely, attaching it to every request, and — the tricky part — silently refreshing it when it expires so the user isn't kicked out mid-session.

Today you build two systems that every serious app needs: a **failure pipeline** (so errors are always graceful) and an **auth data layer** (so identity is handled securely).

---

## 2. Error Handling: The Two-Type System 🎯

Remember Day 1: raw exceptions must **never** reach the UI. So we use **two** error types, and translate between them at the repository boundary.

```mermaid
flowchart LR
    subgraph data["🔌 Data layer speaks: Exceptions"]
        DE["DioException"] --> SE["ServerException"]
        DE --> NE["NetworkException"]
        DE --> UE["UnauthorizedException"]
    end
    subgraph domain["🧠 Domain/UI speaks: Failures"]
        SF["ServerFailure"]
        NF["NetworkFailure"]
        UF["UnauthorizedFailure"]
    end
    SE -->|repository maps| SF
    NE -->|repository maps| NF
    UE -->|repository maps| UF

    style data fill:#f8d7da
    style domain fill:#fff3cd
```

> **Mental model 🛂:** Exceptions are the *local dialect* of the data layer — thrown, unpredictable, low-level. Failures are the *official language* of the domain — returned as values, typed, safe. The repository is the **translator** at the border. The UI only ever hears the official language.

### Why `Either<Failure, T>` instead of try/catch everywhere?

```mermaid
flowchart TD
    A["throw exceptions"] --> A1["caller MIGHT forget to catch<br/>→ crash"]
    B["return Either&lt;Failure, T&gt;"] --> B1["compiler FORCES you to handle<br/>both Left (fail) and Right (ok)"]

    style A1 fill:#f8d7da
    style B1 fill:#d4edda
```

`Either` makes the failure a **value you must handle**, not a surprise you might miss. `Left` = failure, `Right` = success ("right" = "correct").

---

## 3. The Full Error Journey 🚀

```mermaid
sequenceDiagram
    participant API
    participant DS as DataSource
    participant R as Repository
    participant UC as UseCase
    participant UI
    API-->>DS: 500 error
    DS->>DS: throw ServerException
    DS-->>R: (exception bubbles)
    R->>R: catch → Left(ServerFailure)
    R-->>UC: Either.Left(ServerFailure)
    UC-->>UI: Either.Left(ServerFailure)
    UI->>UI: fold → show "Something went wrong, try again"
    Note over UI: user sees a friendly message,<br/>never a stack trace
```

---

## 4. Authentication: The Big Picture 🔐

Auth is a lifecycle: get a token, use it, refresh it, throw it away.

```mermaid
stateDiagram-v2
    [*] --> LoggedOut
    LoggedOut --> Authenticating: login(email, pass)
    Authenticating --> LoggedIn: tokens received + stored
    Authenticating --> LoggedOut: invalid credentials
    LoggedIn --> Refreshing: access token expired (401)
    Refreshing --> LoggedIn: new access token
    Refreshing --> LoggedOut: refresh token also expired
    LoggedIn --> LoggedOut: logout (clear tokens)
```

### Token types — know the difference

```mermaid
flowchart TD
    AT["Access Token<br/>short-lived (minutes)<br/>sent on every request"] --> U["used to authorize calls"]
    RT["Refresh Token<br/>long-lived (days/weeks)<br/>stored securely"] --> G["used ONLY to get a new access token"]

    style AT fill:#d1ecf1
    style RT fill:#fff3cd
```

> **Critical idea 💡:** Two tokens exist for *security*. The access token is exposed on every request, so it's short-lived (a stolen one expires fast). The refresh token is precious and rarely transmitted, so it's long-lived. Store **both** in `flutter_secure_storage`, never SharedPreferences.

### The silent refresh (the senior-level detail)

```mermaid
sequenceDiagram
    participant App
    participant Interceptor
    participant API
    App->>Interceptor: GET /tasks
    Interceptor->>API: GET /tasks (access token)
    API-->>Interceptor: 401 (expired) 🔴
    Note over Interceptor: set isRefreshing = true<br/>(guard against loops)
    Interceptor->>API: POST /refresh (refresh token)
    API-->>Interceptor: new access token ✅
    Interceptor->>Interceptor: save token, isRefreshing = false
    Interceptor->>API: retry GET /tasks
    API-->>Interceptor: 200 + data ✅
    Interceptor-->>App: data (seamless)
```

---

## 5. How This Maps to TaskFlow 🧩

```mermaid
flowchart TD
    subgraph core["core/error/"]
        ex["exceptions.dart (all exceptions)"]
        fa["failures.dart (all failures)"]
    end
    subgraph auth["features/auth/"]
        ds["data/datasources/auth_remote_datasource.dart"]
        ri["data/repositories/auth_repository_impl.dart"]
        ss["flutter_secure_storage (tokens)"]
        uc["domain/usecases/login.dart, logout.dart"]
    end
    ri --> ds
    ri --> ss
    ri -->|maps ex→failure| fa

    style core fill:#f8d7da
    style auth fill:#d4edda
```

Today: expand `core/error/` to full exception+failure sets, build the auth feature (login/register/refresh), store tokens securely, wire the auth interceptor to do the silent refresh, and add `User` entity + `Login`/`Logout` use cases.

---

## 6. Common Traps ⚠️

```mermaid
mindmap
  root((Day 6 Traps))
    Letting exceptions reach the UI
      Always translate to Failure first
    Tokens in SharedPreferences
      Insecure — use secure storage
    Infinite refresh loop
      Guard flag + don't refresh the refresh call
    Concurrent 401s triggering many refreshes
      Queue requests, refresh once
    Generic 'Error' message for everything
      Map each Failure to a specific friendly message
    Storing passwords anywhere
      Never store passwords; only tokens
```

---

## 7. 🏢 Interview Vault — Questions From Top Middle East Companies
> *Fintech (Tabby, Tamara, Halan) and any app with accounts grill you on this — security + UX of auth is make-or-break.*

**Q1. Why two error types (Exception and Failure)?**
> **A:** Exceptions are low-level, thrown, and live in the data layer; Failures are typed values returned to the domain/UI. The repository translates exception→failure at the boundary, so raw library errors never leak inward and the UI always handles a clean, expected type.
> *🎯 Really testing:* boundary discipline + the "errors as values" idea.

**Q2. Why `Either<Failure, T>` over throwing?**
> **A:** It makes error handling explicit and compiler-enforced — the caller must handle both `Left` and `Right`. Throwing relies on the caller remembering to catch, which is easy to forget and causes crashes.
> *🎯 Really testing:* functional error-handling maturity.

**Q3. Explain access vs refresh tokens and where you store them.**
> **A:** Access tokens are short-lived and sent on every request; refresh tokens are long-lived and used only to mint new access tokens. Both go in secure storage (Keychain/Keystore). Short access-token lifetime limits damage if intercepted.
> *🎯 Really testing:* security fundamentals.

**Q4. How do you implement silent token refresh, and what can go wrong?**
> **A:** An interceptor catches 401, calls refresh, stores the new token, and retries the original request. Pitfalls: an infinite loop if the refresh call itself 401s (guard with a flag and don't refresh the refresh endpoint), and a refresh storm when many requests 401 at once (queue them and refresh a single time).
> *🎯 Really testing:* the loop guard + concurrency — the senior differentiators.

**Q5. The user's refresh token expires. What's the correct UX?**
> **A:** Treat it as a hard logout: clear stored tokens, reset auth state, and redirect to login — ideally preserving where they were so they return after re-auth. Never show a raw error.
> *🎯 Really testing:* graceful session-expiry handling.

---

## 8. What You Must Be Able To Do By Tonight ✅
- [ ] Explain the exception→failure translation and where it happens.
- [ ] Justify `Either` over throwing.
- [ ] Explain access vs refresh tokens + secure storage.
- [ ] Implement login + silent refresh with a loop guard.
- [ ] Answer interview Q1–Q5 from memory.

## 9. The One Sentence To Remember 🧠
> **"Translate every exception into a typed Failure at the repository boundary so the UI never crashes, and manage identity with short-lived access tokens, securely-stored refresh tokens, and a guarded silent-refresh flow."**

➡️ **Next chapter (Day 7):** we complete the **Domain layer** — pure entities, use cases, and where business rules truly belong.

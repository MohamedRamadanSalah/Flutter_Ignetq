# 🚀 Senior Notes — Clean Architecture, Networking & Production Thinking

## 1. Dependency Inversion Reverses the Arrows
- Compile Time: Data → Domain
- Runtime: Domain → Data
- Compile-time dependency ≠ Runtime dependency

## 2. Clean Architecture Is About Dependencies, Not Folder Structure
The real question is:

> Who depends on whom?

## 3. DTOs Should Never Escape the Data Layer
Correct flow:

```text
JSON → DTO → Entity → UI
```

Not:

```text
JSON → DTO → UI
```

## 4. DTO Is a Boundary Object
A DTO protects your Domain from external systems such as:
- REST APIs
- Databases
- Firebase
- GraphQL
- Cache

## 5. Exceptions vs Failures
Prefer:

```dart
Either<Failure, T>
```

instead of leaking infrastructure exceptions into the Domain layer.

## 6. The Repository Is Responsible for Mapping Exceptions to Failures

```text
DioException     → NetworkFailure
SocketException  → NetworkFailure
TimeoutException → NetworkFailure
```

The Domain should work with Failures, not technical exceptions.

## 7. Organize by Change, Not by Type
Structure code around features rather than file types.

## 8. A Feature Should Be Deletable
A good architectural test:

> Can I remove a feature by deleting a single folder?

If not, coupling is probably too high.

## 9. Teams Scale Through Ownership
Own features, not layers.

Good:

```text
Team A → Auth
Team B → Tasks
Team C → Billing
```

## 10. Vertical Slicing ≠ Clean Architecture
- Vertical Slicing answers: "Where should code live?"
- Clean Architecture answers: "Who depends on whom?"

## 11. Architecture Is an Economic Decision
Architecture is always a trade-off between cost and future flexibility.

## 12. Architecture Serves Change
Good architecture makes future changes cheaper and safer.

---

# 🌐 Networking & Dio

## 13. Interceptors Are Middleware

```text
Request → Interceptor → Network → Interceptor → Response
```

## 14. Middleware Order Is Behavior
Changing interceptor order changes system behavior.

## 15. Logging Should Observe the Final Request
If you want accurate logs, log the request after important mutations.

## 16. A Misleading Log Is Worse Than No Log
Bad logs waste debugging time and create false assumptions.

## 17. Cross-Cutting Concerns Form a Pipeline
Examples:
- Authentication
- Retry
- Logging
- Metrics
- Caching
- Error Mapping

## 18. onError Is a Hook, Not an Interceptor Type
Every interceptor may contain:
- onRequest
- onResponse
- onError

---

# 🔑 HTTP Status Codes

## 19. Understanding 400, 401, and 403

```text
400 = Your request is invalid.
401 = I don't know who you are.
403 = I know who you are, but you're not allowed.
```

---

# 🔐 Authentication & Tokens

## 20. The Refresh Token Is the Last Line of Defense

```text
Access Token Expired
        ↓
Refresh Token Saves the Session
```

## 21. Refresh Failure Is an Authentication State Change

```text
Authenticated → Unauthenticated
```

## 22. Never Intercept Your Own Recovery Request
Otherwise you risk creating an infinite refresh loop.

## 23. Recovery Logic Needs an Escape Hatch
Every recovery mechanism must have a stop condition.

## 24. Failure Paths Deserve Design
Design failure flows with the same care as success flows.

---

# ⚡ Concurrency & Production Thinking

## 25. One Dio Instance ≠ One Request
A single Dio instance can execute many concurrent requests.

## 26. Token Refresh Must Be Coordinated

```text
401 + 401 + 401
        ↓
   One Refresh
        ↓
   Many Waiters
```

## 27. One Refresh, Many Waiters
Use a shared Future so all requests wait for the same refresh operation.

## 28. Refresh Storm
Multiple refresh requests running simultaneously can create serious production issues.

## 29. Race Conditions Are Often Invisible Locally
Many concurrency bugs only appear under real traffic and real users.

## 30. The Hardest Bugs Are Concurrency Bugs
Code that looks correct can fail under concurrent execution.

---

# ⏱️ Timeouts

## 31. Connect Timeout
Failed to establish a connection to the server.

## 32. Send Timeout
Failed to send data within the configured time limit.

## 33. Receive Timeout
The connection succeeded, but the server took too long to respond.

```text
Connect → Reaching the server
Send    → Sending data
Receive → Waiting for a response
```

---

# 🎯 Golden Rule

> Good architecture is not about making today's code look clean.
>
> It's about making tomorrow's changes cheap.

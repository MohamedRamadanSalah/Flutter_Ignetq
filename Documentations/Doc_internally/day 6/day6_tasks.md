# Day 6 — Tasks · Error Handling System & Auth Data Layer

**Layer:** Data · **Goal:** A complete Exception→Failure system + working auth.

## 🧠 Theory (60–90 min)
- [ ] Exception hierarchy vs Failure abstraction (why two types).
- [ ] Mapping exceptions → failures at the repository boundary.
- [ ] Auth: login/register, session, token storage, refresh-token flow, logout.

## 🛠️ Build (3–3.5 hr) — `features/auth/`
- [ ] Expand `core/error/` with all exceptions + matching failures.
- [ ] Build `AuthRemoteDataSource` (login/register/refresh).
- [ ] Store tokens with `flutter_secure_storage`.
- [ ] Build `AuthRepositoryImpl` returning `Either<Failure, User>`.
- [ ] Wire the **auth interceptor** to read the real stored token + auto-refresh on 401.
- [ ] Add `User` entity + `Login` / `Logout` use cases.

## 📝 Document — copy template → `day 6/`
- [ ] Exception→Failure mapping table.
- [ ] Auth + refresh-token sequence diagram.

## ✅ Definition of Done
- [ ] Login stores tokens. [ ] 401 triggers refresh. [ ] Every error maps to a Failure.

## 🔁 Recall test
- [ ] Explain why exceptions never reach the UI in this architecture.

# Flutter Mastery — 15-Day Master Plan (2026 Level)

> **Profile:** Intermediate Flutter/Dart · 5–6 focused hours/day · One capstone app built layer-by-layer
> **State management focus:** Riverpod 2.x (code-generation `@riverpod` style)
> **Architecture:** Clean Architecture — Data → Domain → Presentation (with Riverpod as the presentation/state bridge)

---

## 1. The North Star

By **Day 15** you can design and build any Flutter feature from scratch — clean Data layer, pure Domain layer, robust Riverpod state, and a reactive UI — *without copying tutorials*, and explain every decision in an interview.

You do not "study Flutter." You **build one real production app**, one layer at a time, and document every concept the moment you implement it.

---

## 2. The Capstone — "TaskFlow" (Team Task Manager)

A single app carries you through all 15 days. It is chosen because it naturally forces every layer and every Riverpod pattern.

| Feature | Forces you to learn |
|---|---|
| Login / Register / token refresh | Auth data layer, secure storage, interceptors |
| Projects & Tasks lists (infinite scroll) | Pagination (cursor), repository, caching |
| Task detail + create/edit forms | Domain use cases, form state in Riverpod |
| Works offline, syncs when online | Local data source, offline-first, sync queue |
| Search & filter tasks | Debounce/throttle, derived providers |
| Live task status updates | Streams, `StreamProvider`, WebSocket data source |
| Attach a file / avatar | Multipart upload, progress tracking |
| Pull-to-refresh, optimistic updates | `AsyncNotifier`, error/loading state |

> **Don't like task managers?** Swap to an e-commerce client or a recipes app — the layer mapping is identical. Pick one and commit on Day 1.

---

## 3. Phase Map

| Phase | Days | Layer |
|---|---|---|
| 0 — Foundation | Day 1 | Clean Architecture + project skeleton + Domain contracts |
| 1 — Data Layer | Days 2–6 | Networking, DTOs, repositories, local/cache, offline, pagination, errors, auth |
| 2 — Domain Layer | Day 7 | Entities, use cases, failures, business rules |
| 3 — Riverpod State | Days 8–11 | Providers, AsyncNotifier, async state, advanced patterns, testing |
| 4 — UI Layer | Days 12–14 | Widgets, screens, navigation, forms, performance |
| 5 — Integration & Hardening | Day 15 | End-to-end wiring, testing, docs review, capstone polish |

> **Why Domain contracts on Day 1 but use cases on Day 7?** In Clean Architecture the Domain is the *center* — Data depends on it. You define the *interfaces* (contracts) first so the Data layer has something to implement, then fill in the business logic once data flows.

---

## 4. Daily Rhythm (your 5–6 hours)

Every day follows the same loop so it becomes a habit:

1. **Theory block (60–90 min)** — read the day's concepts, watch one focused resource, take notes in `Doc_internally/day N`.
2. **Build block (3–3.5 hrs)** — implement the day's deliverable in the capstone. Code > notes.
3. **Documentation block (45–60 min)** — fill the daily doc template: what it is, why, how, gotchas, and 3 interview questions you can now answer.
4. **Recall (15 min)** — close your notes and explain the day's concept out loud or in writing from memory.

**Definition of Done each day:** the deliverable compiles/runs **and** the daily doc is complete **and** you passed your own recall test.

---

## 5. The 15 Days

### PHASE 0 — FOUNDATION

#### Day 1 — Clean Architecture & Project Skeleton
- **Theory:** Clean Architecture, the Dependency Rule, layer boundaries, dependency inversion, folder-by-feature structure.
- **Build:**
  - Create the project + folder structure (`core/`, `features/<feature>/{data,domain,presentation}`).
  - Add base packages: `dio`, `riverpod`/`flutter_riverpod`/`riverpod_annotation`, `freezed`, `json_serializable`, `go_router`, `flutter_secure_storage`, `hive` (or `isar`), `mocktail`.
  - Define **Domain contracts**: `Task`/`Project` entities (skeleton), abstract `TaskRepository`, `Failure` base type.
  - Set up `ProviderScope` in `main.dart`.
- **Doc:** Architecture diagram + dependency-rule notes + folder convention.

---

### PHASE 1 — DATA LAYER (Days 2–6)

#### Day 2 — Networking & API Client
- **Theory:** HTTP lifecycle, REST verbs, status codes, headers, JWT/Bearer/refresh tokens.
- **Build:** Reusable `DioClient` — `BaseOptions`, logging interceptor, auth interceptor, timeout & retry, error interceptor that converts `DioException` → typed exceptions.
- **Doc:** API client design + interceptor order + auth flow.

#### Day 3 — DTOs, Serialization & Mapping
- **Theory:** DTO vs Entity, why models must not leak into Domain, nested/nullable JSON, API evolution.
- **Build:** `TaskDto`/`ProjectDto` with `freezed` + `json_serializable`; `Mapper`s for DTO ↔ Entity. Run `build_runner`.
- **Doc:** DTO vs Entity table + mapping pattern + codegen workflow.

#### Day 4 — Repository + Remote/Local Data Sources
- **Theory:** Repository as single source of truth, remote/local coordination, data-source contracts.
- **Build:** `RemoteDataSource` (Dio calls) + `LocalDataSource` (Hive/Isar) + `TaskRepositoryImpl` coordinating both.
- **Doc:** Repository responsibilities + data-source split + flow diagram.

#### Day 5 — Caching, Offline-First & Pagination
- **Theory:** Cache strategies (cache-first, network-first, stale-while-revalidate), invalidation/expiry, offline-first sync, cursor pagination.
- **Build:** Cache manager + offline read path + a sync queue stub + cursor-based paginated task fetch.
- **Doc:** Cache strategy decision tree + pagination notes.

#### Day 6 — Error Handling & Auth Data Layer
- **Theory:** Exception hierarchy, `Failure` abstraction, exception→failure mapping, refresh-token flow, secure token storage.
- **Build:** Full exception/`Failure` system (`Either<Failure, T>` via `dartz` or sealed classes) + `AuthRepository` with login/refresh/logout + secure storage.
- **Doc:** Exception→Failure mapping table + auth/refresh sequence diagram.

---

### PHASE 2 — DOMAIN LAYER (Day 7)

#### Day 7 — Entities, Use Cases & Business Rules
- **Theory:** Why Domain is pure Dart (no Flutter/Dio imports), use case (interactor) pattern, single-responsibility use cases, where business rules live.
- **Build:** Finalize entities; implement use cases: `GetTasks`, `CreateTask`, `ToggleTaskDone`, `Login`, `SearchTasks`. Each returns `Either<Failure, T>`.
- **Doc:** Use case pattern + the dependency direction proof + "what belongs in Domain vs Data."

---

### PHASE 3 — RIVERPOD STATE MANAGEMENT (Days 8–11)  ⭐ your focus

#### Day 8 — Riverpod Foundations
- **Theory:** Why Riverpod (vs Provider/Bloc), `ProviderScope`, `ref` (`watch`/`read`/`listen`), provider lifecycle, `autoDispose`, `family`, code-gen `@riverpod`.
- **Build:** Wire dependency providers (dio, storage, data sources, repositories, use cases) with `@riverpod`. Simple `Provider`/`FutureProvider` for a first task list.
- **Doc:** Provider type cheat-sheet + watch vs read vs listen + when to use family/autoDispose.

#### Day 9 — Async State with AsyncNotifier
- **Theory:** `AsyncValue` (data/loading/error), `AsyncNotifier`/`Notifier`, `AsyncNotifierProvider`, `FutureProvider`, `StreamProvider`, mutation + `ref.invalidate`.
- **Build:** `TaskListNotifier extends AsyncNotifier` — load, refresh, create (optimistic), toggle, delete. Live updates via `StreamProvider`.
- **Doc:** `AsyncValue` handling patterns + optimistic update recipe.

#### Day 10 — Composition & Advanced Patterns
- **Theory:** Combining/derived providers, dependent providers, `keepAlive`, caching with Riverpod, debounced search, `ref.listen` side effects, scoping & overrides.
- **Build:** Debounced search provider, filtered/derived task provider, paginated list notifier, cross-provider dependencies.
- **Doc:** Derived-provider patterns + debounce recipe + caching/keepAlive notes.

#### Day 11 — Testing Riverpod & Forms State
- **Theory:** `ProviderContainer`, overriding providers in tests, testing notifiers, form state management in Riverpod, error/validation state.
- **Build:** Unit-test 3+ providers with mocked repositories (mocktail + overrides). Build create/edit task **form state** with validation in a `Notifier`.
- **Doc:** Provider testing template + form-state pattern.

---

### PHASE 4 — UI LAYER (Days 12–14)

#### Day 12 — Widgets, Screens & Consuming Providers
- **Theory:** `ConsumerWidget`/`ConsumerStatefulWidget`, `ref.watch` in build, rebuild scoping with `select`, `when`/`maybeWhen` for `AsyncValue`.
- **Build:** Task list screen (loading/error/data states), task detail screen, project list — all driven by Riverpod.
- **Doc:** Consuming-providers patterns + rebuild-optimization with `select`.

#### Day 13 — Navigation, Forms & Feedback
- **Theory:** `go_router` (routes, guards based on auth provider, params), form widgets, snackbars/dialogs as side effects via `ref.listen`.
- **Build:** Auth-guarded routing, create/edit task forms wired to form notifier, success/error feedback, pull-to-refresh + infinite scroll UI.
- **Doc:** Routing + auth-guard pattern + form-to-state wiring.

#### Day 14 — UI Performance & Polish
- **Theory:** `const` constructors, `select` to minimize rebuilds, list virtualization, image caching, loading skeletons, theming.
- **Build:** Optimize rebuilds, add skeletons/shimmer, empty/error states, file/avatar upload UI with progress, theming.
- **Doc:** Performance checklist + rebuild-debugging notes.

---

### PHASE 5 — INTEGRATION & HARDENING (Day 15)

#### Day 15 — End-to-End, Testing & Review
- **Theory:** Test pyramid (unit/widget/integration), what to test per layer, observability/logging.
- **Build:** Full end-to-end run of every feature; add widget tests for 2 screens + 1 integration test for the auth→list flow; fix gaps; final polish.
- **Doc:** **Capstone README**, architecture overview, and a self-review: re-read every daily doc and answer your interview questions from memory.

---

## 6. Documentation System (your "very strong system")

Use your existing split:

- **`Doc_internally/day N/`** — *your own* notes, code snippets, diagrams, gotchas, interview Q&A. One filled `daily_doc_template.md` per day. This is what you'll re-read to revise.
- **`Doc_Externally/`** — *curated external* resources per topic: official docs links, the best article/video you used, package READMEs. Keep it a clean index, not a dump.

**Rule:** You only "understand" a concept when you've written it in your own words *and* can answer its 3 interview questions without notes. The template enforces this.

> Template lives at `Doc_internally/_TEMPLATES/daily_doc_template.md` — copy it into each day's folder and rename it to the day's topic.

---

## 7. Anti-Burnout & Safety Rails

- **Scope is the enemy.** If a day's build runs long, ship a smaller version and note the gap — never skip the documentation block.
- **One buffer is built in:** if you fall behind, compress Day 14 (polish) — it's the most cuttable.
- **Daily git commit** (even though this folder isn't a repo, init one for the capstone) — your commit history is proof of progress.
- **Weekly checkpoint:** End of Day 5 and Day 11, do a 30-min review of all docs so far.

---

## 8. Progress Tracker

| Day | Layer | Deliverable done | Doc done | Recall passed |
|---|---|:--:|:--:|:--:|
| 1 | Foundation | ☐ | ☐ | ☐ |
| 2 | Data | ☐ | ☐ | ☐ |
| 3 | Data | ☐ | ☐ | ☐ |
| 4 | Data | ☐ | ☐ | ☐ |
| 5 | Data | ☐ | ☐ | ☐ |
| 6 | Data | ☐ | ☐ | ☐ |
| 7 | Domain | ☐ | ☐ | ☐ |
| 8 | Riverpod | ☐ | ☐ | ☐ |
| 9 | Riverpod | ☐ | ☐ | ☐ |
| 10 | Riverpod | ☐ | ☐ | ☐ |
| 11 | Riverpod | ☐ | ☐ | ☐ |
| 12 | UI | ☐ | ☐ | ☐ |
| 13 | UI | ☐ | ☐ | ☐ |
| 14 | UI | ☐ | ☐ | ☐ |
| 15 | Integration | ☐ | ☐ | ☐ |

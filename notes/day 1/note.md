# Day 1 Notes — Clean Architecture & Project Skeleton

---

## 1. Why Architecture Matters

Without architecture, your app becomes **spaghetti code** — every change breaks something else, nothing is testable, and swapping one library means touching 40 files.

Clean Architecture solves this by drawing **hard boundaries** between parts of the app. Each part has one job and doesn't know about the others.

---

## 2. The Three Layers

```
┌─────────────────────────────────┐
│   PRESENTATION (outer)          │  Widgets, Screens, Riverpod Providers
│                                 │  → What the user sees and touches
├─────────────────────────────────┤
│   DOMAIN (center — the heart)   │  Entities, Use Cases, Repository Contracts
│                                 │  → Pure Dart. The rules of the game.
├─────────────────────────────────┤
│   DATA (outer)                  │  Repository Implementations, DTOs, Mappers, Dio
│                                 │  → How we actually get things
└─────────────────────────────────┘
```

**Key point:** Presentation and Data are both "outer" layers. Domain is the center. Both outer layers point inward — toward Domain. Domain points at nobody.

---

## 3. The Dependency Rule

> **Source-code dependencies may only point INWARD.**

This is the single most important rule in Clean Architecture.

- ✅ Presentation imports Domain → allowed
- ✅ Data imports Domain → allowed
- ❌ Domain imports Flutter → FORBIDDEN
- ❌ Domain imports Dio → FORBIDDEN
- ❌ Domain imports Data → FORBIDDEN

**Why?** Because the domain contains your business rules, and business rules should never depend on a framework (Flutter) or a library (Dio) that can change or be replaced.

**Mental model — the Onion:**
The domain is the core of an onion. You can peel off the outer layers (swap Dio for `http`, swap Flutter for a CLI) and the core is untouched.

---

## 4. The Domain Layer — "The Rules of the Game"

The domain layer contains exactly **three things**:

### 4.1 Entity
A business object. Not a JSON model. Just the shape of a thing as your business cares about it.

```dart
class Task extends Equatable {
  final String id;      // String, not int — business decision
  final String title;
  final bool isDone;    // bool, not 0/1 — business shape
  ...
}
```

**Rules for entities:**
- `final` fields only (immutable)
- No Flutter imports
- No JSON parsing
- Extend `Equatable` for value equality

### 4.2 Repository Contract (Interface)
An **abstract promise**: "someone, somewhere, will give me this data."  
It says *what* it needs, not *how* to get it.

```dart
abstract interface class TaskRepository {
  Future<Either<Failure, List<Task>>> getTasks();
}
```

**Why it lives in domain, not data:**
Because it is a *business contract*, not an implementation detail. Moving it to data would make the domain depend on the data layer — breaking the dependency rule.

### 4.3 Use Case
One class = one business action. It orchestrates the repository.

```dart
class GetTasks implements UseCase<List<Task>, GetTasksParams> {
  const GetTasks(this._repository);
  final TaskRepository _repository;

  @override
  Future<Either<Failure, List<Task>>> call(GetTasksParams params) {
    return _repository.getTasks(cursor: params.cursor);
  }
}
```

---

## 5. Dependency Inversion Principle (the "D" in SOLID)

**The puzzle:** If domain can't import data, how does the use case ever reach the real API?

**The answer:** The *contract* (interface) lives in domain. The *implementation* lives in data. At runtime, we inject the implementation.

```
Compile-time (who imports whom):
  Data → imports → Domain contract

Runtime (who calls whom):
  Domain use case → calls → Data implementation
```

The dependency arrow is *inverted* — Data depends on Domain, not the reverse. This is Dependency Inversion.

---

## 6. DTO vs Entity — The Two Shapes of Data

| | DTO | Entity |
|---|---|---|
| **Lives in** | Data layer | Domain layer |
| **Shape matches** | API JSON | Business logic |
| **Contains** | `fromJson`, `toJson` | `copyWith`, business methods |
| **Imports** | Can import anything | Pure Dart only |
| **Example field** | `task_id` (snake_case from API) | `id` (camelCase, business name) |

**Why not use DTOs everywhere?**

If the API renames `task_id` to `id` and you used `TaskDto` in 20 widgets → you edit 20 files.

If you used the mapper pattern → you edit 1 file (the mapper).

### The Mapper
A translator at the border between Data and Domain:

```
API JSON → TaskDto → [Mapper] → Task Entity → Domain/Presentation
```

The mapper is the only place that knows both shapes. Change happens in one place.

---

## 7. The Two Magic Boundaries

Every request crosses two walls on its way from the API to the UI:

1. **DTO → Entity** — The API shape never escapes the data layer
2. **Exception → Failure** — Raw exceptions never reach the UI; they become safe typed `Failure` values

```dart
// In RepositoryImpl — this is the boundary
try {
  final dtos = await _remote.getTasks();
  return Right(dtos.map((d) => d.toEntity()).toList()); // DTO → Entity
} on NetworkException {
  return const Left(NetworkFailure()); // Exception → Failure
}
```

---

## 8. REST vs GraphQL

### REST (Representational State Transfer)
- Multiple endpoints, each with a fixed URL and fixed response
- The **server decides** what data to return
- You often get more data than you need (over-fetching) or need multiple calls to get all the data (under-fetching)

```
GET /tasks          → returns all task fields (whether you need them or not)
GET /tasks/1        → returns one task
GET /tasks/1/user   → separate call to get the task's owner
```

**When to use:** Most apps. Simple, well-understood, great tooling.

### GraphQL
- **One single endpoint** (usually `/graphql`)
- The **client decides** exactly what fields it wants — you ask, you get exactly that
- No over-fetching, no under-fetching
- One call can fetch deeply nested data

```graphql
query {
  task(id: "1") {
    title        # only these fields come back
    isDone
    owner {
      name
    }
  }
}
```

**When to use:** Complex UIs that need flexible queries, apps with many different clients (mobile/web needing different data), or when bandwidth matters.

| | REST | GraphQL |
|---|---|---|
| Endpoints | Many | One |
| Who controls response shape | Server | Client |
| Over-fetching | Common | Eliminated |
| Learning curve | Low | Higher |
| Caching | Easy (HTTP cache) | Harder |
| Tooling maturity | Very mature | Mature but complex |

---

## 9. When Do You NOT Need Use Cases?

Some apps and tutorials skip the `usecases/` folder entirely. Here's when that's justified:

### Use cases are just pass-through (no real logic)
```dart
// This use case adds ZERO value — it's just wrapping the repository call
class GetTasks {
  Future<List<Task>> call() => _repo.getTasks();
}
```
When a use case does nothing except delegate to the repository with no transformation, no rules, no combining of sources — it's boilerplate without benefit.

### When you CAN skip use cases:
- Simple CRUD apps with no real business logic
- Prototypes or small personal apps
- When the ViewModel/Provider already handles the orchestration simply

### When you MUST keep use cases:
- When multiple repositories are combined in one action
- When business rules live in the use case (validation, calculations, decisions)
- When the same business action is triggered from multiple places (share the logic)
- When you need to unit test business logic independently of the UI

**The rule of thumb:**
> If your use case only calls one repository method and returns the result unchanged, question whether it's worth having. If it does anything else — keep it.

In production apps at companies like Careem or Talabat, use cases almost always exist because real business logic is complex enough to justify them.

---

## 10. Key Phrases to Remember for Interviews

- "The domain is pure Dart and depends on nothing."
- "The repository interface lives in domain because it's a business contract, not an implementation detail."
- "Dependency Inversion: Data depends on Domain, not the reverse — because Domain owns the interface."
- "DTOs are the API's shape; Entities are the business's shape. The mapper translates between them."
- "Two boundaries: DTO→Entity and Exception→Failure. Neither leaks out of the data layer."

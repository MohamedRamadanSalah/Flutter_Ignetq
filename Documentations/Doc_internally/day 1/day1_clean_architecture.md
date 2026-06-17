# Day 1 — Clean Architecture & Project Skeleton (Foundation)

**Date:** 2026-06-18  ·  **Hours spent:** ____  ·  **Capstone feature touched:** project skeleton + Tasks contracts

> This is a WORKED EXAMPLE of the daily template, filled in for Day 1.
> Use `_TEMPLATES/daily_doc_template.md` for Days 2–15.

---

## 1. What is it? (in my own words)
Clean Architecture splits an app into concentric layers — **Presentation**, **Domain**, **Data** — where the **Domain** sits in the center and knows nothing about the others. Code dependencies only ever point *inward* toward the domain. The domain defines *contracts* (interfaces); the outer layers *implement* them.

## 2. Why does it exist? (the problem it solves)
Without it, API calls, JSON, and UI logic get tangled together. Changing the API breaks the UI; you can't unit-test business rules without a real network; and the codebase becomes impossible to reason about. Clean Architecture isolates change: swap Dio for http, or REST for GraphQL, and the domain + UI don't notice.

## 3. How it works / how I implemented it
- Created **feature-first** folders: `features/<feature>/{data,domain,presentation}` + a shared `core/`.
- Domain defines `Task` entity + `TaskRepository` (abstract) + `Failure` types.
- Data implements `TaskRepositoryImpl` against the contract, mapping `DTO → Entity` and `Exception → Failure`.
- Presentation wires everything with Riverpod providers and reads through a use case.
- `main.dart` wraps the app in `ProviderScope`.

```dart
// The dependency-inversion seam — domain owns the abstraction:
abstract interface class TaskRepository {
  Future<Either<Failure, List<Task>>> getTasks({String? cursor});
}
// data depends on domain (implements it); domain depends on no one.
class TaskRepositoryImpl implements TaskRepository { /* ... */ }
```

## 4. Key concepts learned today
- The **Dependency Rule**: source-code dependencies point inward only.
- **Dependency Inversion**: high-level (domain) and low-level (data) both depend on an abstraction, not each other.
- **DTO ≠ Entity**: API shape must not leak into business code.
- **Either<Failure, T>**: errors are values, not thrown surprises, once they cross into the domain.

## 5. Gotchas / mistakes I hit
- The domain layer must have **zero** imports of `dio`, `flutter`, or JSON — if it does, the layering is broken.
- Repository *contract* lives in `domain/`, the *implementation* in `data/`. Mixing them up is the #1 beginner error.

## 6. Diagram
```
presentation ──► domain ◄── data
   (Riverpod)   (entities,   (dio, dtos,
                 use cases,   repo impl,
                 contracts)   mappers)
        arrows = compile-time dependencies, all point to domain
```

## 7. Interview questions I can now answer
1. **Q:** What is the Dependency Rule and why does it matter?
   **A:** Source dependencies point only inward toward the domain, so business logic never depends on frameworks/UI — making it testable and change-resilient.
2. **Q:** Where does the repository interface live vs its implementation, and why?
   **A:** Interface in `domain` (it's a business contract), implementation in `data`. This inverts the dependency so data depends on domain, not the reverse.
3. **Q:** Why map DTOs to entities instead of using DTOs everywhere?
   **A:** To stop API/JSON details (field names, formats, nullability) from leaking into business logic and UI, so API changes are absorbed in one mapper.

## 8. External resources used
- Flutter official: app architecture guide → (add link in Doc_Externally)
- Riverpod docs: Getting started → (add link in Doc_Externally)

## 9. Recall test — did I explain it from memory without notes?  ☐ Yes  ☐ Not yet

## 10. Open questions / to revisit
- When should a feature get its OWN `core`-like shared code vs putting it in global `core/`?
- fpdart `Either` vs dartz `Either` — which to standardize on?

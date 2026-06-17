# Day 7 — Tasks · Entities, Use Cases & Business Rules

**Layer:** Domain · **Goal:** A complete, pure domain layer driving everything.

## 🧠 Theory (60–90 min)
- [ ] Why domain is pure Dart (no Flutter/Dio/JSON imports).
- [ ] Use case (interactor) pattern: one action per use case.
- [ ] Where business rules belong (validation, defaults, derived values).

## 🛠️ Build (3–3.5 hr) — `features/*/domain/usecases/`
- [ ] Finalize entities (`Task`, `Project`, `User`) with any invariants.
- [ ] Implement use cases: `CreateTask`, `ToggleTaskDone`, `DeleteTask`, `SearchTasks`, `GetProjects`.
- [ ] Add a real business rule (e.g. a task title must be 1–120 chars → `ValidationFailure`).
- [ ] Confirm each use case returns `Either<Failure, T>` and calls only the repository.
- [ ] Verify: domain folder has ZERO `dio`/`flutter`/`hive` imports.

## 📝 Document — copy template → `day 7/`
- [ ] Use case pattern + "what belongs in Domain vs Data" table.
- [ ] Proof of the dependency direction (list domain imports).

## ✅ Definition of Done
- [ ] All use cases compile & are pure. [ ] One validation rule enforced. [ ] Doc done.

## 🔁 Recall test
- [ ] Explain why business logic lives in use cases, not in providers or repositories.

# Day 3 — Tasks · DTOs, Serialization & Mapping

**Layer:** Data · **Goal:** Type-safe models with codegen + a clean DTO↔Entity seam.

## 🧠 Theory (60–90 min)
- [ ] DTO vs Entity (recap) + why models must not leak into domain.
- [ ] `freezed` + `json_serializable`: what they generate and why.
- [ ] Handling nested objects, nullable fields, and API field renames.

## 🛠️ Build (3–3.5 hr)
- [ ] Add `freezed`/`json_serializable` setup (already in `pubspec.yaml`).
- [ ] Convert `task_dto.dart` to a **freezed** model with `fromJson`/`toJson`.
- [ ] Run: `dart run build_runner build --delete-conflicting-outputs`.
- [ ] Add a `ProjectDto` (freezed) too.
- [ ] Verify `task_mapper.dart` still maps DTO → `Task` entity correctly.
- [ ] Handle a nullable/renamed field (e.g. `due_date` → `dueDate`) cleanly.

## 📝 Document — copy template → `day 3/`
- [ ] DTO vs Entity comparison table.
- [ ] The build_runner workflow (build / watch / delete-conflicting).

## ✅ Definition of Done
- [ ] Codegen runs clean. [ ] DTOs are freezed. [ ] Mapping verified.

## 🔁 Recall test
- [ ] Explain what `freezed` generates for you and why it reduces bugs.

# Day 11 — Tasks · Testing Riverpod & Form State ⭐

**Layer:** State Management · **Goal:** Tested providers + a validated form notifier.

## 🧠 Theory (60–90 min)
- [ ] `ProviderContainer` + overriding providers in tests.
- [ ] Testing a Notifier/AsyncNotifier with mocked dependencies (mocktail).
- [ ] Form state in Riverpod: fields, validation, submit status.

## 🛠️ Build (3–3.5 hr) — `test/`
- [ ] Write a fake/mock `TaskRepository` with mocktail.
- [ ] Test `TaskListNotifier`: loads data, surfaces error, create updates state.
- [ ] Test the debounced search + filtered provider.
- [ ] Build a `CreateTaskFormNotifier` holding fields + validation + `AsyncValue` submit state.
- [ ] Test validation (empty title → `ValidationFailure`).

## 📝 Document — copy template → `day 11/`
- [ ] Provider testing template (container + overrides).
- [ ] Form-state pattern.

## ✅ Definition of Done
- [ ] 3+ provider tests pass. [ ] Form validates + submits. [ ] Doc done.

## 🔁 Recall test
- [ ] Explain how `ProviderContainer` + overrides isolate a provider under test.
- [ ] **Checkpoint:** review all Day 1–11 docs (30 min).

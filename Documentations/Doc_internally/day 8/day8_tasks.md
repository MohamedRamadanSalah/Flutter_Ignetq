# Day 8 — Tasks · Riverpod Foundations ⭐

**Layer:** State Management · **Goal:** Understand providers deeply + migrate wiring to code-gen.

## 🧠 Theory (60–90 min)
- [ ] Why Riverpod (vs Provider/Bloc): compile-safe, testable, no BuildContext.
- [ ] `ProviderScope`, `ref.watch` vs `ref.read` vs `ref.listen`.
- [ ] Provider types: `Provider`, `FutureProvider`, `StreamProvider`, `NotifierProvider`.
- [ ] `autoDispose` and `family` — what problems they solve.
- [ ] Code-gen `@riverpod` annotation.

## 🛠️ Build (3–3.5 hr) — `presentation/providers/`
- [ ] Migrate `dio/datasource/repository/usecase` providers to `@riverpod` functions.
- [ ] Run `build_runner` and confirm generated `.g.dart` files.
- [ ] Convert `tasksProvider` to a code-gen `FutureProvider`.
- [ ] Add a `family` provider: `taskById(id)`.
- [ ] Add an `autoDispose` provider and observe it dispose in logs.

## 📝 Document — copy template → `day 8/`
- [ ] Provider-type cheat sheet.
- [ ] watch vs read vs listen + when family/autoDispose.

## ✅ Definition of Done
- [ ] All providers code-gen. [ ] family + autoDispose used. [ ] App still runs.

## 🔁 Recall test
- [ ] Explain the difference between `ref.watch` and `ref.read` and when each is wrong.

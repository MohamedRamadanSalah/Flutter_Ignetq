# Day 9 — Tasks · Async State with AsyncNotifier ⭐

**Layer:** State Management · **Goal:** Robust async state + mutations + optimistic updates.

## 🧠 Theory (60–90 min)
- [ ] `AsyncValue`: data / loading / error and pattern matching with `when`.
- [ ] `AsyncNotifier` / `Notifier` lifecycle and `build()`.
- [ ] Mutations + `ref.invalidateSelf()` / `ref.invalidate()`.
- [ ] `StreamProvider` for live data.

## 🛠️ Build (3–3.5 hr)
- [ ] Replace `tasksProvider` with a `TaskListNotifier extends AsyncNotifier<List<Task>>`.
- [ ] Implement `build()` to load tasks via `GetTasks`.
- [ ] Add `createTask()` with an **optimistic update** (add to state, rollback on failure).
- [ ] Add `toggleDone()` and `delete()` mutations.
- [ ] Add a `StreamProvider` for live task-status updates (mock stream is fine).

## 📝 Document — copy template → `day 9/`
- [ ] AsyncValue handling patterns.
- [ ] Optimistic update + rollback recipe.

## ✅ Definition of Done
- [ ] Notifier loads/refreshes. [ ] Create is optimistic w/ rollback. [ ] Stream updates UI.

## 🔁 Recall test
- [ ] Explain optimistic updates and how you roll back on error.

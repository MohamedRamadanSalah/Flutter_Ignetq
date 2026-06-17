# Day 12 — Tasks · Widgets, Screens & Consuming Providers

**Layer:** UI · **Goal:** Reactive screens driven entirely by Riverpod.

## 🧠 Theory (60–90 min)
- [ ] `ConsumerWidget` vs `ConsumerStatefulWidget` vs `Consumer`.
- [ ] `ref.watch` in build + `select` to scope rebuilds.
- [ ] Rendering `AsyncValue` with `when` / `maybeWhen`.

## 🛠️ Build (3–3.5 hr) — `presentation/screens/` + `widgets/`
- [ ] Build `TaskListScreen` with loading / error / data states via `when`.
- [ ] Extract a `TaskTile` widget (uses `select` to watch only what it needs).
- [ ] Build `TaskDetailScreen` reading `taskById(id)` family provider.
- [ ] Build `ProjectListScreen`.
- [ ] Add empty-state UI when the list is empty.

## 📝 Document — copy template → `day 12/`
- [ ] Consuming-providers patterns.
- [ ] Rebuild optimization with `select`.

## ✅ Definition of Done
- [ ] 3 screens render real data. [ ] States handled. [ ] `select` used to limit rebuilds.

## 🔁 Recall test
- [ ] Explain how `select` reduces rebuilds and when it matters.

# Day 10 — Tasks · Composition & Advanced Patterns ⭐

**Layer:** State Management · **Goal:** Derived state, debounced search, paginated notifier.

## 🧠 Theory (60–90 min)
- [ ] Combining/derived providers (one provider watching another).
- [ ] `keepAlive` + caching results across navigation.
- [ ] Debounce vs throttle for search.
- [ ] `ref.listen` for side effects (navigation, snackbars).
- [ ] Scoping + provider overrides.

## 🛠️ Build (3–3.5 hr)
- [ ] Add a `searchQueryProvider` (`StateProvider`/`Notifier`) + a **debounced** search.
- [ ] Add a **derived** `filteredTasksProvider` that watches tasks + query.
- [ ] Build a `PaginatedTasksNotifier` (loads next page, tracks `isLoadingMore` + `hasMore`).
- [ ] Use `keepAlive` so the list survives navigating away and back.
- [ ] Use `ref.listen` to show a snackbar when a create fails.

## 📝 Document — copy template → `day 10/`
- [ ] Derived-provider pattern.
- [ ] Debounce recipe + keepAlive notes.

## ✅ Definition of Done
- [ ] Debounced search filters live. [ ] Pagination appends. [ ] keepAlive verified.

## 🔁 Recall test
- [ ] Explain how a derived provider recomputes and why it's better than manual sync.

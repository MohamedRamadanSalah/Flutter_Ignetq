# Day 5 — Tasks · Caching, Offline-First & Pagination

**Layer:** Data · **Goal:** Smart caching, offline behavior, and cursor pagination.

## 🧠 Theory (60–90 min)
- [ ] Cache strategies: cache-first, network-first, stale-while-revalidate.
- [ ] Cache invalidation + expiry (TTL).
- [ ] Offline-first principles + sync queue idea.
- [ ] Pagination types: offset vs page vs **cursor**.

## 🛠️ Build (3–3.5 hr)
- [ ] Add a `CacheManager` with TTL (e.g. tasks expire after 5 min).
- [ ] Implement **stale-while-revalidate**: return cache instantly, refresh in bg.
- [ ] Add a **sync queue** stub: store pending writes when offline.
- [ ] Implement **cursor-based** `getTasks(cursor)` and append results.
- [ ] Add connectivity check (online/offline) to drive the cache decision.

## 📝 Document — copy template → `day 5/`
- [ ] Cache-strategy decision tree.
- [ ] Cursor pagination explained with a diagram.

## ✅ Definition of Done
- [ ] Cache has TTL. [ ] Offline returns cache + queues writes. [ ] Pagination loads page 2.

## 🔁 Recall test
- [ ] Explain stale-while-revalidate and when to prefer it over network-first.
- [ ] **Checkpoint:** review all Day 1–5 docs (30 min).

# Day 4 — Tasks · Repository + Remote/Local Data Sources

**Layer:** Data · **Goal:** A repository that coordinates remote + local as one source of truth.

## 🧠 Theory (60–90 min)
- [ ] Repository = single source of truth; what belongs in it vs the data source.
- [ ] Remote vs Local data source responsibilities.
- [ ] Read-through vs write-through coordination.

## 🛠️ Build (3–3.5 hr)
- [ ] Create `TaskLocalDataSource` using **Hive** (init Hive in `main.dart`).
- [ ] Define a Hive model/adapter (or store raw JSON for now).
- [ ] Implement `getTasks`: fetch remote → cache to local → return.
- [ ] Implement the unfinished `toggleDone` and `deleteTask` in `TaskRepositoryImpl`.
- [ ] On remote failure, fall back to local cache (return cached tasks).

## 📝 Document — copy template → `day 4/`
- [ ] Repository ↔ data source responsibilities split.
- [ ] Read-through cache flow diagram.

## ✅ Definition of Done
- [ ] Tasks cache locally. [ ] Offline read returns cache. [ ] toggle/delete work.

## 🔁 Recall test
- [ ] Explain "single source of truth" with the TaskFlow example.

# Day 1 — Tasks · Clean Architecture & Project Skeleton

**Layer:** Foundation · **Goal:** A runnable skeleton + the dependency rule in your bones.

## 🧠 Theory (60–90 min)
- [✅] Read the Flutter "app architecture" guide + Clean Architecture layers.
- [✅] Write in your own words: the Dependency Rule + Dependency Inversion.
- [✅] Understand DTO vs Entity and why domain stays pure.

## 🛠️ Build (3–3.5 hr) — in `Work and challenges/taskflow`
- [✅] `flutter pub get` and confirm the skeleton compiles.
- [✅] Re-read every file in `lib/` and explain each out loud (don't just skim).
- [✅] Add one more domain entity yourself: `Project` (`id`, `name`, `taskCount`).
- [✅] Add its contract `ProjectRepository` (just `getProjects()` for now).
- [✅] Run the app; confirm `ProviderScope` + `TasksScreen` render (API failure is OK).

## 📝 Document (45–60 min)
- [✅] Read the worked example `day1_clean_architecture.md`.
- [✅] (Already done for you — verify you agree with every line.)
- [✅] Add your architecture diagram drawn by hand / ascii.

## ✅ Definition of Done
- [✅] App compiles & runs. [✅] You added `Project` entity + contract. [✅] Doc verified.

## 🔁 Recall test
- [✅] Close notes. Explain: "Why does the repository interface live in domain, not data?"

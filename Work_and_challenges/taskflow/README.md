# TaskFlow — 15-Day Mastery Capstone

A team task manager built **one layer at a time** to master Flutter Clean Architecture + Riverpod.
See the full plan in `Documentations/Doc_internally/15_DAY_MASTER_PLAN.md`.

## Getting started
```bash
flutter pub get
dart run build_runner build --delete-conflicting-outputs   # from Day 3 onward
flutter run
```

## Layer structure (the dependency rule: arrows point INWARD)

```
presentation (Riverpod + widgets)  ─┐
                                     ├──►  domain (entities, use cases, repo CONTRACTS)
data (dio, dtos, repo IMPLEMENTATIONS) ─┘        ▲ pure Dart, depends on nothing
```

```
lib/
├── core/                 # shared: error, network, storage, usecase base
└── features/
    ├── tasks/
    │   ├── data/          # dtos · mappers · datasources · repository impl
    │   ├── domain/        # entities · repository contract · use cases
    │   └── presentation/  # providers (Riverpod) · screens · widgets
    └── auth/              # same structure
```

## Flow of one request (getTasks)
```
UI (ConsumerWidget)
  → watches tasksProvider (FutureProvider → AsyncNotifier on Day 9)
    → GetTasks use case
      → TaskRepository (contract)  [domain]
        → TaskRepositoryImpl       [data]  — maps Exception → Failure
          → TaskRemoteDataSource → Dio → API
        ← TaskDto → (mapper) → Task entity
      ← Either<Failure, List<Task>>
```

## Build order (which file each day touches)
- **Day 1:** folders, `core/error/*`, `core/usecase`, domain contracts, `task_providers`, `main.dart` ✅ (skeleton here)
- **Day 2:** `core/network/dio_client` — interceptors, auth, retry
- **Day 3:** convert `task_dto` to freezed; finalize mappers
- **Day 4:** local datasource + repository coordination
- **Day 5:** cache + offline + pagination
- **Day 6:** full Failure system + auth feature
- **Day 7:** all use cases
- **Days 8–11:** migrate providers to `@riverpod`, AsyncNotifier, testing
- **Days 12–14:** screens, routing, forms, polish
- **Day 15:** tests + integration + README finalization
```

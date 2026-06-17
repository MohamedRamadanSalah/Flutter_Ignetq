# 📖 Day 1 — Clean Architecture & the Project Skeleton
### *The chapter where you learn to build a house that never collapses*

---

## 1. The Story 🏛️

Imagine two developers, **Sara** and **Omar**, both asked to build the same app: a task manager.

**Omar** opens `main.dart` and just starts typing. He puts the API call inside the button's `onPressed`. He parses JSON right inside the widget. He stores the token in a global variable. In two days he has a working screen. Everyone claps. 👏

Then the client says: *"Change the backend from REST to GraphQL, and make it work offline."*

Omar's app **explodes**. The API code is glued to 40 different widgets. He can't test anything without a real server. Changing one thing breaks five others. He spends two weeks untangling spaghetti. 🍝

**Sara** spent her first day differently. She drew **boundaries** before writing features. She decided: *"The UI will never know what an API is. The business rules will never know what JSON is. Each part will have one job."*

When the same change request came, Sara swapped **one folder** — the data layer — and everything else kept working. She was done in an afternoon.

> **The moral:** The difference between Omar and Sara is not talent. It's that Sara built **architecture** before she built **features**. Today, you become Sara.

---

## 2. The Big Picture 🗺️

Clean Architecture organizes your app into **three concentric layers**. The most important rule in the entire chapter is about the *direction* the arrows point.

```mermaid
flowchart TD
    subgraph PRES["🎨 PRESENTATION (outer)"]
        UI["Widgets / Screens"]
        RP["Riverpod Providers"]
    end
    subgraph DOM["🧠 DOMAIN (center — the heart)"]
        E["Entities"]
        UC["Use Cases"]
        RC["Repository CONTRACTS<br/>(abstract interfaces)"]
    end
    subgraph DATA["🔌 DATA (outer)"]
        RI["Repository IMPLEMENTATIONS"]
        DS["Data Sources (Dio, Hive)"]
        DTO["DTOs + Mappers"]
    end

    UI --> RP --> UC
    UC --> RC
    UC --> E
    RI -. "implements" .-> RC
    RI --> DS --> DTO

    style DOM fill:#fff3cd,stroke:#d39e00,stroke-width:3px
    style PRES fill:#d1ecf1,stroke:#0c5460
    style DATA fill:#d4edda,stroke:#155724
```

Read it like this: **Presentation and Data are both on the outside. Domain is in the middle. Everyone points *inward* toward the Domain. The Domain points at nobody.**

---

## 3. The Critical Idea: The Dependency Rule 🎯

This is the single most important sentence in Clean Architecture:

> **Source-code dependencies may only point INWARD.**

An *inner* layer (Domain) must **never** import anything from an *outer* layer (Data or Presentation).

Why does this one rule create such powerful software? Because of what it *forbids*:

```mermaid
flowchart LR
    A["Domain imports Dio?"] -->|"❌ FORBIDDEN"| B["Business logic now<br/>depends on a network library"]
    C["Domain imports Flutter?"] -->|"❌ FORBIDDEN"| D["Business logic now<br/>depends on the UI framework"]
    E["Domain imports nothing<br/>but pure Dart"] -->|"✅ ALLOWED"| F["Business logic is<br/>testable, portable, eternal"]

    style B fill:#f8d7da
    style D fill:#f8d7da
    style F fill:#d4edda
```

**Mental model — the Onion 🧅:** The domain is the core of an onion. You can peel off the outer layers (swap Dio for `http`, swap Flutter for a CLI) and the core is untouched. But you can never have the core depend on a peel — peels come and go, the core is forever.

---

## 4. The Three Layers, One by One

### 4.1 🧠 Domain — *"The rules of the game"*

The Domain layer knows **what your app does**, not *how*. It is **pure Dart** — zero Flutter, zero Dio, zero JSON.

It contains three things:

```mermaid
classDiagram
    class Task {
        +String id
        +String title
        +bool isDone
        +copyWith()
    }
    class TaskRepository {
        <<interface>>
        +getTasks() Either~Failure, List~Task~~
        +createTask(Task) Either~Failure, Task~
    }
    class GetTasks {
        -TaskRepository repo
        +call() Either~Failure, List~Task~~
    }
    GetTasks --> TaskRepository : uses
    GetTasks --> Task : returns
    TaskRepository --> Task : works with
```

- **Entity** (`Task`) — a business object. Not a JSON model. Just the *shape* of a task as your business cares about it.
- **Repository Contract** (`TaskRepository`) — an **abstract interface**. It's a *promise*: "someone, somewhere, will give me tasks." It does **not** say how (no Dio, no Hive mentioned).
- **Use Case** (`GetTasks`) — one single business action. It orchestrates the repository.

### 4.2 🔌 Data — *"How we actually get things"*

The Data layer is the **how**. It *implements* the promises the Domain made.

```mermaid
flowchart LR
    API["🌐 REST API"] --> DTO["TaskDto<br/>(matches JSON)"]
    DTO --> MAP["🔄 Mapper"]
    MAP --> ENT["Task Entity<br/>(business shape)"]
    ENT --> REPO["RepositoryImpl<br/>returns Either"]

    style DTO fill:#d4edda
    style ENT fill:#fff3cd
```

The key character here is the **Mapper** — a translator standing at the border between the API world and the business world. JSON comes in as a `TaskDto`; a clean `Task` entity comes out. The API can rename a field tomorrow and you fix it in **one** place: the mapper.

### 4.3 🎨 Presentation — *"What the user sees and touches"*

This is widgets + Riverpod. It calls **use cases** (never repositories or APIs directly) and turns the result into pixels.

---

## 5. The Full Journey of One Request 🚀

Here is what happens, end to end, when the user opens the task list. Trace it slowly — this single diagram *is* Clean Architecture in motion.

```mermaid
sequenceDiagram
    participant U as 🎨 Widget
    participant P as Riverpod Provider
    participant UC as 🧠 GetTasks (UseCase)
    participant R as TaskRepository (contract)
    participant RI as 🔌 RepositoryImpl
    participant DS as RemoteDataSource
    participant API as 🌐 API

    U->>P: ref.watch(tasksProvider)
    P->>UC: call(NoParams)
    UC->>R: getTasks()
    Note over R,RI: contract → implementation
    R->>RI: (resolved at runtime)
    RI->>DS: getTasks()
    DS->>API: GET /tasks
    API-->>DS: JSON
    DS-->>RI: List<TaskDto>
    RI->>RI: map DTO → Entity<br/>catch Exception → Failure
    RI-->>UC: Either<Failure, List<Task>>
    UC-->>P: Either<Failure, List<Task>>
    P-->>U: AsyncValue (loading→data/error)
```

Notice the **two magic boundaries**:
1. **DTO → Entity** (the API shape never escapes the data layer).
2. **Exception → Failure** (raw errors never escape into the UI; they become safe, typed values).

---

## 6. Critical Idea: Dependency Inversion 🔄

"But wait," you ask, "if Domain can't depend on Data, how does the use case ever reach the real API?"

This is the clever trick. The **contract lives in Domain**, the **implementation lives in Data**. At runtime, we *inject* the implementation. So the arrow of *dependency* (compile-time) points the opposite way to the arrow of *control* (runtime).

```mermaid
flowchart TD
    subgraph compile["Compile-time dependency (who imports whom)"]
        direction TB
        DataC["Data layer"] -->|imports| DomainC["Domain contract"]
    end
    subgraph runtime["Runtime control (who calls whom)"]
        direction TB
        DomainR["Domain use case"] -->|calls| DataR["Data implementation"]
    end

    style DomainC fill:#fff3cd
    style DomainR fill:#fff3cd
```

> **The aha 💡:** We *inverted* the dependency. Data depends on Domain (not the reverse) because Domain owns the interface. This is the "D" in SOLID — the Dependency Inversion Principle.

---

## 7. How This Maps to TaskFlow 🧩

Your capstone folder structure *is* the architecture made physical:

```mermaid
flowchart TD
    root["features/tasks/"]
    root --> dom["domain/"]
    root --> dat["data/"]
    root --> pres["presentation/"]

    dom --> e["entities/task.dart"]
    dom --> rc["repositories/task_repository.dart  ⟵ contract"]
    dom --> u["usecases/get_tasks.dart"]

    dat --> dto["dtos/task_dto.dart"]
    dat --> m["mappers/task_mapper.dart"]
    dat --> ds["datasources/task_remote_datasource.dart"]
    dat --> ri["repositories/task_repository_impl.dart  ⟵ implements contract"]

    pres --> pr["providers/task_providers.dart"]
    pres --> sc["screens/ + widgets/"]

    style dom fill:#fff3cd
    style dat fill:#d4edda
    style pres fill:#d1ecf1
```

Open each file in `Work and challenges/taskflow/lib/features/tasks/` and find it on this map. **You should be able to point to any file and say which layer it's in and why.**

---

## 8. Common Traps ⚠️

```mermaid
mindmap
  root((Day 1 Traps))
    Putting the repository INTERFACE in data/
      Wrong: it's a business contract → belongs in domain
    Importing Flutter/Dio in domain
      Breaks the dependency rule silently
    Using DTOs in the UI
      JSON shape leaks everywhere → fragile
    One giant lib/ with no features
      Organize by FEATURE, then by layer
    Throwing exceptions to the UI
      Convert to Failure at the repo boundary
```

---

## 9. What You Must Be Able To Do By Tonight ✅

- [ ] Draw the three-layer diagram from memory and explain the arrow direction.
- [ ] Explain *why* the repository interface lives in `domain/`.
- [ ] Point at every file in `taskflow/lib/` and name its layer.
- [ ] Explain the two boundaries: DTO→Entity and Exception→Failure.
- [ ] Add the `Project` entity + `ProjectRepository` contract yourself.
- [ ] Answer interview Q1–Q5 (below) out loud without notes.

---

## 10. 🏢 Interview Vault — Questions From Top Middle East Companies
> *Real-style questions asked at Careem, Talabat, Noon, Tabby, Tamara, Instabug, Vezeeta, Foodics, Halan, etc. Architecture is the #1 senior-screening topic in the region.*

```mermaid
mindmap
  root((What they probe<br/>on Day 1 topics))
    Do you UNDERSTAND boundaries
      or just memorize folder names
    Can you JUSTIFY decisions
      "why not put the API call in the widget?"
    Trade-offs awareness
      "isn't this over-engineering for a small app?"
    SOLID in practice
      Dependency Inversion specifically
```

**Q1. Walk me through Clean Architecture and the dependency rule.** *(asked everywhere)*
> **A:** Three layers — Presentation, Domain, Data. Domain is the center and pure Dart; it holds entities, use cases, and repository *contracts*. Source-code dependencies point only inward, so business logic never depends on Flutter, Dio, or JSON. This makes the domain testable and lets us swap frameworks without touching business rules.
> *🎯 Really testing:* whether you can explain the **arrow direction** and *why* it matters, not just list layers.

**Q2. Why does the repository interface live in the domain layer and the implementation in data?**
> **A:** Because the repository is a *business contract* ("give me tasks"), not a networking detail. Putting the interface in domain inverts the dependency: data depends on domain instead of the reverse (Dependency Inversion Principle). The domain stays ignorant of *how* data is fetched.
> *🎯 Really testing:* genuine grasp of Dependency Inversion vs cargo-culting folder structure.

**Q3. What is a DTO and why not use it throughout the app?**
> **A:** A DTO mirrors the API JSON shape and lives only in the data layer. If DTOs leak into UI/domain, an API field rename ripples through the whole app. The mapper isolates that change to one place, and the domain keeps a stable, business-shaped `Entity`.
> *🎯 Really testing:* do you understand *coupling* and *single point of change*.

**Q4. Isn't Clean Architecture over-engineering for a small app?** *(trap question)*
> **A:** For a throwaway prototype, yes — boilerplate has a cost. But for any app expected to grow, be tested, or be maintained by a team, the boundaries pay for themselves the first time requirements change. The honest senior answer is "it depends on the app's lifespan and team size" — show you weigh trade-offs, don't dogmatically defend it.
> *🎯 Really testing:* engineering maturity — can you criticize your own approach.

**Q5. How would you make the domain layer independently testable?**
> **A:** Keep it pure Dart (no Flutter/Dio imports), depend only on abstractions, and inject fakes/mocks of the repository contract in tests. Then a use case can be unit-tested with zero network or widgets.
> *🎯 Really testing:* connecting architecture to testability.

---

## 11. The One Sentence To Remember 🧠

> **"Dependencies point inward; the domain is pure and depends on nothing — so the business survives any change to the framework, the network, or the UI."**

➡️ **Next chapter (Day 2):** we step into the Data layer and build the bridge to the outside world — the Dio API client.

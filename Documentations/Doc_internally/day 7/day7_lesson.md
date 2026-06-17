# 📖 Day 7 — The Domain Layer: Entities, Use Cases & Business Rules
### *The chapter where you find the soul of the app*

---

## 1. The Story 🧠

Strip away the buttons, the API, the database. What is TaskFlow, really? It's a set of *truths*: "a task has a title and can be done or not", "you can't create a task with an empty title", "completing a task toggles its status." These truths don't care if the UI is Flutter or a website, or if the data comes from REST or GraphQL. **They are the soul of the app.**

**Mariam** scattered these truths everywhere — title validation in the widget, the "toggle" logic in the repository, the "what counts as overdue" rule in three different screens. When the business changed the rule ("titles max 120 chars"), she found four copies, fixed three, missed one. The app became inconsistent.

The **Domain layer** is the single home for these truths. Pure Dart, no dependencies, the part of your app that would survive even if Flutter disappeared tomorrow. Today you complete it.

---

## 2. The Big Picture 🗺️

The domain has exactly three citizens — and today you've already met them, but now you make them complete:

```mermaid
flowchart TD
    subgraph DOMAIN["🧠 Domain Layer (pure Dart)"]
        E["Entities<br/>(the nouns: Task, User, Project)"]
        UC["Use Cases<br/>(the verbs: CreateTask, Login)"]
        RC["Repository Contracts<br/>(the promises)"]
        F["Failures<br/>(the typed errors)"]
    end
    UC --> E
    UC --> RC
    UC --> F

    style DOMAIN fill:#fff3cd,stroke:#d39e00,stroke-width:3px
```

> **Mental model 📜:** Think of the domain as the **rulebook of a board game**. Entities are the pieces, use cases are the legal moves, contracts are "someone will provide the dice and board." The rulebook never mentions whether you play on wood or an app — that's the implementation's problem.

---

## 3. The Critical Idea: Purity 🎯

The domain's superpower is that it imports **nothing** from the outside world.

```mermaid
flowchart LR
    D["Domain file"] --> Check{imports?}
    Check -->|"import 'dart:core'"| OK["✅ pure Dart — fine"]
    Check -->|"import fpdart (Either)"| OK2["✅ allowed (pure utility)"]
    Check -->|"import 'package:flutter/...'"| BAD["❌ BROKEN — UI leaked in"]
    Check -->|"import 'package:dio/...'"| BAD2["❌ BROKEN — network leaked in"]
    Check -->|"import a DTO"| BAD3["❌ BROKEN — data leaked in"]

    style OK fill:#d4edda
    style OK2 fill:#d4edda
    style BAD fill:#f8d7da
    style BAD2 fill:#f8d7da
    style BAD3 fill:#f8d7da
```

**The litmus test:** open any file in `domain/`. If you see `import 'package:flutter'` or `dio` or a `Dto`, the layering is broken. A pure domain can be unit-tested in milliseconds with zero mocks of frameworks.

---

## 4. The Use Case Pattern 🎬

A **use case** (a.k.a. interactor) represents **one single business action**. One class, one job, one `call()` method.

```mermaid
classDiagram
    class UseCase~Type, Params~ {
        <<interface>>
        +call(Params) Either~Failure, Type~
    }
    class CreateTask {
        -TaskRepository repo
        +call(CreateTaskParams) Either~Failure, Task~
    }
    class Login {
        -AuthRepository repo
        +call(LoginParams) Either~Failure, User~
    }
    class ToggleTaskDone {
        -TaskRepository repo
        +call(String id) Either~Failure, Task~
    }
    CreateTask ..|> UseCase
    Login ..|> UseCase
    ToggleTaskDone ..|> UseCase
```

Why one class per action instead of fat methods on a service?

```mermaid
mindmap
  root((Why one use case<br/>per action))
    Single Responsibility
      each class does exactly one thing
    Readable intent
      CreateTask() screams what it does
    Easy to test
      tiny, focused unit tests
    Composable
      a use case can call other use cases
    Clear dependency
      depends only on the repo it needs
```

> **Critical idea 💡:** Use cases are the **only doorway** the presentation layer uses to enter the domain. The UI never touches a repository directly — it always goes through a use case. This keeps business logic out of the UI.

---

## 5. Where Do Business Rules Live? 🧩

This is the question that confuses everyone. The answer:

```mermaid
flowchart TD
    Q["A business rule.<br/>Where does it go?"] --> A{What kind?}
    A -->|"Invariant of one entity<br/>(title 1-120 chars)"| E["In the Entity<br/>(or its factory/validator)"]
    A -->|"A business action/workflow<br/>(create, toggle, search)"| U["In a Use Case"]
    A -->|"How to fetch/store data"| R["In the Repository (data)"]
    A -->|"How it looks on screen"| P["In Presentation"]

    style E fill:#fff3cd
    style U fill:#fff3cd
    style R fill:#d4edda
    style P fill:#d1ecf1
```

Example with TaskFlow:
- *"A task title must be 1–120 chars"* → entity invariant / validated in `CreateTask` use case → returns `ValidationFailure`.
- *"Toggling done flips the boolean and persists"* → `ToggleTaskDone` use case.
- *"Fetch from network, fall back to cache"* → repository (data). **Not** a business rule — it's a data policy.

---

## 6. The Full Domain in Motion 🚀

```mermaid
sequenceDiagram
    participant UI
    participant UC as CreateTask (UseCase)
    participant V as Validation (business rule)
    participant R as TaskRepository (contract)
    UI->>UC: call(CreateTaskParams(title))
    UC->>V: title valid? (1-120 chars)
    alt invalid
        V-->>UC: no
        UC-->>UI: Left(ValidationFailure)
    else valid
        V-->>UC: yes
        UC->>R: createTask(task)
        R-->>UC: Either<Failure, Task>
        UC-->>UI: result
    end
```

---

## 7. How This Maps to TaskFlow 🧩

```mermaid
flowchart TD
    subgraph domain["features/*/domain/"]
        ent["entities/ (Task, Project, User)"]
        rc["repositories/ (contracts)"]
        uc["usecases/ (GetTasks, CreateTask, ToggleTaskDone, DeleteTask, SearchTasks, Login, Logout)"]
    end
    note["✅ ZERO imports of flutter/dio/hive/dtos"]
    domain --- note

    style domain fill:#fff3cd
```

Today: finalize all entities with invariants, implement the remaining use cases, enforce at least one real validation rule (title length → `ValidationFailure`), and **prove purity** by listing the imports in your domain folder.

---

## 8. Common Traps ⚠️

```mermaid
mindmap
  root((Day 7 Traps))
    Business logic in widgets/providers
      Belongs in use cases
    Domain importing data/flutter
      Breaks purity — the cardinal sin
    Anemic use cases that just forward
      Some forwarding is fine, but rules go here
    Validation only in the UI
      Bypassed easily — enforce in domain too
    One giant 'TaskService' with 20 methods
      Split into focused use cases
```

---

## 9. 🏢 Interview Vault — Questions From Top Middle East Companies
> *Senior screens at Noon, Careem, Foodics dig hard here — it reveals whether you truly understand layering or just copy templates.*

**Q1. What is a use case and why one class per action?**
> **A:** A use case encapsulates a single business action with one `call()` method. One-per-action enforces the Single Responsibility Principle, makes intent explicit, keeps tests tiny, and lets use cases compose. It's the single entry point from presentation into the domain.
> *🎯 Really testing:* SRP applied + understanding the domain entry point.

**Q2. Where do business rules belong — and give an example of getting it wrong.**
> **A:** Entity invariants live on the entity; business actions/validation live in use cases; data policies (caching) live in the repository. Getting it wrong: putting title validation only in the widget — it's bypassed by any other caller and duplicated across screens. Put it in the use case (and/or entity) so it's enforced once.
> *🎯 Really testing:* precise placement of logic.

**Q3. Why must the domain be pure Dart?**
> **A:** So business logic is independent of frameworks — testable in milliseconds without mocks of Flutter or the network, portable, and immune to UI/data changes. If the domain imports Flutter or Dio, that independence is gone.
> *🎯 Really testing:* the *why* behind purity, not just the rule.

**Q4. Does the UI ever call the repository directly?**
> **A:** No. The UI calls use cases; use cases call repositories. This keeps business logic out of the UI and preserves a single entry point into the domain. (Some teams allow trivial reads to skip a use case, but the default is to go through one.)
> *🎯 Really testing:* discipline + awareness of pragmatic exceptions.

**Q5. Entity vs Model vs DTO — distinguish them.**
> **A:** A DTO mirrors the API JSON (data layer). An entity is the pure business object (domain layer). "Model" is an ambiguous term often meaning either; in Clean Architecture we keep DTO (data) and Entity (domain) strictly separate, bridged by a mapper.
> *🎯 Really testing:* vocabulary precision — a frequent junior stumble.

---

## 10. What You Must Be Able To Do By Tonight ✅
- [ ] Explain the use case pattern + why one-per-action.
- [ ] Correctly place 4 different rules across the layers.
- [ ] Prove your domain folder imports nothing from flutter/dio/data.
- [ ] Implement all the TaskFlow use cases + one validation rule.
- [ ] Answer interview Q1–Q5 from memory.

## 11. The One Sentence To Remember 🧠
> **"The domain is the pure-Dart soul of the app — entities are the nouns, use cases are the verbs, and all business rules live here, untouched by any framework, network, or UI."**

➡️ **Next chapter (Day 8):** the data and domain are ready — now we bring the app to life with **Riverpod**, your state-management focus. The four-day deep dive begins.

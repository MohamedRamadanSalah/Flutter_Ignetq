# Day 13 — Tasks · Navigation, Forms & Feedback

**Layer:** UI · **Goal:** Auth-guarded routing + working forms + user feedback.

## 🧠 Theory (60–90 min)
- [ ] `go_router`: routes, params, nested routes, redirects/guards.
- [ ] Auth guard driven by an auth provider.
- [ ] Snackbars/dialogs as side effects via `ref.listen` (not in build).

## 🛠️ Build (3–3.5 hr)
- [ ] Set up `go_router` with routes: login, tasks, task detail, create/edit.
- [ ] Add an **auth redirect**: unauthenticated → login (reads auth provider).
- [ ] Build the create/edit form UI wired to `CreateTaskFormNotifier`.
- [ ] Show success/error feedback via `ref.listen` on the submit state.
- [ ] Add **pull-to-refresh** + **infinite scroll** to the task list UI.

## 📝 Document — copy template → `day 13/`
- [ ] Routing + auth-guard pattern.
- [ ] Form-to-state wiring + side-effect handling.

## ✅ Definition of Done
- [ ] Guarded routing works. [ ] Form creates a task. [ ] Pull-to-refresh + infinite scroll work.

## 🔁 Recall test
- [ ] Explain why feedback (snackbars) goes in `ref.listen`, not `build`.

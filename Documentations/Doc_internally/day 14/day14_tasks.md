# Day 14 — Tasks · UI Performance & Polish

**Layer:** UI · **Goal:** Fast, polished UI + file upload. (Most cuttable day if behind.)

## 🧠 Theory (60–90 min)
- [ ] `const` constructors + why they cut rebuilds.
- [ ] `select` + splitting widgets to localize rebuilds.
- [ ] List virtualization (`ListView.builder`), image caching, skeletons/shimmer.
- [ ] Multipart file upload + progress.

## 🛠️ Build (3–3.5 hr)
- [ ] Audit rebuilds (use Flutter DevTools / `debugPrint` in build) and fix hotspots.
- [ ] Add loading **skeletons/shimmer** for the list.
- [ ] Add proper **empty + error** states everywhere.
- [ ] Build avatar/attachment **upload** (multipart) with a progress indicator.
- [ ] Apply consistent theming (Material 3, color scheme, typography).

## 📝 Document — copy template → `day 14/`
- [ ] Performance checklist.
- [ ] Rebuild-debugging notes + upload-progress recipe.

## ✅ Definition of Done
- [ ] No needless rebuilds. [ ] Skeletons + states polished. [ ] Upload shows progress.

## 🔁 Recall test
- [ ] List 4 concrete ways to reduce widget rebuilds in Flutter.

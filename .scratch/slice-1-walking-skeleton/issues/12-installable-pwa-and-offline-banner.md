# 12: Installable PWA and offline banner

**What to build:** The Owner can install Liasse on their phone's home screen. A manifest with icons and a service worker that caches the app shell make it installable. Liasse is online-only: when the device is offline, a banner says so and uploads are disabled.

**Blocked by:** 01 (Skeleton)

**Status:** ready-for-agent

- [ ] Manifest with name, icons and theme; the app passes installability checks in the browser
- [ ] The service worker caches the app shell only, never API responses or Documents
- [ ] An offline banner appears and disappears with connectivity
- [ ] Uploading is disabled while offline
- [ ] Frontend tests cover the offline banner and the disabled upload

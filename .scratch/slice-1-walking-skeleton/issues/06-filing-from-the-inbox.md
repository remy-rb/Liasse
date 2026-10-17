# 06: Filing from the Inbox

**What to build:** The Owner opens the Inbox, sees every Document waiting there with Liasse's guesses and why each uncertain field was flagged, and files it by confirming or correcting the Category, Correspondent (pick an existing one or type a new one) and Document Date. Filing moves the file from `Inbox/` to its place in the Archive and marks the Document Filed. The Inbox count is visible in the navigation.

**Blocked by:** 05 (Automatic filing)

**Status:** ready-for-agent

- [ ] Inbox view lists Inbox Documents with guesses and per-field reasons
- [ ] Navigation shows the Inbox count
- [ ] Filing with confirmed or corrected fields moves the file to `<Category>/<Correspondent>/` with the standard name and sets status Filed
- [ ] Typing a new Correspondent creates it
- [ ] The file no longer exists in `Inbox/` after filing
- [ ] Backend tests through the API and frontend tests (MSW) cover filing

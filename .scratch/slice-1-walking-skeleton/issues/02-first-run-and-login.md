# 02: First-run setup and login

**What to build:** The first time Liasse runs, the Owner is asked to set a password, which creates the single Owner. Afterwards the Owner logs in, stays logged in through an HTTP-only session cookie, and can log out. Every API route except first-run setup, login and health requires a session, and the PWA redirects to login when the session is missing. Every later table is scoped by Owner (ADR-0001), so this ticket introduces the Owner record.

**Blocked by:** 01 (Skeleton)

**Status:** ready-for-agent

- [ ] With no Owner, the app shows first-run setup; setting a password creates the Owner (password hashed) and logs in
- [ ] First-run setup is impossible once an Owner exists
- [ ] Login with the right password sets a session cookie; a wrong password is rejected without revealing details
- [ ] Logout clears the session
- [ ] Protected routes return 401 without a session; the PWA redirects to login
- [ ] Session secret comes from Settings
- [ ] Backend tests through the HTTP API cover setup, login, logout and protection; frontend tests (MSW) cover the setup and login screens

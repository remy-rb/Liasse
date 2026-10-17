# 03: Upload and processing jobs

**What to build:** The Owner uploads one or several PDFs or images from the Upload screen. Each file becomes a Document with status Processing and a processing job stored in Postgres. A separate worker process claims jobs (row locking with skip-locked), stores the untouched original under `<Owner>/.originals/<document-id>/` in the Archive, converts images to PDF, and writes the PDF flat into `<Owner>/Inbox/`, setting the status to Inbox. The Documents list shows each Document's status and polls while any is Processing. All Archive access goes through fsspec using `STORAGE_URL` (local `file://` here). No OCR or classification yet: every Document ends in the Inbox. This ticket also introduces the Models seam's fake (for later tickets) and the first fixture Documents.

**Blocked by:** 02 (First-run setup and login)

**Status:** ready-for-agent

- [ ] Upload accepts PDF, JPEG, PNG and HEIC; other types and corrupt files are rejected with a clear reason
- [ ] Files above the configured size limit are rejected
- [ ] Several files in one upload each become their own Document; a multi-page PDF is one Document
- [ ] Upload returns immediately; the Document is Processing until the worker finishes
- [ ] The worker stores the original under `.originals/<document-id>/` and a PDF in `Inbox/`; status becomes Inbox
- [ ] Two workers never process the same job
- [ ] The worker exposes a "run pending jobs" entry point used by tests in-process
- [ ] Documents list (newest first) shows status and refreshes while anything is Processing
- [ ] Tests run with storage on fsspec `memory://` and assert on the storage tree
- [ ] A Models fake (scripted classify/answer, deterministic embed) and a few anonymised French and English fixture Documents exist for later tickets

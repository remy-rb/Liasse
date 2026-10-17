# The Archive is a read-only mirror of the app, in configurable storage

Owners must be able to browse their Documents without the web app, so Liasse writes every Document as a searchable PDF into a real folder tree, the Archive (`<Owner>/<Category>/<Correspondent>/`, plus `<Owner>/Inbox/`), and keeps the untouched originals under `<Owner>/.originals/<document-id>/` so Documents can be reprocessed later. The Archive lives wherever `STORAGE_URL` points (via fsspec): local disk by default, or S3 and S3-compatible services; Google Drive, Dropbox or a NAS are reached by pointing local storage at a synced or rclone-mounted folder rather than by native integrations. "Browsing without the app" means through that storage's own tools. The app's records are the source of truth: Liasse writes the Archive and does not support changes made in it. Treating storage as the truth would mean watching files, resolving conflicts and keeping the RAG index in step with arbitrary edits, which is out of scope for now; a "rescan" could be added later.

## Consequences

- On S3 there are no real folders, so renaming a Category copies and deletes every object under it; acceptable at personal scale.

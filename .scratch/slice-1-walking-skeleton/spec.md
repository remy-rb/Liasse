# Spec: Slice 1, walking skeleton

Status: ready-for-agent

## Problem Statement

People with piles of paper (bills, payslips, tax notices, medical letters, contracts) have no easy way to turn them into something they can find again. Scanning apps produce a heap of badly named files; filing them by hand into folders is tedious and rarely kept up; and once filed, answering a simple question like "how much did I pay EDF last year?" still means opening documents one by one. They want to hand Liasse a Document and have it filed in the right place automatically, in a form they can browse without any special app, and then be able to ask questions across everything they own and get answers they can verify.

## Solution

Liasse is a self-hostable web service with an installable React PWA. In this first slice the Owner logs in, uploads a PDF or image, and Liasse processes it in the background: it runs OCR (French and English), works out the Category, Correspondent and Document Date, and writes a searchable PDF into the Archive at `<Owner>/<Category>/<Correspondent>/`, or into the Inbox when it isn't confident. The Owner can browse the Archive with ordinary tools (Finder, an S3 browser, a synced Drive folder), see each Document's status in the app, file Inbox Documents themselves, Search across their Documents, and ask Questions in French or English whose Answers cite the exact Document and page.

The whole stack starts with a couple of Makefile commands, and the LLM provider (Claude, OpenAI or Ollama) and the storage backend (local disk or S3) are chosen through environment variables.

## User Stories

### Setup and access

1. As a self-hoster, I want to start Liasse with `make setup` and `make up`, so that I can run it without reading a long install guide.
2. As a developer, I want `make dev` to start Postgres in Docker and the backend, worker and frontend with hot reload, so that I can iterate quickly.
3. As a self-hoster, I want a `.env.example` listing every setting with a comment, so that I know what I can configure.
4. As a self-hoster, I want to choose my LLM provider (Claude, OpenAI or Ollama) through environment variables, so that I can trade privacy, cost and quality as I see fit.
5. As a self-hoster, I want to point Liasse at an Ollama instance by its base URL, so that no Document text leaves my network.
6. As a self-hoster, I want to choose where the Archive lives with a single `STORAGE_URL`, so that I can keep it on local disk or in S3.
7. As a self-hoster, I want local storage to be the default, so that Liasse works out of the box without any cloud account.
8. As a self-hoster, I want to use S3-compatible services (MinIO, Cloudflare R2, Backblaze B2) by setting an endpoint and keys, so that I'm not tied to AWS.
9. As a self-hoster, I want the README to explain how to point local storage at a Google Drive, Dropbox or rclone-mounted folder, so that my Archive appears in the tools I already use.
10. As a self-hoster, I want Liasse to refuse to start with a clear message when required settings are missing or invalid, so that I don't discover misconfiguration halfway through processing.
11. As an Owner, on first run, I want to set my password, so that nobody else on my network can see my Documents.
12. As an Owner, I want to log in and stay logged in on my devices, so that I don't type my password every time.
13. As an Owner, I want to log out, so that I can hand my device to someone else safely.
14. As an Owner, I want every page except login and first-run setup to require me to be logged in, so that my Documents are never exposed by accident.
15. As an Owner, I want to install Liasse on my phone's home screen as a PWA, so that it feels like an app.
16. As an Owner, I want the app to tell me clearly when I'm offline, so that I don't think a Capture was sent when it wasn't.

### Capture

17. As an Owner, I want to upload a PDF, so that Documents I already have digitally end up in my Archive.
18. As an Owner, I want to upload an image (JPEG, PNG, HEIC from my phone), so that a photo I already took becomes a Document.
19. As an Owner, I want to upload several files at once, each becoming its own Document, so that I can clear a backlog quickly.
20. As an Owner, I want a multi-page PDF to become a single Document, so that a letter isn't split across files.
21. As an Owner, I want unsupported or corrupt files to be rejected with a clear reason, so that I know what to fix.
22. As an Owner, I want files above a size limit to be rejected before upload finishes, so that I don't wait for something that will fail.
23. As an Owner, I want the upload to return immediately and processing to continue in the background, so that I can keep using the app.

### Processing and filing

24. As an Owner, I want each Document to show a status of Processing, Filed or Inbox, so that I know where it is.
25. As an Owner, I want the status to update without reloading the page, so that I can watch a Document get filed.
26. As an Owner, I want Liasse to OCR my Documents in French and English, so that their text is searchable whichever language they're in.
27. As an Owner, I want Liasse to determine the Category of each Document from the default set, so that I don't sort them by hand.
28. As an Owner, I want Liasse to determine the Correspondent of each Document, so that Documents from the same sender are grouped.
29. As an Owner, I want Liasse to recognise that "EDF SA" and "Électricité de France" are my existing Correspondent "EDF", so that my Archive doesn't split into near-duplicate folders.
30. As an Owner, I want a genuinely new Correspondent to be created automatically, so that I'm not interrupted for every new sender.
31. As an Owner, I want Liasse to read the Document Date printed on the paper, so that files are dated by when they were issued, not when I captured them.
32. As an Owner, I want Liasse to give each Document a short title, so that its file name tells me what it is.
33. As an Owner, I want a Document to be Filed only when Liasse is confident about its Category, Correspondent and Document Date, so that my Archive isn't polluted by guesses.
34. As an Owner, I want uncertain Documents to go to the Inbox, so that I can check them.
35. As an Owner, I want to see why a Document is in the Inbox (which field was uncertain and what Liasse guessed), so that filing it takes seconds.
36. As a self-hoster, I want the confidence threshold to be a setting, so that I can tune how often Documents land in the Inbox.
37. As an Owner, I want a Document whose processing failed (unreadable image, provider down) to show a Failed status with the reason and a Retry action, so that nothing silently disappears.
38. As an Owner, I want processing to survive a server restart, so that Documents I uploaded before a reboot still get filed.
39. As an Owner, I want the ten default Categories (Invoices, Bank, Payslips, Taxes, Health, Insurance, Housing, Vehicle, Contracts, Identity) to exist from the start, so that filing works immediately.
40. As an Owner, I want there to be no catch-all "Other" Category, so that unclear Documents come to my Inbox instead of disappearing into a dumping ground.

### The Inbox

41. As an Owner, I want an Inbox view listing every Document waiting for me, so that I can clear it.
42. As an Owner, I want to file an Inbox Document by confirming or correcting its Category, Correspondent and Document Date, so that it moves into the right place in my Archive.
43. As an Owner, I want to pick an existing Correspondent or type a new one when filing, so that I can fix Liasse's mistakes.
44. As an Owner, I want to see the Inbox count at a glance, so that I know when something needs me.

### The Archive

45. As an Owner, I want every Document written to my Archive as a searchable PDF, so that it opens in any PDF viewer and its text can be searched by my OS.
46. As an Owner, I want Filed Documents stored under `<Category>/<Correspondent>/`, so that I can browse my Archive without Liasse.
47. As an Owner, I want Inbox Documents stored flat in an `Inbox` folder of my Archive, so that I can see them outside the app too.
48. As an Owner, I want files named `YYYY-MM-DD_<Correspondent>_<short-title>.pdf`, so that they sort by date and are readable at a glance.
49. As an Owner, I want two Documents with the same name to get `-2`, `-3` suffixes rather than overwrite each other, so that I never lose a Document.
50. As an Owner, I want names to be safe on every filesystem (no slashes or reserved characters), so that my Archive syncs to Drive, Dropbox or a NAS without errors.
51. As an Owner, I want filing an Inbox Document to move its file from `Inbox` to the right folder, so that the Archive always matches the app.
52. As an Owner, I want the original upload kept untouched under a hidden `.originals` folder, so that Documents can be reprocessed later with better models.
53. As an Owner, I want my Archive to live under my Owner folder, so that a future multi-Owner install keeps everyone's Documents apart.

### Documents

54. As an Owner, I want a list of my Documents, newest first, showing title, Category, Correspondent, Document Date and status, so that I can see what I have.
55. As an Owner, I want to filter the list by Category and Correspondent, so that I can narrow it down.
56. As an Owner, I want to open a Document and view its pages, so that I can read it in the app.
57. As an Owner, I want to download a Document's searchable PDF, so that I can share or print it.

### Search

58. As an Owner, I want to Search my Documents with a natural-language query, so that I find things without remembering exact words.
59. As an Owner, I want Search to work across French and English (a query in English finds a French Document), so that language doesn't hide anything.
60. As an Owner, I want Search results to show the Document, the matching page and a snippet, so that I can tell which result I want.
61. As an Owner, I want to open a result at its matching page, so that I don't have to hunt for it.
62. As an Owner, I want Search to cover only my own Documents, so that a future multi-Owner install never leaks others' data.

### Questions and Answers

63. As an Owner, I want to ask a Question in French or English across my Documents, so that I get a direct Answer instead of a list of files.
64. As an Owner, I want the Answer in the language I asked in, so that I can read it naturally.
65. As an Owner, I want every Answer to come with Citations to the exact Document and page, so that I can verify it.
66. As an Owner, I want to open a Citation and land on the cited page, so that checking takes one tap.
67. As an Owner, I want Liasse to say plainly when my Documents don't contain the answer, so that I'm never given an invented one.
68. As an Owner, I want each Question to be answered on its own, so that the behaviour is predictable (no hidden conversation memory).
69. As an Owner, I want Questions to consider only Documents that have finished processing, so that half-processed Documents don't produce wrong Answers.

### Developer experience and portfolio

70. As a developer, I want `make test` to run the backend and frontend test suites, so that I can check everything with one command.
71. As a developer, I want `make lint` to lint and type-check both sides, so that style and type errors are caught early.
72. As a developer, I want `make api-client` to regenerate the TypeScript client from the backend's OpenAPI schema, so that frontend and backend never drift apart.
73. As a developer, I want `make eval` to run the real models against fixture Documents and report classification accuracy, so that I can measure and showcase model quality.
74. As a developer, I want tests to run without any API key or network access, so that CI is free and deterministic.
75. As a portfolio reader, I want the README to explain the architecture, the RAG pipeline and the ADRs, so that I understand the design choices.

## Implementation Decisions

### Shape

- One repository with a FastAPI backend (managed with `uv`), a Vite + React + TypeScript frontend following the bulletproof-react structure, a root Docker Compose file and a Makefile.
- Docker Compose runs Postgres (with pgvector), the API, the worker and the frontend. A MinIO service is available for S3 development and tests.
- Makefile targets: `setup`, `dev`, `up`, `down`, `test`, `lint`, `api-client`, `eval`.

### Backend modules

- **Settings**: reads and validates all environment configuration at startup and fails fast with a clear message. Covers database URL, `STORAGE_URL` (plus S3 endpoint and credentials), LLM provider/model/API key/base URL, Inbox confidence threshold (default 0.7), upload size limit, session secret.
- **Auth**: single-Owner authentication. First-run setup creates the Owner and its password (hashed). Login issues an HTTP-only session cookie. Every API route except first-run setup, login and health requires a session.
- **Documents**: the Document record and its lifecycle. A Document has an Owner, a status (`processing`, `filed`, `inbox`, `failed`), title, Category, Correspondent, Document Date, per-field confidences and guesses, page count, failure reason, the Archive path of its searchable PDF and the path of its original. The API covers upload, list (with Category and Correspondent filters), get, file (confirm or correct Category, Correspondent and Document Date), retry and download.
- **Categories**: seeded with the ten defaults on first run, per Owner. Read-only through the API in this slice.
- **Correspondents**: per Owner. Matching an extracted name against existing Correspondents is done by giving the model the Owner's existing Correspondent names during classification and asking it to return either an existing name or a new one; a new name creates a Correspondent.
- **Jobs and worker**: processing jobs are rows in Postgres, claimed by a separate worker process using row locking with skip-locked so several workers never take the same job. A job left claimed by a crashed worker is picked up again after a timeout. Jobs that fail are marked failed with a reason; retry re-queues them. The worker exposes a "run pending jobs" entry point that tests call in-process.
- **Pipeline** (what a job does): store the original in the Archive's originals area; run OCRmyPDF (French and English, with deskew) to produce a searchable PDF and per-page text; classify; decide Filed vs Inbox against the threshold (Inbox if any of Category, Correspondent or Document Date is below it); write the searchable PDF to its Archive path; split text into one chunk per page; embed each chunk and store it in pgvector; update the Document. Images are converted to PDF before OCR.
- **Archive**: all reads and writes go through fsspec using `STORAGE_URL` (`file://` by default, `s3://` supported). Owns path building: `<Owner>/<Category>/<Correspondent>/YYYY-MM-DD_<Correspondent>_<short-title>.pdf`, `<Owner>/Inbox/<same name>.pdf`, `<Owner>/.originals/<document-id>/<original filename>`. Names are sanitised for cross-platform safety and de-duplicated with `-2`, `-3` suffixes. Filing moves the file. The Archive is write-only from the app: changes made directly in storage are not detected (ADR-0002).
- **Models** (the single test seam): a small module exposing three operations: `classify(text, categories, correspondents) → {category, correspondent, document_date, title, confidences}`, `answer(question, chunks) → {text, cited chunk ids}` and `embed(texts) → vectors`. Classification and answering call the configured LLM through LiteLLM; embedding always uses the local `multilingual-e5-small` sentence-transformers model (ADR-0003). Classification asks for structured JSON output and validates it; invalid output fails the job with a clear reason.
- **Search**: embeds the query, runs a pgvector similarity search over chunks filtered by Owner and by Documents that are not processing or failed, and returns Document, page and snippet.
- **Questions**: retrieves the top chunks the same way, asks the model to answer only from them in the Question's language, and returns the Answer with Citations (Document id, title, page). If the model finds nothing relevant, the Answer says so and carries no Citations. No conversation history.
- **Ownership**: every table and every query is scoped by Owner, including the vector search (ADR-0001).

### Data (Postgres)

- `owner`, `category`, `correspondent`, `document`, `chunk` (document, page number, text, embedding vector), `job` (document, state, attempts, claimed-at, error). Category and Correspondent names are unique per Owner. Migrations are managed with Alembic.

### API contract

- JSON over HTTP, described by FastAPI's OpenAPI schema. The frontend's TypeScript client and types are generated from that schema (`make api-client`), never hand-written.
- Status updates are delivered by polling the Document list while any Document is processing (no websockets in this slice).

### Frontend

- Vite + React + TypeScript, bulletproof-react layout: `app` (routes, providers), `features/<feature>` (auth, documents, inbox, search, questions, capture), shared `components` and `lib`. TanStack Query for server state.
- Screens: first-run setup, login, Documents (list with filters and statuses, Document view with page viewer and download), Upload, Inbox (with the guesses and per-field reasons, and a file form), Search, Ask (Question box, Answer with clickable Citations).
- Installable PWA (manifest, icons, service worker caching the app shell only). Online only: an offline banner is shown and uploads are disabled while offline.

## Testing Decisions

- Good tests check behaviour through the highest public interface and never assert on internals, so refactors don't break them.
- **Backend**: tests go through the HTTP API with an async test client, and run the worker's "run pending jobs" entry point in-process. They use a real Postgres with pgvector and the real OCRmyPDF, and storage set to fsspec's `memory://`. The only fake is the **Models** module, replaced by scripted classifications, Answers and deterministic embeddings. Archive assertions inspect the storage tree (paths, names, file present, PDF has a text layer). A separate small set of tests runs the Archive against MinIO to prove `s3://` works.
- Backend behaviours to cover: first-run and login; auth required everywhere; upload validation; PDF and image processing to Filed; Inbox below threshold with reasons; existing-Correspondent matching and new-Correspondent creation; name collisions and sanitising; filing an Inbox Document moves the file; failure and retry; job survives a "restart" (claimed job re-taken after timeout); Owner scoping of lists, Search and Questions; Search returns page and snippet; Questions return Citations, refuse to invent, and ignore processing Documents.
- **Frontend**: Vitest and Testing Library per feature, with the API mocked by MSW using the generated types. Cover login/first-run, upload and status polling, Inbox filing, Search results, Question with Citations, and the offline banner.
- **Fixtures**: a small set of anonymised French and English invoices and payslips (PDF and photo) with their expected Category, Correspondent and Document Date, used by both tests and `make eval`.
- **Eval**: `make eval` runs the real Models against the fixtures and reports per-field accuracy and how many would go to the Inbox. Opt-in, needs a configured provider, not part of `make test`.
- **Prior art**: none yet, as the repo is empty. These tests establish the patterns.

## Out of Scope

- Camera Capture in the PWA, page edge detection, cropping and straightening (slice 2).
- HTTPS through Traefik and the certificate approach for home-network use (slice 2).
- Adding, renaming or deleting Categories (slice 2), and renaming or merging Correspondents.
- Offline Capture queue.
- Native Google Drive, Dropbox or OneDrive integration (use a synced or mounted folder).
- Detecting or importing changes made directly in the Archive ("rescan").
- Conversational Questions with history or follow-ups.
- Multiple Owners, sign-up, password reset and SaaS billing (the data model is ready for them per ADR-0001).
- Configurable embedding model.
- Reprocessing existing Documents with a new model (originals are kept so it can be added later).
- Deleting Documents.
- A French UI (the UI is English; Documents, Questions and Answers can be French or English).

## Further Notes

- This is a portfolio project: the README should present the architecture, the processing pipeline, the RAG flow and the three ADRs, and `make eval` results are worth showing.
- Choosing a hosted LLM sends page text to that provider; the README should say so and point to Ollama for full privacy.
- Read `GLOSSARY.md` before naming anything; use its terms (Document, Capture, Category, Correspondent, Document Date, Filed, Inbox, Archive, Owner, Search, Question, Answer, Citation) in code, UI copy and tests.
- Relevant ADRs: 0001 (Owner on every record), 0002 (Archive is a read-only mirror, in configurable storage), 0003 (local embeddings).

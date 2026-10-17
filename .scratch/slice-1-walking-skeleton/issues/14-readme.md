# 14: README for self-hosters and portfolio readers

**What to build:** A README that lets a self-hoster go from clone to a running Liasse, and lets a portfolio reader understand the design. It covers setup with the Makefile, every environment variable, choosing an LLM provider and its privacy implications (hosted providers receive page text; Ollama keeps it local), pointing local storage at a Google Drive, Dropbox or rclone-mounted folder, S3 setup, the architecture, the processing pipeline and RAG flow, the three ADRs, and `make eval` results.

**Blocked by:** 10 (Questions with Citations), 11 (S3 storage), 13 (Fixtures and eval)

**Status:** ready-for-agent

- [ ] A newcomer can follow the README from clone to first filed Document
- [ ] Every setting in `.env.example` is explained
- [ ] The privacy implications of each LLM provider are stated plainly
- [ ] Google Drive / Dropbox / rclone and S3 setups are documented
- [ ] Architecture, pipeline and RAG flow are explained with links to the ADRs and the glossary
- [ ] Latest `make eval` results are included

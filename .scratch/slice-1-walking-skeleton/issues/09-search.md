# 09: Search

**What to build:** Processing now splits each Document's text into one chunk per page and embeds the chunks locally with `multilingual-e5-small` (ADR-0003) into pgvector. The Owner types a natural-language query on the Search screen and gets matching Documents with the page and a snippet, across French and English, and opens a result at its page. Search covers only the Owner's Documents that are not Processing or Failed.

**Blocked by:** 04 (OCR)

**Status:** ready-for-agent

- [ ] Each processed Document has one embedded chunk per page
- [ ] Search returns Document, page number and snippet, best matches first
- [ ] A query in one language can find a Document in the other (verified with the real model in `make eval` or a marked slow test; the fake covers ranking logic)
- [ ] Results exclude other Owners' Documents and Documents that are Processing or Failed
- [ ] Inbox Documents are searchable
- [ ] Clicking a result opens the Document at that page
- [ ] Tests use the Models fake for embeddings

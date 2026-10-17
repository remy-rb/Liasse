# 10: Questions with Citations

**What to build:** On the Ask screen the Owner asks a Question in French or English. Liasse retrieves the most relevant chunks (same scoping as Search), asks the configured LLM to answer only from them, and shows the Answer in the Question's language with Citations to the exact Document and page; clicking a Citation opens that page. If the Documents don't contain the answer, Liasse says so and shows no Citations. Each Question stands alone, with no conversation history.

**Blocked by:** 09 (Search)

**Status:** ready-for-agent

- [ ] The API takes a Question and returns Answer text and Citations (Document id, title, page)
- [ ] The Answer is in the Question's language
- [ ] When nothing relevant is found, the Answer says so and has no Citations
- [ ] Only the Owner's processed Documents are used
- [ ] Citations open the Document at the cited page
- [ ] Tests use the Models fake for both retrieval and answering

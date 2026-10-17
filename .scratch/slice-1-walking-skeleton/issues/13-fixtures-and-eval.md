# 13: Fixtures with expected labels and `make eval`

**What to build:** A set of anonymised French and English fixture Documents (invoices and payslips at least, as PDFs and phone photos) with their expected Category, Correspondent and Document Date. `make eval` runs the real configured models over them and reports per-field accuracy and how many would land in the Inbox at the current threshold. It is opt-in and not part of `make test`.

**Blocked by:** 05 (Automatic filing)

**Status:** ready-for-agent

- [ ] Fixtures contain no real personal data
- [ ] Each fixture has its expected Category, Correspondent and Document Date recorded alongside it
- [ ] `make eval` runs the full pipeline with the real models and prints per-field accuracy and the Inbox rate
- [ ] `make eval` fails clearly if no LLM provider is configured
- [ ] `make test` stays free of network and API keys

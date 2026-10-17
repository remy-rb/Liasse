# 05: Automatic filing

**What to build:** After OCR, Liasse classifies each Document and files it. The ten default Categories (Invoices, Bank, Payslips, Taxes, Health, Insurance, Housing, Vehicle, Contracts, Identity, no "Other") are seeded for the Owner. `Models.classify` receives the text, the Categories and the Owner's existing Correspondents, and returns Category, Correspondent (an existing name or a new one), Document Date, short title and a confidence for each field, through LiteLLM with structured, validated output. A new Correspondent is created automatically. If any of Category, Correspondent or Document Date is below the configured threshold (default 0.7), the Document stays in the Inbox with its guesses and the reason recorded; otherwise it is Filed and written to `<Owner>/<Category>/<Correspondent>/YYYY-MM-DD_<Correspondent>_<short-title>.pdf`.

**Blocked by:** 04 (OCR)

**Status:** ready-for-agent

- [x] Default Categories exist for the Owner after first-run setup
- [x] LLM provider, model, API key or base URL come from Settings (Claude, OpenAI and Ollama supported via LiteLLM)
- [x] A confident classification Files the Document at the right Archive path with the right name
- [x] A classification naming an existing Correspondent reuses it; an unknown one creates it
- [x] Any field below the threshold sends the Document to `Inbox/` with guesses and per-field reasons stored
- [x] Names are sanitised for every filesystem; collisions get `-2`, `-3` suffixes and never overwrite
- [x] Invalid model output fails clearly rather than filing garbage
- [x] The Documents list shows Category, Correspondent, Document Date and title
- [x] Tests use the Models fake to cover Filed, Inbox, Correspondent reuse/creation and naming

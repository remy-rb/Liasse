# 04: OCR

**What to build:** Processing now runs OCRmyPDF (French and English, with deskew) on each Document, so the PDF written to the Archive is a searchable PDF with an invisible text layer that opens in any viewer and is findable by the OS's search. The text of each page is stored with the Document for classification, Search and Questions.

**Blocked by:** 03 (Upload and processing jobs)

**Status:** ready-for-agent

- [ ] The PDF in the Archive has a text layer (verified in tests by extracting text from it)
- [ ] French and English fixtures produce their expected key words in the extracted text
- [ ] Per-page text is stored and linked to the Document and page number
- [ ] A PDF that already has a text layer is still processed correctly
- [ ] The Docker images and `make setup` install Tesseract with French and English language packs

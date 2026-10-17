# Liasse

A self-hostable web service that takes people's paper documents, files them automatically, and lets them search and ask questions across everything they've filed.

## Language

**Document**:
One paper item brought into Liasse (a letter, invoice, payslip, contract), possibly several pages long. The unit that gets filed, searched and cited.
_Avoid_: File, scan, paper, item

**Owner**:
The person whose Documents these are. A self-hosted install has one Owner; everything in Liasse belongs to exactly one.
_Avoid_: User, account, tenant, customer

**Capture**:
Bringing a Document into Liasse, either by photographing its pages with the device's camera or by uploading an existing PDF or image.
_Avoid_: Scan, upload, import

**Category**:
The top-level grouping a Document is filed under (e.g. Invoices, Payslips, Health). Liasse ships a default set; the Owner can add, rename or remove Categories.
_Avoid_: Type, class, tag

**Correspondent**:
Who a Document comes from (EDF, BNP, Dr Martin). Within a Category, Documents are grouped by Correspondent.
_Avoid_: Sender, issuer, vendor, subfolder

**Document Date**:
The date printed on a Document, as opposed to when it was Captured.
_Avoid_: Created date, scan date, upload date

**Filed**:
The state of a Document that has a Category and a Correspondent, as opposed to waiting in the Inbox.
_Avoid_: Sorted, classified, done

**Inbox**:
Where a Document waits when Liasse isn't confident about its Category or Correspondent, until the Owner files it.
_Avoid_: Unsorted, pending, review queue

**Archive**:
The Owner's browsable folder tree of Documents, grouped by Category then Correspondent, plus the Inbox. It can be opened without Liasse.
_Avoid_: Library, vault, storage, folders

**Search**:
Finding the Documents that match a natural-language query.
_Avoid_: Lookup, retrieval

**Question**:
A natural-language request the Owner asks across their Documents, expecting a written Answer.
_Avoid_: Query, prompt, chat

**Answer**:
Liasse's written reply to a Question, always backed by Citations.
_Avoid_: Response, result

**Citation**:
A pointer from an Answer to the exact Document and page it relies on.
_Avoid_: Source, reference, link

# 07: Failure, retry and surviving a restart

**What to build:** When processing a Document fails (unreadable file, OCR error, model provider down, invalid model output), the Document shows status Failed with a readable reason and a Retry action that re-queues it. A job left claimed by a worker that crashed is picked up again after a timeout, so Documents uploaded before a restart still get processed.

**Blocked by:** 03 (Upload and processing jobs)

**Status:** ready-for-agent

- [ ] A failing job marks the Document Failed with the reason; nothing is silently lost
- [ ] Retry re-queues the job and the Document goes back to Processing
- [ ] Attempts are counted on the job
- [ ] A job claimed longer than the timeout is re-claimed by another worker run
- [ ] The UI shows Failed Documents with reason and a Retry button
- [ ] Tests simulate a failure and a crashed worker

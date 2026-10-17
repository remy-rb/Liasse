# 11: S3 storage

**What to build:** A self-hoster sets `STORAGE_URL=s3://bucket/prefix` with an endpoint and credentials, and the whole Archive (originals, Inbox, Filed Documents, moves on filing) works on S3 or an S3-compatible service. A MinIO service is available in Docker Compose for development and tests.

**Blocked by:** 03 (Upload and processing jobs)

**Status:** ready-for-agent

- [ ] S3 endpoint, bucket and credentials come from Settings and are documented in `.env.example`
- [ ] Upload, processing and filing produce the same Archive layout on S3 as on local disk
- [ ] Moving a file (Inbox to Filed) works on S3 (copy then delete)
- [ ] A MinIO service exists in Compose; a dedicated set of tests runs the Archive against it
- [ ] Misconfigured S3 settings fail at startup with a clear message

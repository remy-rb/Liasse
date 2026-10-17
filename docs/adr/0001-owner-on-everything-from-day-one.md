# Every record carries an Owner from day one

Liasse is self-hosted first, with one Owner per install, but may become a SaaS later. Every Document, Category and Correspondent, and every entry in the search index, is scoped to an Owner from the start. Adding that boundary afterwards would mean migrating stored data and re-scoping the RAG index, which costs much more than carrying an Owner field that a single-user install never varies.

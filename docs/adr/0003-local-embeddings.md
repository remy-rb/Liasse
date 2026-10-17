# Embeddings are always computed locally

The LLM used for classification and Answers is configurable per install (Claude, OpenAI or Ollama, via LiteLLM), but embeddings always come from a local multilingual sentence-transformers model (`multilingual-e5-small`) with no setting. Every Document's vectors depend on that model, so changing it means re-indexing everything; fixing it keeps the search index portable across LLM choices, needs no API key, and never sends Document text off the machine just to index it.

# STAR Story: Challenge in RAG Hallucination

- **Situation**: While building a Legal-AI RAG system, the model was hallucinating case citations.
- **Task**: Reduce hallucination and improve latency for a million-document vector store.
- **Action**: Implemented HNSW indexing and a two-stage reranking process (Cross-Encoder). Added a surgical hallucination filter using Regex and LLM-based verification.
- **Result**: Hallucinations dropped by 40% and latency became sub-second.

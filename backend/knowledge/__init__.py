"""Knowledge module — WeKnora-backed knowledge base integration.

Provides knowledge base CRUD, document upload/status tracking,
instrument association, and read-only search with citation-backed excerpts.

Storage boundary:
- PostgreSQL: business metadata, source mapping, import task status
- MinIO: raw document files (managed by existing storage client)
- WeKnora: document parsing, chunking, embedding, retrieval index

WeKnora is NOT the financial truth source. Retrieved excerpts do not
automatically become VERIFIED Evidence.
"""

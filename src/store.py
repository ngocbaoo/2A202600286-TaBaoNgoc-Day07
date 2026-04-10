from __future__ import annotations

from typing import Any, Callable

from .chunking import _dot, compute_similarity
from .embeddings import _mock_embed
from .models import Document


class EmbeddingStore:
    """
    A vector store for text chunks.

    Tries to use ChromaDB if available; falls back to an in-memory store.
    The embedding_fn parameter allows injection of mock embeddings for tests.
    """

    def __init__(
        self,
        collection_name: str = "documents",
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        self._embedding_fn = embedding_fn or _mock_embed
        self._collection_name = collection_name
        self._use_chroma = False
        self._store: list[dict[str, Any]] = []
        self._collection = None
        self._next_index = 0

        try:
            import chromadb
            # Use EphemeralClient for isolated in-memory operation
            self._client = chromadb.EphemeralClient()
            # Delete and recreate to ensure a clean slate for tests
            try:
                self._client.delete_collection(name=collection_name)
            except Exception:
                pass
            self._collection = self._client.create_collection(name=collection_name)
            self._use_chroma = True
        except Exception:
            self._use_chroma = False
            self._collection = None

    def _make_record(self, doc: Document) -> dict[str, Any]:
        embedding = self._embedding_fn(doc.content)
        metadata = doc.metadata.copy()
        if 'doc_id' not in metadata and doc.id:
            metadata['doc_id'] = doc.id
        return {
            "id": f"chunk_{self._next_index}",
            "content": doc.content,
            "embedding": embedding,
            "metadata": metadata,
        }

    def _search_records(self, query: str, records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        # TODO: run in-memory similarity search over provided records
        query_embedding = self._embedding_fn(query)
        similarities = []
        for record in records:
            similarity = compute_similarity(query_embedding, record["embedding"])
            similarities.append((similarity, record))
        similarities.sort(key=lambda x: x[0], reverse=True)
        
        results = []
        for similarity, record in similarities[:top_k]:
            rec = record.copy()
            rec["score"] = similarity
            results.append(rec)
        return results

    def add_documents(self, docs: list[Document]) -> None:
        """
        Embed each document's content and store it.

        For ChromaDB: use collection.add(ids=[...], documents=[...], embeddings=[...])
        For in-memory: append dicts to self._store
        """
        # TODO: embed each doc and add to store
        if self._use_chroma:
            ids = []
            documents = []
            embeddings = []
            metadatas = []
            for doc in docs:
                record = self._make_record(doc)
                ids.append(record["id"])
                documents.append(record["content"])
                embeddings.append(record["embedding"])
                metadatas.append(record["metadata"])
                self._next_index += 1
            self._collection.add(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)
        else:
            for doc in docs:
                record = self._make_record(doc)
                self._store.append(record)
                self._next_index += 1

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Find the top_k most similar documents to query.

        For in-memory: compute dot product of query embedding vs all stored embeddings.
        """
        # TODO: embed query, compute similarities, return top_k
        if self._use_chroma:
            query_embedding = self._embedding_fn(query)
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=['documents', 'embeddings', 'metadatas', 'distances']
            )
            return [
                {
                    "id": results['ids'][0][i],
                    "content": results['documents'][0][i],
                    "embedding": results['embeddings'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "score": 1.0 - (results['distances'][0][i] if results['distances'] else 0),
                }
                for i in range(len(results['ids'][0]))
            ]
        else:
            records = self._search_records(query, self._store, top_k)
            # Add similarity score to records
            query_embedding = self._embedding_fn(query)
            for r in records:
                r["score"] = compute_similarity(query_embedding, r["embedding"])
            return records

    def get_collection_size(self) -> int:
        """Return the total number of stored chunks."""
        # TODO
        if self._use_chroma:
            return self._collection.count()
        else:
            return len(self._store)

    def search_with_filter(self, query: str, top_k: int = 3, metadata_filter: dict = None) -> list[dict]:
        """
        Search with optional metadata pre-filtering.

        First filter stored chunks by metadata_filter, then run similarity search.
        """
        # TODO: filter by metadata, then search among filtered chunks
        if self._use_chroma:
            query_embedding = self._embedding_fn(query)
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=metadata_filter,
                include=['documents', 'embeddings', 'metadatas', 'distances']
            )
            return [
                {
                    "id": results['ids'][0][i],
                    "content": results['documents'][0][i],
                    "embedding": results['embeddings'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "score": 1.0 - (results['distances'][0][i] if results['distances'] else 0),
                }
                for i in range(len(results['ids'][0]))
            ]
        else:
            filtered_records = [r for r in self._store if all(r['metadata'].get(k) == v for k, v in metadata_filter.items())]
            return self._search_records(query, filtered_records, top_k)

    def delete_document(self, doc_id: str) -> bool:
        """
        Remove all chunks belonging to a document.

        Returns True if any chunks were removed, False otherwise.
        """
        if self._use_chroma:
            count_before = self._collection.count()
            self._collection.delete(where={'doc_id': doc_id})
            count_after = self._collection.count()
            return count_after < count_before
        else:
            initial_len = len(self._store)
            self._store = [r for r in self._store if r['metadata'].get('doc_id') != doc_id]
            return len(self._store) < initial_len

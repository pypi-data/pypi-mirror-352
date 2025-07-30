import os
import shutil
import time
from pathlib import Path
from typing import Literal

from tantivy import Document, Index, SchemaBuilder

from .common import SearchIndex, SearchResult, deduplicate_exact, deduplicate_fuzzy


class TantivySearch(SearchIndex):
    def __init__(self, index_path: str):
        self.index_path = Path(index_path)
        self.schema = None
        self.index = None

    def create_schema(self, sample_record: dict):
        schema_builder = SchemaBuilder()
        for key in sample_record.keys():
            if key == "id":
                continue
            schema_builder.add_text_field(key, stored=True, tokenizer_name="en_stem")
        schema_builder.add_text_field(
            "id", stored=True, tokenizer_name="raw", index_option="basic"
        )
        self.schema = schema_builder.build()

    @classmethod
    def from_index(cls, index_path: str):
        index = cls(index_path)
        index.load_index()
        return index

    def load_index(self):
        if not self.index_path.exists():
            raise FileNotFoundError(f"Index not found at {self.index_path}")
        self.index = Index.open(str(self.index_path))

    def build_index(
        self,
        records: list[dict],
        deduplicate_strategy: Literal["exact", "fuzzy", None] = "fuzzy",
        deduplicate_by: str | None = None,
    ):
        if not records:
            raise ValueError("No records to index")

        if not self.schema:
            self.create_schema(records[0])
        assert self.schema is not None, "Schema not created"
        # Create index
        if self.index_path.exists():
            print(f"Removing existing index at {self.index_path} in 5 seconds...")
            time.sleep(5)
            shutil.rmtree(self.index_path)
        os.makedirs(self.index_path, exist_ok=True)
        self.index = Index(self.schema, str(self.index_path))

        # Deduplicate if needed
        if deduplicate_strategy == "exact":
            assert (
                deduplicate_by is not None
            ), "Deduplication by must be specified for exact deduplication"
            records = deduplicate_exact(records, deduplicate_by)
        elif deduplicate_strategy == "fuzzy":
            assert (
                deduplicate_by is not None
            ), "Deduplication by must be specified for fuzzy deduplication"
            records = deduplicate_fuzzy(records, deduplicate_by)

        # Index documents
        writer = self.index.writer()
        for record in records:
            writer.add_document(Document(**{k: [str(v)] for k, v in record.items()}))
        writer.commit()
        writer.wait_merging_threads()

    def search(
        self, queries: list[str], fields: list[str], limit: int = 8
    ) -> list[SearchResult]:
        assert self.index is not None, "Index not built"
        self.index.reload()
        searcher = self.index.searcher()
        results = []

        for query in queries:
            query_obj = self.index.parse_query(query, fields)
            hits = searcher.search(query_obj, limit=limit).hits

            for score, doc_address in hits:
                doc = searcher.doc(doc_address)
                content = {k: v[0] for k, v in doc.to_dict().items()}
                results.append(
                    SearchResult(
                        id=content["id"],
                        score=score,
                        content=content,
                    )
                )

        # Rank fusion using reciprocal rank fusion
        doc_scores = {}
        for rank, result in enumerate(results, 1):
            doc_key = str(result.id)
            if doc_key not in doc_scores:
                doc_scores[doc_key] = 0
            doc_scores[doc_key] += 1 / (60 + rank)

        # Sort and deduplicate
        unique_results = {}
        for result in results:
            doc_key = str(result.id)
            if doc_key not in unique_results:
                unique_results[doc_key] = result

        sorted_results = sorted(
            unique_results.values(),
            key=lambda x: doc_scores[str(x.id)],
            reverse=True,
        )

        return sorted_results[:limit]

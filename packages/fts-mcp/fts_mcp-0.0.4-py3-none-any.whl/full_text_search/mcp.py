#!/usr/bin/env python3
"""
MCP server for full-text search using Tantivy.
Initializes with a fixed JSONL file and provides search/read tools via HTTP.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from fastmcp import FastMCP

from .tantivy_index import TantivySearch


def load_jsonl_data(file_path: str) -> List[dict]:
    """Load data from a JSONL file."""
    data = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                data.append(json.loads(line))
    return data


def preview_text(text: str, max_length: int = 200) -> str:
    """Create a preview of text content."""
    if not text or len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def normalize_field_value(value) -> str:
    """Convert field value to string, handling JSON/list columns."""
    if value is None:
        return ""
    elif isinstance(value, (list, tuple)):
        # Join list/tuple elements with spaces
        return " ".join(str(item) for item in value if item is not None)
    elif isinstance(value, dict):
        # For dict/JSON, join all values
        return " ".join(str(v) for v in value.values() if v is not None)
    else:
        return str(value)


class FullTextSearchMCP:
    """Encapsulates full-text search MCP server functionality."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.search_index: Optional[TantivySearch] = None
        self.original_data: List[dict] = []
        self.config = {
            "data_file": "",
            "id_column": "",
            "text_column": "",
            "searchable_columns": [],
            "index_path": "",
        }

    def initialize(
        self,
        data_file: str,
        id_column: str,
        text_column: str,
        searchable_columns: List[str],
        index_path: Optional[str] = None,
    ) -> None:
        """Initialize the search index."""
        # Load data
        print(f"Loading data from {data_file}...")
        self.original_data = load_jsonl_data(data_file)
        if not self.original_data:
            raise ValueError("No data found in file")

        # Validate columns exist
        sample_record = self.original_data[0]
        missing_cols = []
        if id_column not in sample_record:
            missing_cols.append(id_column)
        if text_column not in sample_record:
            missing_cols.append(text_column)
        for col in searchable_columns:
            if col not in sample_record:
                missing_cols.append(col)

        if missing_cols:
            raise ValueError(f"Missing columns in data: {missing_cols}")

        # Set default index path if not provided
        if index_path is None:
            data_file_path = Path(data_file)
            index_path = str(data_file_path.parent / f"{data_file_path.stem}_index")

        # Create search index
        print(f"Building search index at {index_path}...")
        self.search_index = TantivySearch(index_path)

        # Build index with all searchable columns plus id
        all_columns = [id_column, text_column] + [
            col for col in searchable_columns if col not in [id_column, text_column]
        ]

        # Filter records to only include relevant columns and normalize values
        filtered_records = []
        for record in self.original_data:
            filtered_record = {}
            for col in all_columns:
                if col in record:
                    # Normalize field values (handles JSON/list columns)
                    filtered_record[col] = normalize_field_value(record[col])

            # Ensure id is string
            filtered_record["id"] = str(filtered_record.get(id_column, ""))
            # Remove the original id column if it's different from "id"
            if id_column != "id" and id_column in filtered_record:
                del filtered_record[id_column]
            filtered_records.append(filtered_record)

        # Build index without deduplication (since we don't have a dedupe column specified)
        self.search_index.build_index(filtered_records, deduplicate_strategy=None)

        # Store configuration
        self.config.update(
            {
                "data_file": data_file,
                "id_column": id_column,
                "text_column": text_column,
                "searchable_columns": searchable_columns,
                "index_path": index_path,
            }
        )

        print(
            f"Successfully initialized index with {len(self.original_data)} documents"
        )

    def search(self, query: str, limit: int = 5) -> str:
        """Search documents and return previews."""
        if self.search_index is None:
            return "Error: Search index not initialized"

        try:
            # Search across all searchable columns
            all_searchable = [self.config["text_column"]] + self.config[
                "searchable_columns"
            ]
            # Remove duplicates while preserving order
            search_fields = []
            for field in all_searchable:
                if field not in search_fields and field != self.config["id_column"]:
                    search_fields.append(field)

            results = self.search_index.search([query], search_fields, limit=limit)

            if not results:
                return f"No results found for query: '{query}'"

            # Format results with previews
            formatted_results = [f"Found {len(results)} results for '{query}':\n"]

            for i, result in enumerate(results, 1):
                content = result.content
                doc_id = result.id
                score = result.score

                # Get preview of main text content
                main_text = content.get(self.config["text_column"], "")
                preview = preview_text(main_text)

                formatted_results.append(f"Result {i} (Score: {score:.3f})")
                formatted_results.append(f"ID: {doc_id}")
                formatted_results.append(f"Preview: {preview}")

                # Show other searchable fields (abbreviated)
                for field in self.config["searchable_columns"]:
                    if field != self.config["text_column"] and field in content:
                        value = content[field]
                        if len(str(value)) > 100:
                            value = str(value)[:100] + "..."
                        formatted_results.append(f"{field}: {value}")

                formatted_results.append("")  # Empty line between results

            return "\n".join(formatted_results)

        except Exception as e:
            return f"Error during search: {str(e)}"

    def read_documents(self, document_ids: List[str]) -> str:
        """Retrieve full content for specific document IDs."""
        if self.search_index is None:
            return "Error: Search index not initialized"

        try:
            # Create lookup by ID using cached original data
            id_to_record = {}
            for record in self.original_data:
                doc_id = str(record.get(self.config["id_column"], ""))
                id_to_record[doc_id] = record

            # Retrieve requested documents
            results = []
            found_ids = []
            missing_ids = []

            for doc_id in document_ids:
                if doc_id in id_to_record:
                    results.append(id_to_record[doc_id])
                    found_ids.append(doc_id)
                else:
                    missing_ids.append(doc_id)

            # Format results
            if not results:
                return f"No documents found for IDs: {document_ids}"

            formatted_results = [f"Retrieved {len(results)} documents:\n"]

            for i, record in enumerate(results):
                doc_id = found_ids[i]
                formatted_results.append(f"Document {i + 1} (ID: {doc_id})")
                formatted_results.append("-" * 40)

                # Show all fields
                for key, value in record.items():
                    formatted_results.append(f"{key}: {value}")

                formatted_results.append("")  # Empty line between documents

            if missing_ids:
                formatted_results.append(f"Missing document IDs: {missing_ids}")

            return "\n".join(formatted_results)

        except Exception as e:
            return f"Error retrieving documents: {str(e)}"

    def create_mcp_server(self) -> FastMCP:
        """Create MCP server with tools that have custom descriptions."""
        mcp = FastMCP("full-text-search")

        @mcp.tool(
            name=f"{self.name}_search",
            description=f"Search documents and return previews.\n\nIndex description: {self.description}\n\nArgs:\n\tquery: Search query string\n\tlimit: Maximum number of results to return",
        )
        def search_tool(query: str, limit: int = 5) -> str:
            return self.search(query, limit)

        @mcp.tool(
            name=f"{self.name}_read_docs",
            description=f"Retrieve full content for specific document IDs.\n\nIndex description: {self.description}\n\nArgs:\n\tdocument_ids: List of document IDs to retrieve",
        )
        def read_documents_tool(document_ids: List[str]) -> str:
            return self.read_documents(document_ids)

        return mcp

    def run_server(self, host: str = "0.0.0.0", port: int = 8000) -> None:
        """Run the MCP server."""
        mcp = self.create_mcp_server()
        print(f"Starting MCP server on {host}:{port}")
        print(f"MCP endpoint: http://{host}:{port}/mcp")
        mcp.run(transport="streamable-http", host=host, port=port)


def main():
    """CLI entry point for running the MCP server."""
    parser = argparse.ArgumentParser(description="Full-text search MCP server")

    # Required arguments for server configuration
    parser.add_argument(
        "--name",
        required=True,
        help="Name for the server (should be alpha + underscores)",
    )
    parser.add_argument(
        "--description",
        required=True,
        help="Description of what this search index contains",
    )
    parser.add_argument(
        "--data-file", required=True, help="Path to JSONL file containing documents"
    )
    parser.add_argument(
        "--id-column",
        required=True,
        help="Name of column containing unique document IDs",
    )
    parser.add_argument(
        "--text-column", required=True, help="Name of main text column for content"
    )
    parser.add_argument(
        "--searchable-columns",
        nargs="+",
        required=True,
        help="List of column names to make searchable",
    )

    # Optional arguments
    parser.add_argument(
        "--index-path", help="Path for index storage (defaults to data_file_index)"
    )
    parser.add_argument("--host", default="0.0.0.0", help="Host for HTTP server")
    parser.add_argument("--port", type=int, default=8000, help="Port for HTTP server")

    args = parser.parse_args()

    try:
        # Create and initialize the search server
        search_server = FullTextSearchMCP(name=args.name, description=args.description)
        search_server.initialize(
            data_file=args.data_file,
            id_column=args.id_column,
            text_column=args.text_column,
            searchable_columns=args.searchable_columns,
            index_path=args.index_path,
        )

        # Start HTTP server
        search_server.run_server(host=args.host, port=args.port)

    except Exception as e:
        print(f"Error starting server: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    main()

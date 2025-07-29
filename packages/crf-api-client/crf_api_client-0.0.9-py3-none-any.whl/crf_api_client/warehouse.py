# ruff: noqa: ANN003, D105

from __future__ import annotations

import json
import re
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, List, Type

import requests
from datamodel_code_generator import DataModelType, InputFileType, generate

if TYPE_CHECKING:
    from pydantic import BaseModel

from .base import BaseAPIClient
from .table import Table


def inject_docstring(code: str, class_name: str, docstring: str) -> str:
    """Insert a docstring into a generated class definition."""
    docstring_block = '    """' + docstring.strip().replace("\n", "\n    ") + '"""\n'

    # Use regex to find the class definition
    pattern = rf"(class {re.escape(class_name)}\(.*?\):\n)"

    # Inject the docstring after the class declaration
    return re.sub(pattern, r"\1" + docstring_block, code)


def model_to_code(model_cls: Type[BaseModel], *, class_name: str | None = None) -> str:
    """
    Convert a Pydantic model class into nicely-formatted source code.

    using `datamodel-code-generator` entirely in memory.

    Parameters
    ----------
    model_cls : Type[BaseModel]
        The Pydantic model you want to export.
    class_name : str | None
        Optional new name for the top-level class in the generated file.

    Returns
    -------
    str
        A Python module (including imports) as plain text.

    """
    # 1) Serialize the model`s *schema* (not an instance) to JSON text
    schema_text = json.dumps(model_cls.model_json_schema())
    docstring = model_cls.__doc__ or ""

    # 2) Create a temporary *.py* file, have `generate()` write into it, read it back
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "model.py"
        generate(
            schema_text,
            input_file_type=InputFileType.JsonSchema,
            input_filename=f"{model_cls.__name__}.json",
            output=out_path,
            output_model_type=DataModelType.PydanticV2BaseModel,
            class_name=class_name or model_cls.__name__,
        )
        lines = out_path.read_text().splitlines()
        new_text = "\n".join(lines[6:])
        return inject_docstring(new_text, class_name or model_cls.__name__, docstring)


class Warehouse(BaseAPIClient):
    def __init__(self, base_url: str, token: str, warehouse_id: str, name: str = None, **kwargs):
        super().__init__(base_url, token)
        self.warehouse_id = warehouse_id
        self.name = name
        # Store any additional warehouse attributes
        for key, value in kwargs.items():
            setattr(self, key, value)

    def _get_headers(self):
        return {"Authorization": f"Token {self.token}", "Content-Type": "application/json"}

    def _get_headers_without_content_type(self):
        return {"Authorization": f"Token {self.token}"}

    def _get_paginated_data(self, url: str, params: dict = {}) -> list[dict]:
        next_url = url
        data = []
        use_https = url.startswith("https://")
        is_first_call = True

        while next_url:
            # Ensure HTTPS consistency if base URL uses HTTPS
            if use_https and next_url.startswith("http://"):
                next_url = next_url.replace("http://", "https://")
            if is_first_call:
                response = requests.get(next_url, headers=self._get_headers(), params=params)
                is_first_call = False
            else:
                response = requests.get(next_url, headers=self._get_headers())
            response.raise_for_status()
            response_data = response.json()
            data.extend(response_data["results"])
            next_url = response_data.get("next")

        return data

    # Table-related methods that return Table objects
    def get_table(self, table_identifier: str | int) -> Table:
        """Get a specific table by name or ID and return as Table object"""
        # First try to find by name, then by ID
        tables = self.list_tables()

        for table in tables:
            if table_identifier in (table.name, table.table_id):
                return table

        msg = f"Table '{table_identifier}' not found in warehouse {self.warehouse_id}"
        raise ValueError(msg)

    def create_table(self, table_name: str, columns: list[dict]) -> Table:
        """Create a table in this warehouse and return as Table object"""
        response = requests.post(
            f"{self.base_url}/api/v1/projects/{self.warehouse_id}/tables/",
            headers=self._get_headers(),
            json={"name": table_name, "columns": columns},
        )
        response.raise_for_status()
        data = response.json()

        return Table(
            base_url=self.base_url,
            token=self.token,
            warehouse_id=self.warehouse_id,
            table_id=data.get("id"),
            name=data.get("name"),
            **{k: v for k, v in data.items() if k not in ["id", "name"]},
        )

    def list_tables(self) -> List[Table]:
        """List all tables in this warehouse as Table objects"""
        tables_data = self._get_paginated_data(
            f"{self.base_url}/api/v1/projects/{self.warehouse_id}/tables/"
        )
        tables = []
        for table_data in tables_data:
            table = Table(
                base_url=self.base_url,
                token=self.token,
                warehouse_id=self.warehouse_id,
                table_id=table_data.get("id"),
                name=table_data.get("name"),
                **{k: v for k, v in table_data.items() if k not in ["id", "name"]},
            )
            tables.append(table)
        return tables

    def delete_table(self, table_identifier: str | Table) -> dict:
        """Delete a table by ID, name, or Table object"""
        if isinstance(table_identifier, Table):
            table_id = table_identifier.table_id
        else:
            # Find table by name or ID
            tables = self.list_tables()
            table_id = None
            for table in tables:
                if table_identifier in (table.name, table.table_id):
                    table_id = table.table_id
                    break

            if not table_id:
                msg = f"Table '{table_identifier}' not found in warehouse {self.warehouse_id}"
                raise ValueError(msg)

        response = requests.delete(
            f"{self.base_url}/api/v1/projects/{self.warehouse_id}/tables/{table_id}/",
            headers=self._get_headers(),
        )
        response.raise_for_status()
        return response.json()

    # Settings management
    def update_settings(self, **settings) -> dict:
        """Update warehouse settings"""
        response = requests.patch(
            f"{self.base_url}/api/v1/projects/{self.warehouse_id}/",
            headers=self._get_headers(),
            json=settings,
        )
        response.raise_for_status()
        return response.json()

    # Document management methods
    def upload_documents(
        self, file_paths: List[str], skip_parsing: bool = False, batch_size: int = 10
    ) -> List[dict]:
        """Upload documents to this warehouse"""
        responses = []
        data = {"skip_parsing": "true"} if skip_parsing else {}

        # Process files in batches
        for i in range(0, len(file_paths), batch_size):
            batch = file_paths[i : i + batch_size]
            files_to_upload = []

            try:
                # Open files for current batch
                for file_path in batch:
                    files_to_upload.append(
                        ("files", (file_path.split("/")[-1], open(file_path, "rb")))
                    )

                # Upload current batch
                response = requests.post(
                    f"{self.base_url}/api/v1/projects/{self.warehouse_id}/documents/bulk-upload/",
                    headers=self._get_headers_without_content_type(),
                    files=files_to_upload,
                    data=data,
                )
                response.raise_for_status()
                responses.append(response.json())

            finally:
                # Ensure files are closed even if an error occurs
                for _, (_, file_obj) in files_to_upload:
                    file_obj.close()

        return responses

    def list_documents(self) -> List[dict]:
        """List all documents in this warehouse"""
        return self._get_paginated_data(
            f"{self.base_url}/api/v1/projects/{self.warehouse_id}/documents/"
        )

    def delete_documents(self, document_ids: List[str]) -> dict:
        """Remove documents from this warehouse"""
        response = requests.post(
            f"{self.base_url}/api/v1/projects/{self.warehouse_id}/documents/bulk-delete/",
            headers=self._get_headers(),
            json={"document_ids": document_ids},
        )
        response.raise_for_status()
        return response.json()

    def create_objects_table(self, table_name, object_class):
        data = {
            "name": table_name,
            "columns": [
                {"name": "id", "type": "uuid"},
                {"name": "chunk_id", "type": "uuid"},
                {"name": "json_object", "type": "json"},
                {"name": "object_bbox", "type": "json"},
            ],
            "object_type": "object",
            "object_metadata": {
                "object_name": object_class.__name__,
                "object_pydantic_class": model_to_code(object_class),
            },
        }

        r = requests.post(
            f"{self.base_url}/api/v1/projects/{self.warehouse_id}/tables/",
            headers=self._get_headers(),
            json=data,
        )
        r.raise_for_status()
        data = r.json()

        return Table(
            base_url=self.base_url,
            token=self.token,
            warehouse_id=self.warehouse_id,
            table_id=data.get("id"),
            name=data.get("name"),
        )

    def __repr__(self):
        return f"Warehouse(id='{self.warehouse_id}', name='{self.name}')"

    def __str__(self):
        return f"Warehouse: {self.name} ({self.warehouse_id})"

    def retrieve_with_semantic_search(
        self, query: str, n_objects: int = 10, indexes: list[str] = []
    ) -> list[dict]:
        if not indexes:
            indexes = ["chunks"]
        """Retrieve objects from this warehouse with semantic search"""
        response = requests.post(
            f"{self.base_url}/api/v1/projects/{self.warehouse_id}/retrieve-with-naive/",
            headers=self._get_headers(),
            json={"query": query, "n_objects": n_objects, "indexes": indexes},
        )
        response.raise_for_status()
        return response.json()

    def retrieve_with_cypher(self, cypher_query: str) -> list[dict]:
        response = requests.post(
            f"{self.base_url}/api/v1/projects/{self.warehouse_id}/run-neo4j-query/",
            headers=self._get_headers(),
            json={"cypher_query": cypher_query},
        )
        response.raise_for_status()
        return response.json()

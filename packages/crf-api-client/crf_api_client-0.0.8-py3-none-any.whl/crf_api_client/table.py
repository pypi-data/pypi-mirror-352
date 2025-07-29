# ruff: noqa: ANN003, D105
import json
from typing import Optional

import requests

from .base import BaseAPIClient


class Table(BaseAPIClient):
    def __init__(
        self,
        base_url: str,
        token: str,
        warehouse_id: str,
        table_id: str,
        name: str = None,
        **kwargs,
    ):
        super().__init__(base_url, token)
        self.warehouse_id = warehouse_id
        self.table_id = table_id
        self.name = name
        # Store any additional table attributes
        for key, value in kwargs.items():
            setattr(self, key, value)

    def write_data(self, data: list[dict], override: bool = False) -> dict:
        """Write data to this table"""
        if isinstance(data, dict):
            data = [data]
        if isinstance(data, list):
            data = json.dumps(data)
        response = requests.post(
            f"{self.base_url}/api/v1/projects/{self.warehouse_id}/write-data/?table_name={self.name}",
            headers=self._get_headers(),
            json={"table_name": self.name, "data": data, "override": override},
        )
        response.raise_for_status()
        return response.json()

    def get_data(
        self,
        offset: int = 0,
        limit: int = 10000,
        remove_embeddings: bool = True,
        chunk_id: Optional[str] = None,
        document_id: Optional[str] = None,
    ) -> list[dict]:
        """Download data from this table"""
        params = {
            "table_name": self.name,
            "remove_embeddings": str(remove_embeddings).lower(),
            "offset": offset,
            "limit": limit,
        }

        if chunk_id:
            params["chunk_id"] = chunk_id
        if document_id:
            params["document_id"] = document_id

        return self._get_paginated_data(
            f"{self.base_url}/api/v1/projects/{self.warehouse_id}/get-data/", params=params
        )

    def push_to_retrieval(self) -> dict:
        if self.name == "chunks":
            response = requests.post(
                f"{self.base_url}/api/v1/projects/{self.warehouse_id}/build-table/",
                headers=self._get_headers(),
                json={
                    "table_name": "pushed_chunks",
                    "pipeline_name": "push_chunks",
                    "mode": "recreate-all",
                },
            )
        else:
            response = requests.post(
                f"{self.base_url}/api/v1/projects/{self.warehouse_id}/tables/{self.table_id}/push-objects/",
                headers=self._get_headers(),
                json={},
            )
        response.raise_for_status()
        return response.json()

    def __repr__(self):
        return (
            f"Table(id='{self.table_id}', name='{self.name}', warehouse_id='{self.warehouse_id}')"
        )

    def __str__(self):
        return f"Table: {self.name} ({self.table_id})"

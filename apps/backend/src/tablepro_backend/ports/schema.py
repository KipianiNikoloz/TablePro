from __future__ import annotations

from typing import Protocol

from tablepro_backend.domain.schema import SchemaIntrospectionRequest, SchemaSnapshot


class SchemaIntrospector(Protocol):
    def introspect(self, request: SchemaIntrospectionRequest) -> SchemaSnapshot:
        """Return schema metadata for a saved database connection."""

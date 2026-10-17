from __future__ import annotations

from collections.abc import Mapping

from psycopg.errors import UniqueViolation

from lakegen.core.error.base import BaseError
from lakegen.core.error.code import ErrorCode
from lakegen.core.persistence.repository.base import Repository


class CompactionRepository(Repository):
    def create(self, data: Mapping[str, object]) -> None:
        payload = dict(data)
        compaction_id = self._required_string(payload, "id")

        try:
            self._database.insert(
                "compactions",
                {
                    "id": compaction_id,
                    "data": self._required_string(payload, "data"),
                    "session_id": self._required_string(payload, "session_id"),
                    "last_compacted_turn_id": self._required_string(payload, "last_compacted_turn_id"),
                },
            )
        except UniqueViolation as error:
            raise BaseError(
                ErrorCode.ALREADY_EXISTS,
                f"Compaction {compaction_id!r} already exists.",
            ) from error

    def get(self, identifier: str) -> dict[str, object]:
        row = self._database.fetch_one(
            """
            SELECT id, session_id, data,
                   last_compacted_turn_id, created_at
            FROM compactions
            WHERE id = %s
            """,
            (identifier,),
        )
        if row is None:
            self._raise_not_found(identifier)
        return row

    def list(
        self,
        identifier: str,
        offset: int = 0,
        limit: int = 20,
    ) -> list[dict[str, object]]:
        return self._database.fetch_all(
            """
            SELECT id, session_id, data,
                   last_compacted_turn_id, created_at
            FROM compactions
            WHERE session_id = %s
            ORDER BY created_at DESC, id DESC
            OFFSET %s
            LIMIT %s
            """,
            (identifier, offset, limit),
        )

    def exists(self, identifier: str) -> bool:
        if not identifier:
            return False
        return (
            self._database.fetch_one(
                "SELECT 1 AS found FROM compactions WHERE id = %s",
                (identifier,),
            )
            is not None
        )

    def delete(self, identifier: str) -> None:
        row = self._database.fetch_one(
            "DELETE FROM compactions WHERE id = %s RETURNING id",
            (identifier,),
        )
        if row is None:
            self._raise_not_found(identifier)

    @staticmethod
    def _raise_not_found(identifier: str) -> None:
        raise BaseError(
            ErrorCode.NOT_FOUND,
            f"Compaction {identifier!r} not found.",
        )


compaction_repository = CompactionRepository()

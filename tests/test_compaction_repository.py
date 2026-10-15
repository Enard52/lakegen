from datetime import datetime
from unittest.mock import MagicMock

import pytest

from lakegen.core.error.base import BaseError
from lakegen.core.error.code import ErrorCode
from lakegen.core.persistence import PostgresPersistence
from lakegen.core.persistence.repository.compaction_repository import (
    CompactionRepository,
)


def test_create_inserts_compaction() -> None:
    database = MagicMock(spec=PostgresPersistence)

    CompactionRepository(database).create(
        {
            "id": "compaction-1",
            "session_id": "session-1",
            "data": "Compacted context:\nsummary",
            "last_compacted_turn_id": "turn-5",
        }
    )

    database.insert.assert_called_once_with(
        "compactions",
        {
            "id": "compaction-1",
            "data": "Compacted context:\nsummary",
            "session_id": "session-1",
            "last_compacted_turn_id": "turn-5",
        },
    )


def test_get_returns_compaction() -> None:
    database = MagicMock(spec=PostgresPersistence)
    row = {
        "id": "compaction-1",
        "session_id": "session-1",
        "data": "Compacted context:\nsummary",
        "last_compacted_turn_id": "turn-5",
        "created_at": datetime.now(),
    }
    database.fetch_one.return_value = row

    assert CompactionRepository(database).get("compaction-1") == row


def test_get_missing_raises_not_found() -> None:
    database = MagicMock(spec=PostgresPersistence)
    database.fetch_one.return_value = None

    with pytest.raises(BaseError) as exc_info:
        CompactionRepository(database).get("missing")

    assert exc_info.value.code == ErrorCode.NOT_FOUND


def test_list_is_session_scoped_and_paginated() -> None:
    database = MagicMock(spec=PostgresPersistence)
    database.fetch_all.return_value = []

    assert CompactionRepository(database).list("session-1", 10, 20) == []
    statement, parameters = database.fetch_all.call_args.args
    assert "WHERE session_id = %s" in statement
    assert parameters == ("session-1", 10, 20)

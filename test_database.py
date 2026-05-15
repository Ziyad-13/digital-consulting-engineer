import unittest
from unittest.mock import patch, MagicMock

import database

class TestDatabase(unittest.TestCase):

    @patch("database.clear_checklist_image")
    @patch("database.upsert_checklist_item")
    @patch("database.get_conn")
    def test_start_rework_existing_item(self, mock_get_conn, mock_upsert, mock_clear):
        # Setup mock db connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value = mock_cursor

        # Mock row return for an existing item with rework_count = 2
        mock_row = {"rework_count": 2}
        mock_cursor.fetchone.return_value = mock_row

        project_id = 1
        phase = 1
        item_key = "test_item"

        # Execute
        database.start_rework(project_id, phase, item_key)

        # Verify db query
        mock_conn.execute.assert_called_once_with(
            "SELECT rework_count FROM checklist_items "
            "WHERE project_id=? AND phase_number=? AND item_key=?",
            (project_id, phase, item_key)
        )

        # Verify upsert call with incremented count (2 + 1 = 3)
        mock_upsert.assert_called_once_with(
            project_id, phase, item_key,
            status=database.STATUS_REWORK,
            rework_count=3,
        )

        # Verify clear image call
        mock_clear.assert_called_once_with(project_id, phase, item_key)

    @patch("database.clear_checklist_image")
    @patch("database.upsert_checklist_item")
    @patch("database.get_conn")
    def test_start_rework_missing_item(self, mock_get_conn, mock_upsert, mock_clear):
        # Setup mock db connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value = mock_cursor

        # Mock row return for a missing item
        mock_cursor.fetchone.return_value = None

        project_id = 2
        phase = 3
        item_key = "missing_item"

        # Execute
        database.start_rework(project_id, phase, item_key)

        # Verify db query
        mock_conn.execute.assert_called_once_with(
            "SELECT rework_count FROM checklist_items "
            "WHERE project_id=? AND phase_number=? AND item_key=?",
            (project_id, phase, item_key)
        )

        # Verify upsert call with initial count (0 + 1 = 1)
        mock_upsert.assert_called_once_with(
            project_id, phase, item_key,
            status=database.STATUS_REWORK,
            rework_count=1,
        )

        # Verify clear image call
        mock_clear.assert_called_once_with(project_id, phase, item_key)

if __name__ == "__main__":
    unittest.main()

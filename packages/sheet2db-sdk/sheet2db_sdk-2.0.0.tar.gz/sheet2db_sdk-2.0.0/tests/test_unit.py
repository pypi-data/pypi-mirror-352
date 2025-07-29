import unittest
from unittest.mock import patch, MagicMock
from packages.sdk.python.sheet2db.main import Sheet2DBClient


class TestSheet2DBClient(unittest.TestCase):
    def setUp(self):
        self.client = Sheet2DBClient("test-api-id")

    @patch("sheet2db_client.requests.post")
    def test_read(self, mock_post):
        mock_post.return_value = MagicMock(status_code=200, json=lambda: [{"name": "Alice"}])
        options = {"limit": 1, "format": "rows"}
        response = self.client.read(options, sheet="Users")

        self.assertEqual(response, [{"name": "Alice"}])
        mock_post.assert_called_with(
            "https://api.sheet2db.com/v1/test-api-id/Users/read",
            json=options,
            headers=self.client.headers
        )

    @patch("sheet2db_client.requests.post")
    def test_insert(self, mock_post):
        mock_post.return_value = MagicMock(status_code=200, json=lambda: {"inserted": 1})
        data = [{"name": "Bob"}]
        response = self.client.insert(data, sheet="Users")

        self.assertEqual(response, {"inserted": 1})
        mock_post.assert_called_once()

    @patch("sheet2db_client.requests.post")
    def test_update(self, mock_post):
        mock_post.return_value = MagicMock(status_code=200, json=lambda: {"updated": 1})
        options = {"type": "row", "row": 1, "data": {"name": "Updated Bob"}}
        response = self.client.update(options, sheet="Users")

        self.assertEqual(response, {"updated": 1})
        mock_post.assert_called_once()

    @patch("sheet2db_client.requests.post")
    def test_delete(self, mock_post):
        mock_post.return_value = MagicMock(status_code=200, json=lambda: {"deleted": 1})
        options = {"type": "row", "row": 2}
        response = self.client.delete(options, sheet="Users")

        self.assertEqual(response, {"deleted": 1})
        mock_post.assert_called_once()

    @patch("sheet2db_client.requests.post")
    def test_add_sheet(self, mock_post):
        mock_post.return_value = MagicMock(status_code=200, json=lambda: {"ok": True})
        response = self.client.add_sheet(name="NewSheet", first_row=["name", "email"])

        self.assertEqual(response, {"ok": True})
        mock_post.assert_called_once()

    @patch("sheet2db_client.requests.post")
    def test_delete_sheet(self, mock_post):
        mock_post.return_value = MagicMock(status_code=200, json=lambda: {"ok": True})
        response = self.client.delete_sheet("OldSheet")

        self.assertEqual(response, {"ok": True})
        mock_post.assert_called_once()


if __name__ == "__main__":
    unittest.main()

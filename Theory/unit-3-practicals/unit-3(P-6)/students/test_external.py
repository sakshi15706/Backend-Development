"""Tests for the external-API integration. NO test touches the real internet:
requests.get is replaced with a mock (Task 5).  Run: python manage.py test
"""
from unittest.mock import Mock, patch

import requests
from django.test import SimpleTestCase
from django.urls import reverse

from .utils import get_external_data


class ExternalDataUtilityTests(SimpleTestCase):
    @patch("students.utils.requests.get")
    def test_success_returns_data(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {"id": 1, "title": "Example"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = get_external_data(1)

        self.assertEqual(result["data"]["id"], 1)
        self.assertIsNone(result["error"])
        # the URL and the 2 second timeout from the slide
        mock_get.assert_called_once_with(
            "https://jsonplaceholder.typicode.com/posts/1",
            timeout=2.0,
        )

    @patch("students.utils.requests.get")
    def test_timeout_returns_safe_error(self, mock_get):
        mock_get.side_effect = requests.Timeout
        result = get_external_data(1)
        self.assertIsNone(result["data"])
        self.assertEqual(result["error"], "External service timed out")

    @patch("students.utils.requests.get")
    def test_connection_error_is_unavailable(self, mock_get):
        mock_get.side_effect = requests.ConnectionError
        result = get_external_data(1)
        self.assertEqual(result["error"], "External service is unavailable")

    @patch("students.utils.requests.get")
    def test_http_error_is_unavailable(self, mock_get):
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("500 Server Error")
        mock_get.return_value = mock_response
        result = get_external_data(1)
        self.assertIsNone(result["data"])
        self.assertEqual(result["error"], "External service is unavailable")

    @patch("students.utils.requests.get")
    def test_invalid_json_is_reported_as_invalid_json(self, mock_get):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = requests.exceptions.JSONDecodeError("bad", "doc", 0)
        mock_get.return_value = mock_response
        result = get_external_data(1)
        self.assertEqual(result["error"], "External service returned invalid JSON")

    @patch("students.utils.requests.get")
    def test_plain_value_error_is_invalid_json(self, mock_get):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = ValueError("no json")
        mock_get.return_value = mock_response
        self.assertEqual(
            get_external_data(1)["error"], "External service returned invalid JSON"
        )


class ExternalDataViewTests(SimpleTestCase):
    def url(self, post_id=1):
        return reverse("external-data", kwargs={"post_id": post_id})

    @patch("students.views.get_external_data")
    def test_view_returns_external_json(self, mock_util):
        mock_util.return_value = {"data": {"id": 1, "title": "Hello"}, "error": None}
        response = self.client.get(self.url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "Hello")
        mock_util.assert_called_once_with(1)

    @patch("students.views.get_external_data")
    def test_view_returns_503_on_failure(self, mock_util):
        mock_util.return_value = {"data": None, "error": "External service timed out"}
        response = self.client.get(self.url())
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"error": "External service timed out"})

    @patch("students.utils.requests.get")
    def test_full_path_timeout_gives_503(self, mock_get):
        # integration style: view -> utility -> (mocked) network
        mock_get.side_effect = requests.Timeout
        response = self.client.get(self.url(5))
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["error"], "External service timed out")

    @patch("students.utils.requests.get")
    def test_full_path_success(self, mock_get):
        mock_get.return_value.raise_for_status.return_value = None
        mock_get.return_value.json.return_value = {"id": 5, "title": "t"}
        response = self.client.get(self.url(5))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], 5)

    def test_non_integer_id_is_404(self):
        self.assertEqual(self.client.get("/api/students/external/abc/").status_code, 404)

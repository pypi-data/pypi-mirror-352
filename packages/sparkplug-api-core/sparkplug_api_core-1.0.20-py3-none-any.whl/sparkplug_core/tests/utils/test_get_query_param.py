from django.test import TestCase

from ...utils.get_query_param import get_query_param


class GetQueryParamTests(TestCase):
    def test_valid_query_param(self):
        url = "https://example.com/path?name=John&age=30"
        param = "name"
        expected_result = "John"
        result = get_query_param(url, param)
        assert result == expected_result

    def test_missing_query_param(self):
        url = "https://example.com/path?name=John&age=30"
        param = "email"
        result = get_query_param(url, param)
        assert result is None

    def test_empty_query_param(self):
        url = "https://example.com/path?name=&age=30"
        param = "name"
        result = get_query_param(url, param)
        assert result is None

    def test_no_query_params(self):
        url = "https://example.com/path"
        param = "name"
        result = get_query_param(url, param)
        assert result is None

    def test_invalid_url(self):
        url = "invalid_url"
        param = "name"
        result = get_query_param(url, param)
        assert result is None

from http import HTTPStatus

from django.test import SimpleTestCase


class TestMetaTxt(SimpleTestCase):
    def test_get_robots_txt(self) -> None:
        response = self.client.get("/robots.txt")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response["content-type"], "text/plain")

    def test_get_security_txt(self) -> None:
        response = self.client.get("/security.txt")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response["content-type"], "text/plain")

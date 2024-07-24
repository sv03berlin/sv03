from clubapp.club.models import User
from django.test import Client, TestCase
from django.urls import get_resolver
from django.urls import URLPattern, URLResolver, reverse, NoReverseMatch


class SuperuserPageRenderTest(TestCase):
    """ Renders all Pages. Skips pages with parameters and without reverse match."""

    skip_prefix = ["/accounts", "/admin"]

    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpassword"
        )
        self.client = Client()
        self.client.login(username="admin", password="adminpassword")

    def test_render_all_pages(self):
        resolver = get_resolver()
        url_names = self._get_url_names(resolver.url_patterns)

        for url_name in url_names:
            try:
                url = reverse(url_name)
                if any(url.startswith(prefix) for prefix in self.skip_prefix):
                    continue
                response = self.client.get(url)
                self.assertIn(response.status_code, [200, 204, 302], msg=f"Failed on URL: {url}")
            except NoReverseMatch:
                pass

    def _get_url_names(self, patterns, prefix=''):
        url_names = []
        for pattern in patterns:
            if isinstance(pattern, URLPattern):
                if pattern.name:
                    url_names.append(pattern.name)
            elif isinstance(pattern, URLResolver):
                url_names.extend(self._get_url_names(pattern.url_patterns))
        return url_names
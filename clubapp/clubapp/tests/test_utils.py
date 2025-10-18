from django import forms
from django.test import SimpleTestCase

from clubapp.clubapp.utils import StrippedIntegerField


class TestStrippedIntegerField(SimpleTestCase):
    def test_strips_leading_and_trailing_spaces(self) -> None:
        field = StrippedIntegerField()
        self.assertEqual(field.to_python("  123  "), 123)
        self.assertEqual(field.to_python("123"), 123)
        self.assertEqual(field.to_python("  123"), 123)
        self.assertEqual(field.to_python("123  "), 123)

    def test_handles_none(self) -> None:
        field = StrippedIntegerField()
        self.assertIsNone(field.to_python(None))

    def test_handles_empty_string(self) -> None:
        field = StrippedIntegerField()
        self.assertIsNone(field.to_python(""))

    def test_handles_invalid_input(self) -> None:
        field = StrippedIntegerField()
        with self.assertRaises(forms.ValidationError):
            field.to_python("abc")

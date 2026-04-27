"""Tests for the approve_clubwork_overview view."""

from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from clubapp.club.models import Ressort, User
from clubapp.clubwork.models import ClubWorkParticipation


class ApproveClubworkOverviewViewTest(TestCase):
    """Test the approve_clubwork_overview view."""

    def setUp(self) -> None:
        """Set up test data."""
        # Create a resort head
        self.head = User.objects.create_user(username="head", email="head@test.com", password="testpass")  # noqa: S106

        # Create a member
        self.member = User.objects.create_user(username="member", email="member@test.com", password="testpass")  # noqa: S106

        # Create resort
        self.ressort = Ressort.objects.create(name="Test Ressort", internal_name="test")
        self.ressort.head.add(self.head)

        # Create past (overdue) clubwork - should appear on page
        past_time = timezone.now() - timedelta(days=1)
        ClubWorkParticipation.objects.create(
            title="Overdue Work",
            user=self.member,
            ressort=self.ressort,
            date_time=past_time,
            duration=60,
            is_approved=False,
            description="Overdue work",
        )

        # Create future clubwork - should NOT appear on page
        future_time = timezone.now() + timedelta(days=7)
        ClubWorkParticipation.objects.create(
            title="Future Work",
            user=self.member,
            ressort=self.ressort,
            date_time=future_time,
            duration=60,
            is_approved=False,
            description="Future work",
        )

    def test_view_shows_overdue_clubwork_only(self) -> None:
        """Test that the view only shows overdue clubwork for resort heads."""
        self.client.login(username="head", password="testpass")  # noqa: S106

        url = reverse("approve_clubwork_overview")
        response = self.client.get(url)

        # Should contain overdue work
        self.assertContains(response, "Overdue Work")
        self.assertContains(response, self.member.get_full_name())

        # Should NOT contain future work
        self.assertNotContains(response, "Future Work")

    def test_view_requires_login(self) -> None:
        """Test that the view requires authentication."""
        url = reverse("approve_clubwork_overview")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_superuser_sees_overdue_clubwork(self) -> None:
        """Test that superusers can see overdue clubwork."""
        # Create superuser
        User.objects.create_superuser(username="superuser", email="super@test.com", password="testpass")  # noqa: S106

        self.client.login(username="superuser", password="testpass")  # noqa: S106

        url = reverse("approve_clubwork_overview")
        response = self.client.get(url)

        # Should contain overdue work
        self.assertContains(response, "Overdue Work")

    def test_no_pending_approvals_shows_message(self) -> None:
        """Test that the view shows a message when there are no pending approvals."""
        self.client.login(username="head", password="testpass")  # noqa: S106

        # Approve all current clubwork
        ClubWorkParticipation.objects.all().update(is_approved=True)

        url = reverse("approve_clubwork_overview")
        response = self.client.get(url)

        # Should show "Alles erledigt" message
        self.assertContains(response, "Alles erledigt")

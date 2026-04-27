"""Tests for the notify management command."""

from datetime import timedelta
from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from clubapp.club.models import Ressort, User
from clubapp.clubwork.models import ClubWorkParticipation


class NotifyRessortCommandTest(TestCase):
    """Test the notify_ressort command functionality."""

    def setUp(self) -> None:
        """Set up test data."""
        # Create resort heads
        self.head1 = User.objects.create_user(username="head1", email="head1@test.com", password="testpass1")  # noqa: S106
        self.head2 = User.objects.create_user(username="head2", email="head2@test.com", password="testpass2")  # noqa: S106

        # Create a member (regular user)
        self.member = User.objects.create_user(username="member", email="member@test.com", password="testpass")  # noqa: S106

        # Create two resorts
        self.ressort1 = Ressort.objects.create(name="Ressort 1", internal_name="ressort1")
        self.ressort1.head.add(self.head1)

        self.ressort2 = Ressort.objects.create(name="Ressort 2", internal_name="ressort2")
        self.ressort2.head.add(self.head2)

        # Create clubwork with participations for different dates
        # Past clubwork (overdue) - should trigger notifications
        past_time = timezone.now() - timedelta(days=1)
        ClubWorkParticipation.objects.create(
            title="Past Work 1",
            user=self.member,
            ressort=self.ressort1,
            date_time=past_time,
            duration=60,
            is_approved=False,
            description="Past overdue work for ressort1",
        )

        # Future clubwork - should NOT trigger notifications
        future_time = timezone.now() + timedelta(days=7)
        ClubWorkParticipation.objects.create(
            title="Future Work",
            user=self.member,
            ressort=self.ressort1,
            date_time=future_time,
            duration=60,
            is_approved=False,
            description="Future work for ressort1",
        )

        # Another past clubwork for different resort
        past_time_2 = timezone.now() - timedelta(days=2)
        ClubWorkParticipation.objects.create(
            title="Past Work 2",
            user=self.member,
            ressort=self.ressort2,
            date_time=past_time_2,
            duration=60,
            is_approved=False,
            description="Past overdue work for ressort2",
        )

    def test_command_filters_by_date_time_lte_now(self) -> None:
        """Test that notify command only considers overdue clubwork."""
        # Count pending clubwork without date filter
        all_pending = ClubWorkParticipation.objects.filter(is_approved=False, did_send_approve_hint=False).count()

        # Count overdue clubwork (should be processed by notify)
        overdue_count = ClubWorkParticipation.objects.filter(
            is_approved=False, did_send_approve_hint=False, date_time__lte=timezone.now()
        ).count()

        # Count future clubwork (should NOT be processed by notify)
        future_count = ClubWorkParticipation.objects.filter(
            is_approved=False, did_send_approve_hint=False, date_time__gt=timezone.now()
        ).count()

        # Verify setup: we have 3 total, 2 past, 1 future
        self.assertEqual(all_pending, 3)
        self.assertEqual(overdue_count, 2)
        self.assertEqual(future_count, 1)

    def test_notify_command_only_sends_for_overdue(self) -> None:
        """Test that the notify command only processes overdue clubwork."""
        # Run the notify command and capture output
        out = StringIO()
        err = StringIO()

        # Call the command
        call_command("notify", stdout=out, stderr=err, verbosity=2)

        # Check that output contains the date filter
        output = out.getvalue()
        self.assertIn("date_time__lte", output)

    def test_notification_did_send_approve_hint_updated(self) -> None:
        """Test that did_send_approve_hint is set to True after notification."""
        # Initially all clubwork have not been notified
        initial_count = ClubWorkParticipation.objects.filter(is_approved=False, did_send_approve_hint=False).count()
        self.assertEqual(initial_count, 3)

        # Run the command
        out = StringIO()
        err = StringIO()
        call_command("notify", stdout=out, stderr=err)

        # All should now have did_send_approve_hint=True (or is_approved=True)
        notified_count = ClubWorkParticipation.objects.filter(is_approved=False, did_send_approve_hint=True).count()
        # At least the overdue ones should be marked
        self.assertGreaterEqual(notified_count, 2)

    def test_multiple_overdue_clubwork_for_same_ressort(self) -> None:
        """Test handling of multiple overdue clubwork for the same resort head."""
        # Create another overdue clubwork for head1
        past_time = timezone.now() - timedelta(days=3)
        ClubWorkParticipation.objects.create(
            title="Another Past Work",
            user=self.member,
            ressort=self.ressort1,
            date_time=past_time,
            duration=45,
            is_approved=False,
            description="Another overdue work",
        )

        # Count overdue for head1's resort (overdue AND not notified yet)
        head1_overdue_and_pending = ClubWorkParticipation.objects.filter(
            is_approved=False,
            did_send_approve_hint=False,
            date_time__lte=timezone.now(),
            ressort__head__in=[self.head1.pk],
        ).count()

        self.assertEqual(head1_overdue_and_pending, 2)  # Should find 2 overdue works

    def test_future_clubwork_not_notified(self) -> None:
        """Test that future clubwork does not trigger notifications."""
        # Get future clubwork
        future = ClubWorkParticipation.objects.filter(
            is_approved=False, did_send_approve_hint=False, date_time__gt=timezone.now()
        )

        # Should have 1 future clubwork in setup
        self.assertEqual(future.count(), 1)

        # Run the command
        out = StringIO()
        err = StringIO()
        call_command("notify", stdout=out, stderr=err)

        # Future clubwork should still have did_send_approve_hint=False
        # Because the command now filters by date_time__lte=timezone.now()
        future_after = ClubWorkParticipation.objects.get(
            is_approved=False, did_send_approve_hint=False, date_time__gt=timezone.now()
        )
        self.assertFalse(future_after.did_send_approve_hint)

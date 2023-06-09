from django.db import models
from django.utils.functional import cached_property

from clubapp.club.models import Resort, User


class ClubWork(models.Model):
    resort = models.ForeignKey(Resort, on_delete=models.PROTECT, related_name="clubwork")

    title = models.CharField(max_length=127)
    description = models.TextField()

    date_time = models.DateTimeField()
    max_duration = models.IntegerField()
    max_participants = models.IntegerField()

    @cached_property
    def num_participants(self) -> int:
        return self.participations.count()

    @cached_property
    def registered_users(self) -> list[User]:
        return [p.user for p in self.participations.all()]


class ClubWorkParticipation(models.Model):
    title = models.CharField(max_length=127)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="clubwork_participations")
    resort = models.ForeignKey(Resort, on_delete=models.PROTECT, related_name="clubwork_participations")
    clubwork = models.ForeignKey(ClubWork, on_delete=models.PROTECT, related_name="participations", null=True)
    date_time = models.DateTimeField()
    duration = models.IntegerField()
    approved_by = models.ForeignKey(User, related_name="approved_work", on_delete=models.SET_NULL, null=True)
    approve_date = models.DateTimeField(auto_now_add=True)
    description = models.TextField()

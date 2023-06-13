from django.db import models

from clubapp.club.models import User


class ReservationGroup(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self) -> str:
        return self.name


class ReservabelThing(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    reservation_group = models.ForeignKey(ReservationGroup, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name


class ReservationGroupMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reservation_group_memberships")
    group = models.ForeignKey(ReservationGroup, on_delete=models.CASCADE, related_name="memberships")

    def __str__(self) -> str:
        return f"{self.user} {self.group}"


class Reservation(models.Model):
    thing = models.ForeignKey(ReservabelThing, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start = models.DateTimeField()
    end = models.DateTimeField()

    def __str__(self) -> str:
        return f"{self.thing.name} {self.start} {self.end} - {self.user}"

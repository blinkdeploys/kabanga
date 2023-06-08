from django.db import models
from django.utils.translation import gettext_lazy as _
from __poll.constants import GeoLevelChoices, StatusChoices

class Event(models.Model):
    title = models.CharField("Election name", max_length=255)
    details = models.TextField(blank=True, null=True)
    office = models.ForeignKey(
                               '__poll.Office',
                               on_delete=models.CASCADE,
                               help_text=_("Election office/level"),
                               blank=True, null=True,
                               related_name='events')
    status = models.CharField(max_length=35, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)
    start = models.DateTimeField("Starts On", help_text=_("Election start date"))
    end = models.DateTimeField("Ends On", help_text=_("Election end date"))
    created_at = models.DateTimeField("Created At", auto_now_add=True)

    class Meta:
        db_table = 'poll_event'

    def __str__(self):
        return "{} for the position of {} {} to {}".format(self.title, self.office, self.start, self.end)
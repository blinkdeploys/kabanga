from django.db import models
from django.utils.translation import gettext_lazy as _
from __poll.constants import StatusChoices
from __poll.utils.utils import upload_candidate_image
from django.db.models import F, Value, Func


class Candidate(models.Model):
    prefix = models.CharField(_("Candidate title"), max_length=255, blank=True, null=True)
    first_name = models.CharField(_("Candidate first name"), max_length=255, default='')
    last_name = models.CharField(_("Candidate last name"), max_length=255, default='')
    other_names = models.CharField(_("Candidate other names"), max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    photo = models.FileField(upload_to=upload_candidate_image,
                            help_text=_("Candidate official campaign headshot"),
                            max_length=500,
                            default=None, null=True, blank=True)
    party = models.ForeignKey(
        '__people.Party',
        on_delete=models.CASCADE,
        blank=True, null=True,
        related_name='candidates'
    )
    position = models.ForeignKey(
        '__poll.Position',
        on_delete=models.CASCADE,
        blank=True, null=True,
        related_name='candidates'
    )
    status = models.CharField(max_length=35, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)
    created_at = models.DateTimeField("Created At", auto_now_add=True)
    
    class Meta:
        db_table = 'people_candidate'

    def __str__(self):
        other_names = ''
        if self.other_names is not None:
            other_names = f' {self.other_names}'
        party_code = ''
        if self.party is not None:
            party_code = f' ({self.party.code})'
        return "{} {} {}{}{}".format(self.prefix, self.first_name, self.last_name, other_names, party_code)

    @property
    def full_name(self):
        return "{} {} {}".format(self.prefix, self.first_name, self.last_name)

    @property
    def total_votes(self) -> int:
        votes = 0
        results = self.results.all()
        for result in results:
            votes = votes + int(result.votes)
        return votes

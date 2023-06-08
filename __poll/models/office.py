from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from __poll.constants import GeoLevelChoices


class Office(models.Model):
    # name of the positon (cannot be changed after inital migration)
    title = models.CharField(_("Office / designation / title"), max_length=255, blank=True)
    level = models.IntegerField(_("Office level"), choices=GeoLevelChoices.choices, default=GeoLevelChoices.UNASSIGNED)

    class Meta:
        db_table = 'poll_office'

    @property
    def level_title(self):
        if self.level == GeoLevelChoices.NATIONAL:
            return "Presidential Level"
        elif self.level == GeoLevelChoices.CONSTITUENCY:
            return "Parliamentary Level"
        return ''

    def save(self, *args, **kwargs):
        levels = sorted([o.level for o in Office.objects.all()])

        if len(levels) == 2:
            if (levels[0] == GeoLevelChoices.CONSTITUENCY
                and levels[1] == GeoLevelChoices.NATIONAL):
                raise ValidationError('All levels have been filled by exising instances of this model')

        if self.level not in [GeoLevelChoices.CONSTITUENCY, GeoLevelChoices.NATIONAL]:
            raise ValidationError('Invalid level value, must select National (4) or Constiuency (2)')

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from __poll.constants import GeoLevelChoices, OfficeChoices
from __geo.models import Nation, Region, Constituency, Station
from __poll.models.office import Office
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from __poll.utils.utils import get_zone_ct


class Position(models.Model):
    zone_options = models.Q(app_label='__geo', model='Nation') | \
            models.Q(app_label='__geo', model='Constituency') | \
            models.Q(app_label='__geo', model='Region')

    # name of the positon (cannot be changed after inital migration)
    title = models.CharField("Position name", max_length=255)
    details = models.TextField(blank=True, null=True)
    # actual zone the position contested over
    # optional foreign key for the geo zone being contested
    zone_ct = models.ForeignKey(ContentType,
                                         limit_choices_to=zone_options,
                                         on_delete=models.SET_NULL,
                                         related_name='zones',
                                         null=True, blank=True)
    zone_id = models.PositiveIntegerField(null=True, db_index=True)
    zone = GenericForeignKey('zone_ct', 'zone_id')

    class Meta:
        db_table = 'poll_position'
        # unique_together = ('office', 'zone',)

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        # get the actual positon title
        # e.g. Minister for the Volta Region
        zone_title = ''
        if self.zone is not None:
            zone_title = f' {self.zone.title}'
        return "{}{}".format(self.title, zone_title)

    @property
    def zone_type(self):
        nation_ct = get_zone_ct(Nation)
        constituency_ct = get_zone_ct(Constituency)
        if self.zone_ct == nation_ct and nation_ct is not None:
            return 'Nation'
        if self.zone_ct == constituency_ct and constituency_ct is not None:
            return 'Constituency'
        return 'N/A'

    '''
    def clean(self):
        zone = None
        if self.office_id == OfficeChoices.PRESIDENT:
            try:
                presidential_office = Office.objects.filter(level=GeoLevelChoices.NATIONAL).first()
                if presidential_office.exits():
                    try:
                        zone = Nation.objects.filter(pk=self.zone.id).first()
                    except Nation.DoesNotExist:
                        raise ValidationError("Selected position's zone (nation) does not exist. Please select a valid zone (nation)")
            except Office.DoesNotExist:
                raise ValidationError("Selected position's office does not exist. Please select a valid office")
        else:
            try:
                parliamentary_office = Office.objects.filter(level=GeoLevelChoices.CONSTITUENCY).first()
                if parliamentary_office.exits():
                    try:
                        zone = Constituency.objects.filter(pk=self.zone.id).first()
                    except Constituency.DoesNotExist:
                        raise ValidationError("Selected position's zone (constituency) does not exist. Please select a valid zone (constituency)")
            except Office.DoesNotExist:
                raise ValidationError("Selected position's office does not exist. Please select a valid office")
        if zone is None:
            raise ValidationError("Selected position's zone is not valid.")
    '''

from django.db import models
from django.utils.translation import gettext_lazy as _
from __poll.constants import StatusChoices
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericRelation


class Nation(models.Model):
    code = models.CharField("Nation code", max_length=25)
    title = models.CharField("Nation name", max_length=255)
    positions = GenericRelation('__poll.Position', content_type_field='zone_ct', object_id_field='zone_id')

    class Meta:
        db_table = 'geo_nation'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not Nation.objects.filter(pk=self.pk).exists() and Nation.objects.exists():
            raise ValidationError('There can be only one instance of this model')
        return super(Nation, self).save(*args, **kwargs)

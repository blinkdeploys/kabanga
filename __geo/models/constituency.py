from django.db import models
from django.utils.translation import gettext_lazy as _
from __poll.constants import StatusChoices
from django.contrib.contenttypes.fields import GenericRelation


class Constituency(models.Model):
	title = models.CharField("Constituency name", max_length=255)
	details = models.TextField(blank=True, null=True, help_text=_("Details"))
	region = models.ForeignKey("Region",
								on_delete=models.CASCADE,
								help_text=_("Region"),
								related_name='constituencies')
	status = models.CharField(max_length=35, choices=StatusChoices.choices, default=StatusChoices.ACTIVE, help_text=_("Constituency status"))
	positions = GenericRelation('__poll.Position', content_type_field='zone_ct', object_id_field='zone_id')
	created_at = models.DateTimeField("Created At", auto_now_add=True)

	class Meta:
		db_table = 'geo_constituency'

	def __str__(self):
		return "{}".format(self.title)

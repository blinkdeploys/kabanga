from django.db import models
from django.utils.translation import gettext_lazy as _
from __poll.constants import StatusChoices
from itertools import chain


class Region(models.Model):
	title = models.CharField("Region name", max_length=255)
	details = models.TextField(blank=True, null=True)
	nation = models.ForeignKey(
		"Nation", on_delete=models.CASCADE,
		help_text=_("Nation"),
        related_name='regions')
	status = models.CharField(max_length=35, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)
	created_at = models.DateTimeField("Created At", auto_now_add=True)

	class Meta:
		db_table = 'geo_region'

	def __str__(self):
		return self.title

	@property
	def stations(self):
		constituencies = self.constituencies.all()
		stations = []
		for constituency in constituencies:
			if constituency is not None:
				if constituency.stations is not None:
					if constituency.stations.count() > 0:
						stations = list(chain(stations, constituency.stations.all()))
		return stations
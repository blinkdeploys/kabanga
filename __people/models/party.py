from django.db import models
from django.utils.translation import gettext_lazy as _
from __poll.constants import StatusChoices
from __poll.utils.utils import get_zone_ct
from __poll.models import Position
from __geo.models import Constituency, Nation

class Party(models.Model):
	code = models.CharField("Party accronym", max_length=10)
	title = models.CharField("Party name", max_length=255)
	details = models.TextField(blank=True, null=True)
	agent = models.ForeignKey(
							  '__people.Agent', on_delete=models.CASCADE,
							  help_text=_("Agent in command"),
							  null=True, blank=True,
							  related_name='parties')
	status = models.CharField(max_length=35, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)
	created_at = models.DateTimeField("Created At", auto_now_add=True)
	
	class Meta:
		db_table = 'poll_party'

	def __str__(self):
		return f"{self.title} ({self.code})"

	@property
	def result_votes(self):
		votes = 0
		sheets = self.supernational_collation_sheets.all()
		for sheet in sheets:
			votes = votes + int(sheet.total_votes)
		return votes

	@property
	def total_presidential_votes(self):
		votes = 0
		sheets = self.supernational_collation_sheets \
					.filter(
						zone_ct=get_zone_ct(Nation)
					).all()
		for sheet in sheets:
			votes = votes + int(sheet.total_votes)
		return votes

	@property
	def total_parliamentary_votes(self):
		votes = 0
		sheets = self.supernational_collation_sheets \
					.filter(
						zone_ct=get_zone_ct(Constituency)
					).all()
		for sheet in sheets:
			votes = votes + int(sheet.total_votes)
		return votes

	def total_candidates(self):
		return self.candidates.all().count()

from django.db import models
from django.utils.translation import gettext_lazy as _
from __poll.constants import StatusChoices
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from __geo.models import Nation, Region, Constituency, Station
from __poll.utils.utils import get_zone_ct


class Agent(models.Model):
	zone_options = models.Q(app_label='__geo', model='Nation') | \
				   models.Q(app_label='__geo', model='Region') | \
				   models.Q(app_label='__geo', model='Constituency') | \
				   models.Q(app_label='__geo', model='Station')

	first_name = models.CharField("First name", max_length=255)
	last_name = models.CharField("Last name", max_length=255)
	email = models.EmailField()
	phone = models.CharField(max_length=50)
	address =  models.TextField(blank=True, null=True)
	zone_ct = models.ForeignKey(ContentType,
								limit_choices_to=zone_options,
								on_delete=models.SET_NULL,
								related_name='agent_ct',
								null=True, blank=True)
	zone_id = models.PositiveIntegerField(null=True, db_index=True)
	zone = GenericForeignKey('zone_ct', 'zone_id')
	user = models.OneToOneField("account.User",
								on_delete=models.SET_NULL,
								# primary_key=True,
								related_name="agent",
								default=None, null=True, blank=True)
	description = models.TextField(blank=True, null=True)
	status = models.CharField(max_length=35, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)
	created_at = models.DateTimeField("Created At", auto_now_add=True)

	class Meta:
		db_table = 'people_agent'

	def __str__(self):
		return f'{self.first_name} {self.last_name}'

	@property
	def full_name(self):
		return f'{self.first_name} {self.last_name}'

	@property
	def zone_title(self):
		nation_ct = get_zone_ct(Nation)
		region_ct = get_zone_ct(Region)
		constituency_ct = get_zone_ct(Constituency)
		station_ct = get_zone_ct(Station)
		if self.zone_ct == nation_ct and nation_ct is not None:
			return Nation.objects.get(pk=self.zone_id).title
		if self.zone_ct == region_ct and region_ct is not None:
			return Region.objects.get(pk=self.zone_id).title
		if self.zone_ct == constituency_ct and constituency_ct is not None:
			return Constituency.objects.get(pk=self.zone_id).title
		if self.zone_ct == station_ct and station_ct is not None:
			return Station.objects.get(pk=self.zone_id).title
		return ''
		
	@property
	def zone_type(self):
		if self.zone_ct is not None:
			if self.zone_ct == get_zone_ct(Nation):
				return 'Nation'
			if self.zone_ct == get_zone_ct(Region):
				return 'Region'
			if self.zone_ct == get_zone_ct(Constituency):
				return 'Constituency'
			if self.zone_ct == get_zone_ct(Station):
				return 'Polling Station'
		return 'N/A'

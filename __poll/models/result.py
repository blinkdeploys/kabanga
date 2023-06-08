from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver
from __poll.constants import GeoLevelChoices, StatusChoices
from __poll.utils.utils import upload_result_sheet, intify, get_zone_ct
from __poll.utils.collations import (
    save_supernational_collation_sheet,
    save_national_collation_sheet,
    save_regional_collation_sheet,
    save_constituency_collation_sheet,
    save_station_collation_sheet
)


ZONE_OPTIONS = models.Q(app_label='__geo', model='Nation') | \
        models.Q(app_label='__geo', model='Constituency')
        # models.Q(app_label='__geo', model='Region') | \
        # models.Q(app_label='__geo', model='Station') | \



class ParliamentarySummarySheet(models.Model):
    position = models.OneToOneField("__poll.Position",
                                on_delete=models.CASCADE,
                                help_text=_("Position"),
                                related_name='parliamentary_summary_sheet',
                                default=True, null=True, blank=True)
    candidate = models.OneToOneField("__people.Candidate",
                                  on_delete=models.CASCADE,
                                  help_text=_("Candidate"),
                                  default=None, null=True, blank=True,
                                  related_name='parliamentary_summary_sheet')
    constituency = models.OneToOneField("__geo.Constituency",
                                on_delete=models.CASCADE,
                                help_text=_("Constituency"),
                                default=None, null=True, blank=True,
                                related_name='parliamentary_summary_sheet')
    votes = models.BigIntegerField(_("Collation total number of valid votes"), help_text=_("Total number of votes"), null=True, blank=True)
    total_votes = models.BigIntegerField(_("EC Summary Collation totals"), help_text=_("EC Collation number"), null=True, blank=True)
    status = models.CharField(max_length=35, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)
    created_at = models.DateTimeField("Created At", auto_now_add=True)
    # TODO: To capture Variance with EC Summary

    class Meta:
        db_table = 'poll_parliamentary_summary_sheet'

    def clean(self):
        self.votes = intify(self.votes)
        self.total_votes = intify(self.total_votes)


class SupernationalCollationSheet(models.Model):
    party = models.ForeignKey("__people.Party",
                                on_delete=models.CASCADE,
                                help_text=_("Party"),
                                related_name='supernational_collation_sheets',
                                default=None, null=True, blank=True)
    nation = models.ForeignKey("__geo.Nation",
                                on_delete=models.CASCADE,
                                help_text=_("Nation"),
                                related_name='supernational_collation_sheets',
                                default=None, null=True, blank=True)
    total_votes = models.BigIntegerField(_("Collation total number of valid votes"), help_text=_("Total number of votes"), null=True, blank=True)
    total_invalid_votes = models.BigIntegerField(_("Collation total number of invalid votes"), help_text=_("Total number of invalid votes"), null=True, blank=True)
    total_votes_ec = models.BigIntegerField(_("EC Summary Collation totals"), help_text=_("EC Collation number"), null=True, blank=True)
    created_at = models.DateTimeField("Created At", auto_now_add=True)
    status = models.CharField(max_length=35, choices=StatusChoices.choices, default=StatusChoices.ACTIVE, blank=True, null=True)
    zone_ct = models.ForeignKey(ContentType,
                                limit_choices_to=ZONE_OPTIONS,
                                on_delete=models.SET_NULL,
                                related_name='supernational_collation_zones',
                                default=None, null=True, blank=True)

    class Meta:
        db_table = 'poll_supernational_collation_sheet'

    def clean(self):
        self.total_votes = intify(self.total_votes)


class NationalCollationSheet(models.Model):
    party = models.ForeignKey("__people.Party",
                                on_delete=models.CASCADE,
                                help_text=_("Party"),
                                default=None, null=True, blank=True,
                                related_name='national_collation_sheets')
    region = models.ForeignKey("__geo.Region",
                                on_delete=models.CASCADE,
                                help_text=_("Region"),
                                default=None, null=True, blank=True,
                                related_name='national_collation_sheets')
    total_votes = models.BigIntegerField(_("Collation total number of valid votes"), help_text=_("Total number of votes"), null=True, blank=True)
    total_invalid_votes = models.BigIntegerField(_("Collation total number of invalid votes"), help_text=_("Total number of invalid votes"), null=True, blank=True)
    total_votes_ec = models.BigIntegerField(_("EC Summary Collation totals"), help_text=_("EC Collation number"), null=True, blank=True)
    nation_agent = models.ForeignKey("__people.Agent",
                             on_delete=models.CASCADE,
                             help_text=_("National agent that recorded results"),
                             related_name='national_collation_sheets',
                             default=None, null=True, blank=True)
    national_approval_at = models.DateTimeField("Date of Regional Approved At", default=None, null=True, blank=True)
    created_at = models.DateTimeField("Created At", auto_now_add=True)
    status = models.CharField(max_length=35, choices=StatusChoices.choices, default=StatusChoices.ACTIVE, blank=True, null=True)
    zone_ct = models.ForeignKey(ContentType,
                                limit_choices_to=ZONE_OPTIONS,
                                on_delete=models.SET_NULL,
                                related_name='national_collation_zones',
                                default=None, null=True, blank=True)

    class Meta:
        db_table = 'poll_national_collation_sheet'

    def clean(self):
        self.total_votes = intify(self.total_votes)


class RegionalCollationSheet(models.Model):
    party = models.ForeignKey("__people.Party",
                                  on_delete=models.CASCADE,
                                  help_text=_("Party"),
                                  default=None, null=True, blank=True,
                                  related_name='regional_collation_sheets')
    constituency = models.ForeignKey("__geo.Constituency",
                                on_delete=models.CASCADE,
                                help_text=_("Constituency"),
                                default=None, null=True, blank=True,
                                related_name='regional_collation_sheets')
    total_votes = models.BigIntegerField(_("Collation total number of valid votes"), help_text=_("Total number of votes"), null=True, blank=True)
    total_invalid_votes = models.BigIntegerField(_("Collation total number of invalid votes"), help_text=_("Total number of invalid votes"), null=True, blank=True)
    total_votes_ec = models.BigIntegerField(_("EC Summary Collation totals"), help_text=_("EC Collation number"), null=True, blank=True)
    region_agent = models.ForeignKey("__people.Agent",
                             on_delete=models.CASCADE,
                             help_text=_("Regional agent that recorded results"),
                             related_name='regional_collation_sheets',
                             default=None, null=True, blank=True)
    regional_approval_at = models.DateTimeField("Date of Regional Approved At", default=None, null=True, blank=True)
    created_at = models.DateTimeField("Created At", auto_now_add=True)
    status = models.CharField(max_length=35, choices=StatusChoices.choices, default=StatusChoices.ACTIVE, blank=True, null=True)
    zone_ct = models.ForeignKey(ContentType,
                                limit_choices_to=ZONE_OPTIONS,
                                on_delete=models.SET_NULL,
                                related_name='regional_collation_zones',
                                default=None, null=True, blank=True)

    class Meta:
        db_table = 'poll_regional_collation_sheet'

    def clean(self):
        self.total_votes = intify(self.total_votes)


class ConstituencyCollationSheet(models.Model):
    party = models.ForeignKey("__people.Party",
                                  on_delete=models.CASCADE,
                                  help_text=_("Party"),
                                  default=None, null=True, blank=True,
                                  related_name='constituency_collation_sheets')
    station = models.ForeignKey("__geo.Station",
                                on_delete=models.CASCADE,
                                help_text=_("Station"),
                                default=None, null=True, blank=True,
                                related_name='constituency_collation_sheets')
    total_votes = models.BigIntegerField(_("Collation total number of valid votes"), help_text=_("Total number of votes"), null=True, blank=True)
    total_invalid_votes = models.BigIntegerField(_("Collation total number of invalid votes"), help_text=_("Total number of invalid votes"), null=True, blank=True)
    total_votes_ec = models.BigIntegerField(_("EC Summary Collation totals"), help_text=_("EC Collation number"), null=True, blank=True)
    constituency_agent = models.ForeignKey("__people.Agent",
                             on_delete=models.CASCADE,
                             help_text=_("Constituency agent that recorded results"),
                             related_name='constituency_collation_sheets',
                             default=None, null=True, blank=True)
    constituency_approved_at = models.DateTimeField("Constituency Approved At", default=None, null=True, blank=True)
    created_at = models.DateTimeField("Created At", auto_now_add=True)
    status = models.CharField(max_length=35, choices=StatusChoices.choices, default=StatusChoices.ACTIVE, blank=True, null=True)
    zone_ct = models.ForeignKey(ContentType,
                                limit_choices_to=ZONE_OPTIONS,
                                on_delete=models.SET_NULL,
                                related_name='constituency_collation_zones',
                                default=None, null=True, blank=True)

    class Meta:
        db_table = 'poll_constituency_collation_sheet'

    def clean(self):
        self.total_votes = intify(self.total_votes)


class StationCollationSheet(models.Model):
    candidate = models.ForeignKey("__people.Candidate",
                                  on_delete=models.CASCADE,
                                  help_text=_("Candidate"),
                                  default=None, null=True, blank=True,
                                  related_name='station_collation_sheets')
    station = models.ForeignKey("__geo.Station",
                                on_delete=models.CASCADE,
                                help_text=_("Polling Station"),
                                default=None, null=True, blank=True,
                                related_name='station_collation_sheets')
    total_votes = models.BigIntegerField(_("Collation total number of valid votes"), help_text=_("Total number of votes"), null=True, blank=True)
    total_invalid_votes = models.BigIntegerField(_("Collation total number of invalid votes"), help_text=_("Total number of invalid votes"), null=True, blank=True)
    total_votes_ec = models.BigIntegerField(_("EC Summary Collation totals"), help_text=_("EC Collation number"), null=True, blank=True)
    station_agent = models.ForeignKey("__people.Agent",
                             on_delete=models.CASCADE,
                             help_text=_("Constituency agent that recorded results"),
                             related_name='station_collation_sheets',
                             default=None, null=True, blank=True)
    station_approval_at = models.DateTimeField("Date of Stational Approved At", default=None, null=True, blank=True)
    created_at = models.DateTimeField("Created At", auto_now_add=True)
    status = models.CharField(max_length=35, choices=StatusChoices.choices, default=StatusChoices.ACTIVE, blank=True, null=True)
    zone_ct = models.ForeignKey(ContentType,
                                limit_choices_to=ZONE_OPTIONS,
                                on_delete=models.SET_NULL,
                                related_name='station_collation_zones',
                                default=None, null=True, blank=True)

    class Meta:
        db_table = 'poll_station_collation_sheet'

    def clean(self):
        self.total_votes = intify(self.total_votes)


class ResultSheet(models.Model):
    station = models.ForeignKey("__geo.Station",
                                on_delete=models.CASCADE,
                                help_text=_("Polling Station"),
                                related_name='result_sheets',
                                default=True, null=True, blank=True)
    position = models.ForeignKey("__poll.Position",
                                on_delete=models.CASCADE,
                                help_text=_("Position"),
                                related_name='result_sheets',
                                default=True, null=True, blank=True)
    total_votes = models.BigIntegerField(_("Total number of votes"), help_text=_("Total number of votes"), null=True, blank=True)
    total_valid_votes = models.BigIntegerField(_("Total number of valid votes"), help_text=_("Total number of valid votes"), null=True, blank=True)
    total_invalid_votes = models.BigIntegerField(_("Total number of invalid votes"), help_text=_("Total number of invalid votes"), null=True, blank=True)
    total_votes_ec = models.BigIntegerField(_("EC Summary Collation totals"), help_text=_("EC Collation number"), null=True, blank=True)
    result_sheet = models.FileField(upload_to=upload_result_sheet,
                                    help_text=_("Statement of poll and declaration of results"),
                                    max_length=500,
                                    default=None, null=True, blank=True)
    station_agent = models.ForeignKey("__people.Agent",
                             on_delete=models.CASCADE,
                             help_text=_("Constituency agent that recorded results"),
                             related_name='result_sheets',
                             default=None, null=True, blank=True)
    station_approval_at = models.DateTimeField("Date of Stational Approved At", default=None, null=True, blank=True)
    created_at = models.DateTimeField("Created At", auto_now_add=True)
    status = models.CharField(max_length=35, choices=StatusChoices.choices, default=StatusChoices.ACTIVE, blank=True, null=True)

    class Meta:
        db_table = 'poll_result_sheet'

    def clean(self):
        self.total_votes = intify(self.total_votes)


class Result(models.Model):
    '''
    Collates the total number of votes for each party for each office in each constituency. List of fields as follows:
        * office: office being vied for
        * station: the staton the votes were collected from
        * party: the party that votes were collected for
        * votes: total number of votes per constituent
        * file: path to the verification form
        * is_published: has to be vetted and publshed by regional agent before it can be used in results
    '''
    # polling station where the results was collected
    station = models.ForeignKey(
                                "__geo.Station",
                                on_delete=models.CASCADE,
                                help_text=_("Polling Station"),
                                related_name='results')
    # candidate voted for
    candidate = models.ForeignKey(
                                 "__people.Candidate",
                                 on_delete=models.CASCADE,
                                 help_text=_("Candidate"),
                                 default=None, null=True, blank=True,
                                 related_name='results')
    # total number of votes at station
    votes = models.BigIntegerField(_("Total number of votes"), help_text=_("Total number of votes"))
    # verification sheet
    result_sheet = models.ForeignKey(
                                    "ResultSheet",
                                    on_delete=models.CASCADE,
                                    help_text=_("Result verification sheet"),
                                    related_name='results',
                                    default=None,  null=True, blank=True)
    # party agent responsible
    station_agent = models.ForeignKey(
                             "__people.Agent",
                             on_delete=models.CASCADE,
                             help_text=_("Station agent that recorded the result"),
                             related_name='results',
                             default=None, null=True, blank=True)
    status = models.CharField(max_length=35, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)

    class Meta:
        db_table = 'poll_result'

    def candidate_details(self):
        if self.candidate is not None:
            if self.candidate.party is not None:
                return f'{self.candidate.full_name} ({self.candidate.party.code})'
        return 'NA'

    def clean(self):
        self.votes = intify(self.votes)


class ResultSheetApproval(models.Model):
    '''EC Collation model used in verifying data collected in result sheets'''

    result_sheet = models.ForeignKey("ResultSheet",
                                     on_delete=models.CASCADE,
                                     help_text=_("Result Sheet being approved"),
                                     related_name='approvals')
    total_valid_votes = models.BigIntegerField(_("Result Sheet Total"), help_text=_("Result Sheet Total"), null=True, blank=True)
    ec_summary_total = models.BigIntegerField(_("EC Summary Collation Total"), help_text=_("EC Collation total from the EC Summary Sheet submitted"), null=True, blank=True)
    variance = models.BigIntegerField(_("Variance"), help_text=_("Variance between EC Summary total and Result Sheet total votes"), null=True, blank=True)
    approving_agent = models.ForeignKey("__people.Agent",
                                        on_delete=models.CASCADE,
                                        help_text=_("Agent that approved the result sheet"),
                                        related_name='approved_result_sheets',
                                        default=None, null=True, blank=True)
    approved_at = models.DateTimeField("Approved At", auto_now_add=True)
    status = models.CharField(max_length=35, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)
    created_at = models.DateTimeField("Created At", auto_now_add=True)

    class Meta:
        db_table = 'poll_result_sheet_approval'

    def __str__(self):
        return "{} {} {}".format(self.result_sheet.position, self.result_sheet.station, self.total_valid_votes)

    def save(self, *args, **kwargs):
        if self.ec_summary_total is None:
            self.ec_summary_total = 0
        if self.result_sheet:
            self.total_valid_votes = self.result_sheet.total_valid_votes
            self.variance = int(self.total_valid_votes) - int(self.ec_summary_total)
        super().save(*args, **kwargs)


class ResultApproval(models.Model):
    result = models.ForeignKey("Result", on_delete=models.CASCADE, help_text=_("Position"))
    status = models.CharField(max_length=35, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)
    approved_at = models.DateTimeField("Approved At", auto_now_add=True)
    created_at = models.DateTimeField("Created At", auto_now_add=True)
    approving_agent = models.ForeignKey(
                                        "__people.Agent",
                                        on_delete=models.CASCADE,
                                        help_text=_("Agent that approved the result"),
                                        related_name='result_approvals')

    class Meta:
        db_table = 'poll_result_approval'

    def __str__(self):
        return "{} {} {}".format(self.result.position, self.result.station, self.result.votes)


# process collations sheets on Result post save
@receiver(post_save, sender=Result)
def collate_station_sheet(sender, instance=None, created=False, **kwargs):
    station_sheet = save_station_collation_sheet(instance)

@receiver(post_save, sender=StationCollationSheet)
def collate_station_sheet(sender, instance=None, created=False, **kwargs):
    constituency_sheet = save_constituency_collation_sheet(instance)

@receiver(post_save, sender=ConstituencyCollationSheet)
def collate_station_sheet(sender, instance=None, created=False, **kwargs):
    regional_sheet = save_regional_collation_sheet(instance)

@receiver(post_save, sender=RegionalCollationSheet)
def collate_station_sheet(sender, instance=None, created=False, **kwargs):
    national_sheet = save_national_collation_sheet(instance)

@receiver(post_save, sender=NationalCollationSheet)
def collate_station_sheet(sender, instance=None, created=False, **kwargs):
    supernational_sheet = save_supernational_collation_sheet(instance)

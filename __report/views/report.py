from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
from people.models import Party, Candidate
from people.serializers import PartySerializer
from geo.models import Nation, Region, Constituency, Station
from geo.serializers import RegionSerializer, StationSerializer
from poll.forms import OfficeForm
from poll.constants import ROWS_PER_PAGE
from itertools import chain
from django.apps import apps
from django.db.models import (
    Q, Prefetch, Sum, Count, Max,
    F, Value, Func, Subquery, OuterRef, IntegerField, CharField, Case, When,
)
from django.db.models.functions import Concat
from poll.utils.utils import snakeify, get_zone_ct
from django.contrib.auth.decorators import login_required
from poll.constants import StatusChoices, GeoLevelChoices, NameTitleChoices, TerminalColors
from django.db import connection
from poll.models import (
    Event, Office, Position, ResultSheet, Result, ResultApproval,
    SupernationalCollationSheet, NationalCollationSheet, RegionalCollationSheet,
    ConstituencyCollationSheet, StationCollationSheet,
    ParliamentarySummarySheet
)
from django.http import JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.db.models.functions import Replace


# HELPER FUNCTIONS: EXPORT TO UTILS

def safe_get(dictionary, key, default=0, force='int'):
    if dictionary is not None and type(dictionary).__name__ == 'dict':
        return dictionary.get(key, default) or default
    return default

def get_election_level(level):
    levels = [GeoLevelChoices.CONSTITUENCY, 'parliament', 'parliamentary']
    if level in levels:
        return (GeoLevelChoices.CONSTITUENCY, Constituency, 'Parliamentary', '_parliament')
    return (GeoLevelChoices.NATION, Nation, 'Presidential', '')

@login_required
def index_view(request):
    context = {
        'return': {
            'title': 'home',
            'path': '/',
        },
        'navigation': [
            [
                {
                    'title': 'Presidential Reports',
                    'details': 'View collated presidential report sheets from all levels',
                    'url': '/reports/presidential/nation/',
                    'theme': 'text-dark bg-light',
                },
                {
                    'title': 'Parliamentary Report',
                    'details': 'View collated parliamentary report sheets from all levels',
                    'url': '/reports/parliamentary/nation/',
                    'theme': 'text-dark bg-light',
                },
            ],
            [
                {
                    'title': 'Collection Progress',
                    'details': 'Track the progress of data collection from all areas and levels',
                    'url': '#',
                    'theme': 'text-dark bg-light',
                },
                {
                    'title': 'Approval Progress',
                    'details': 'Track the progress of data approval by higher level party agents',
                    'url': '#',
                    'theme': 'text-dark bg-light',
                },
            ],
            [
                {
                    'title': 'Collate Results',
                    'details': 'Run a collation job to update presidential and parliamentary reports.',
                    'url': '#',
                    'theme': 'text-dark bg-light',
                },
            ],
        ],
    }
    return render(request, "home.html", context)

def get_blank_total_sheets():
    return dict(
        valid=dict(
            party_code='',
            party_title='Total Valid Votes',
            lead=0,
            seats=0,
            total_votes=0,
            total_votes_ec=0,
            total_ec_variance=0,
            total_valid_votes=0,
            total_invalid_votes=0,
        ),
        invalid=dict(
            party_code='',
            party_title='Total Invalid Votes',
            lead=0,
            seats=0,
            total_votes=0,
            total_votes_ec=0,
            total_ec_variance=0,
            total_valid_votes=0,
            total_invalid_votes=0,
        ),
        total=dict(
            party_code='',
            party_title='Total Votes',
            lead=0,
            seats=0,
            total_votes=0,
            total_votes_ec=0,
            total_ec_variance=0,
            total_valid_votes=0,
            total_invalid_votes=0,
        )
    )

# HELPER FUNCTIONS: EXPORT TO UTILS

@login_required
def presidential_win_report(request, pk=None):
    title = 'Presidential Wins'
    template = 'report/win.html'
    zone = 'nation'
    if zone == 'region':
        zone_name = 'constituency'
        collation_sheet = ConstituencyCollationSheet
    elif zone == 'constituency':
        zone_name = 'station'
        collation_sheet = StationCollationSheet
    else:
        zone_name = 'region'
        collation_sheet = NationalCollationSheet
    zone_model = apps.get_model('__geo', zone_name)
    zone_ct = get_zone_ct(Nation)
    reports = None
    zones = zone_model.objects \
                    .values('id') \
                    .all()

    reports = []
    for zone in zones:
        candidates = Candidate.objects \
                            .filter(party__pk=OuterRef('party__pk')) \
                            .annotate(
                                candidate_full_name=Concat(F('prefix'), Value(' '), F('first_name'), Value(' '), F('last_name'))
                            ) \
                            .values('candidate_full_name') \
                            .all()[:1]
        # TECH NOTE: Concat the names of all candidate (from above) into the candidates field below
        results = collation_sheet.objects \
                                        .values(
                                                'party__pk',
                                                'party__code',
                                                'party__title',
                                                'region__pk',
                                                'region__title',
                                                'total_votes',
                                                'total_invalid_votes',
                                                'total_votes_ec',
                                                # 'won',
                                                # 'max_collated_votes',
                                            ) \
                                        .annotate(
                                            position_title=Value('President'),
                                            candidates=Subquery(candidates, output_field=CharField()),
                                            total_variance=F('total_votes_ec') - F('total_votes')
                                        ) \
                                        .filter(**{
                                                f'{zone_name}__pk': zone['id'],
                                                'zone_ct': zone_ct,
                                            }) \
                                        .all().order_by('party__code')
        
        # find records with the max votes
        max_results = results.annotate(
                                    max_collated_votes=Max(F('total_votes')),
                                    ) \
                             .values_list('max_collated_votes')
        max_results = [item[0] for item in max_results]
        max_result = 0
        if max_results is not None:
            if len(max_results) > 0:
                max_result = max(max_results)

        # filter in only the parties with the max votes
        reports.extend([v for v in results if v['total_votes'] == max_result and max_result > 0])

    percentage = 0
    if zones.count() > 0:
        percentage = round(100 * len(reports) / zones.count(), 0)

    context = dict(
        title=title,
        reports=reports,
        zones=zones,
        percentage=percentage,
    )
    return render(request, template, context)


@login_required
def parliamentary_seat_report(request, pk=None):
    title = 'Parliamentary Seats'
    template = 'report/seat.html'
    zone_ct = get_zone_ct(Constituency)
    reports = []
    party = None
    seats = Constituency.objects \
                                 .values('id') \
                                 .all()
    reports = ParliamentarySummarySheet.objects \
                                    .values(
                                        'pk',
                                        'candidate__party__pk',
                                        'candidate__party__code',
                                        'candidate__party__title',
                                        'candidate__position__pk',
                                        'candidate__position__title',
                                        'candidate__prefix',
                                        'candidate__first_name',
                                        'candidate__last_name',
                                        'candidate__other_names',
                                        'constituency__pk',
                                        'constituency__title',
                                        'votes',
                                        'total_votes'
                                    ) \
                                    .filter(constituency__in=seats) \
                                    .filter(position__in=Position.objects
                                                                .values('id')
                                                                .filter(zone_ct=zone_ct) \
                                                                .all())
    if pk is not None:
        try:
            reports = reports.filter(candidate__in=Candidate.objects \
                                                    .values('id')
                                                    .filter(party_id=pk)
                                                    .all())
        except ParliamentarySummarySheet.DoesNotExist as e:
            print(e)
            reports = None
    reports = reports.all().order_by('candidate__party__code')

    seat_percentage = 0
    if seats.count() > 0:
        seat_percentage = round(100 * reports.count() / seats.count(), 0)
    
    try:
        party = Party.objects.values('pk', 'code', 'title').get(pk=pk)
    except Party.DoesNotExist as e:
        print(e)
    context = dict(
        title=title,
        party=party,
        reports=reports,
        seats=seats,
        seat_percentage=seat_percentage,
    )
    return render(request, template, context)


@login_required
def nation_presidential_report(request, npk=None):
    level = GeoLevelChoices.NATIONAL
    zone_ct_model = Nation
    zone_ct = get_zone_ct(zone_ct_model)
    report_title = f'Presidential Collation Results (National)'
    template = f'report/report.html'
    zone_type='nation'
    sub_zone_type='region'
    sub_zone_type_plural = 'regions'
    sub_zone_type_1='constituency'
    sub_zone_type_2='station'
    sub_zone_link=f'/reports/presidential/region/'
    super_zone=None
    super_zone_link='#'
    sheet_model = NationalCollationSheet
    column_model = Region
    page_model = Nation
    zone = page_model.objects.first()
    key_field = 'title'
    rid=1
    office_type='presidential'

    # find all parties and stats for each (y-axis)

    totals_row = dict(
                    valid={},
                    invalid={},
                    total={},
                )
    reports = []
    max_votes = 0
    max_votes_party = None
    p = 0
    total_sheets = get_blank_total_sheets()

    xfields = ['id', 'code', 'title',
                'total_votes',
                'total_valid_votes',
                'total_votes_ec',
                'total_ec_variance',
                'total_invalid_votes',
                'sub_zone_total_votes_ec',
                'sub_zone_total_ec_variance',
              ]

    # report columns (regions for national page)
    columns = column_model.objects.values('id', 'title') \
                    .annotate(key=Replace(
                                    Func(F(key_field), function='LOWER'),
                                    Value(' '),
                                    Value('_')
                    )).filter(nation=zone) \
                    .order_by('title').all()

    sub_xannotates = dict(
                # sum all total_votes (col) in the collation table
                sub_total_valid_votes=Sum(
                                        F('national_collation_sheets__total_votes'),
                                        filter=Q(national_collation_sheets__zone_ct=zone_ct)
                                    ),
                # sum all total_votes_ec (col) in the collation table
                sub_total_votes_ec=Sum(
                                    F('national_collation_sheets__total_votes_ec'),
                                    filter=Q(national_collation_sheets__zone_ct=zone_ct)
                                ),
                sub_total_ec_variance=F('sub_total_valid_votes') - F('sub_total_votes_ec'),
    )
    parties_sub_counts = Party.objects \
                    .filter(pk=OuterRef('pk')) \
                    .annotate(**sub_xannotates) \
                    .order_by('code')
    # run sub queries to include additional columns (national collation sheet)
    parties_sub_counts_votes = parties_sub_counts \
                    .values(*['sub_total_valid_votes'])
    parties_sub_counts_votes_ec = parties_sub_counts \
                    .values(*['sub_total_votes_ec'])[:1]
    parties_sub_counts_variance = parties_sub_counts \
                    .values(*['sub_total_ec_variance'])[:1]

    xannotates = dict(
                # sum all total_votes (col) in the collation table
                total_valid_votes=Sum(
                                        F('supernational_collation_sheets__total_votes'),
                                        filter=Q(supernational_collation_sheets__zone_ct=zone_ct)
                                    ),
                # sum all total_votes_ec (col) in the collation table
                total_votes_ec=Sum(
                                    F('supernational_collation_sheets__total_votes_ec'),
                                    filter=Q(supernational_collation_sheets__zone_ct=zone_ct)
                                ),
                # sum all total_invalid_votes (col) in the collation table
                total_invalid_votes=Sum(
                                            F('supernational_collation_sheets__total_invalid_votes'),
                                            filter=Q(supernational_collation_sheets__zone_ct=zone_ct)
                                        ),
                total_votes=F('total_valid_votes') + F('total_invalid_votes'),
                total_ec_variance=F('total_votes') - F('total_votes_ec'),
                sub_zone_total_votes_ec=Subquery(parties_sub_counts_votes_ec, output_field=IntegerField()),
                sub_zone_total_ec_variance=Subquery(parties_sub_counts_variance, output_field=IntegerField()),
            )

    parties = Party.objects \
                    .annotate(**xannotates) \
                    .values(*xfields) \
                    .order_by('code').all()


    # loop through the parties (report rows)
    for party in parties:
        yid = party['id']
        # define an "empty" report row
        total_votes = safe_get(party, 'total_votes', default=0, force='int')
        total_votes_ec = safe_get(party, 'total_votes_ec', default=0, force='int')
        total_valid_votes = safe_get(party, 'total_valid_votes', default=0, force='int')
        total_ec_variance = safe_get(party, 'total_ec_variance', default=0, force='int')
        total_invalid_votes = safe_get(party, 'total_invalid_votes', default=0, force='int')
        sub_zone_total_votes_ec = safe_get(party, 'sub_zone_total_votes_ec', default=0, force='int')
        sub_zone_total_ec_variance = safe_get(party, 'sub_zone_total_ec_variance', default=0, force='int')
        report_sheet = dict(
            party_id=party['id'],
            party_code=party['code'],
            party_title=party['title'],
            lead=0,
            seats=0,
            total_votes=total_votes,
            total_votes_ec=total_votes_ec,
            total_valid_votes=total_valid_votes,
            total_ec_variance=total_ec_variance,
            total_invalid_votes=total_invalid_votes,
            sub_zone_total_votes_ec=sub_zone_total_votes_ec,
            sub_zone_total_ec_variance=sub_zone_total_ec_variance,
        )
        # find the leading party
        if max_votes <= report_sheet['total_votes']:
            max_votes = report_sheet['total_votes']
            max_votes_party = p
        # loop through the report columns
        for column in columns:
            xid = column['id']
            xcode = column['key']
            # fetch the collation sheet for each column
            party_sheet = sheet_model.objects \
                                    .annotate(total_ec_variance=F('total_votes') - F('total_votes_ec')) \
                                    .values('total_votes', 'total_votes_ec', 'total_ec_variance') \
                                    .filter(
                                        region_id=xid,
                                        party_id=yid,
                                        zone_ct=zone_ct,
                                    ).first()
            party_votes = safe_get(party_sheet, 'total_votes', default=0, force='int')
            party_votes_ec = safe_get(party_sheet, 'total_votes_ec', default=0, force='int')
            party_ec_variance = safe_get(party_sheet, 'total_ec_variance', default=0, force='int')
            party_valid_votes = party_votes
            # set the total votes and ec
            report_sheet[xcode] = party_votes
            count = total_sheets['invalid'].get(xcode, 0)
            count += 0
            total_sheets['invalid'][xcode] = count
            count = total_sheets['valid'].get(xcode, 0)
            count += party_valid_votes
            total_sheets['valid'][xcode] = count
            count = total_sheets['total'].get(xcode, 0)
            count += party_valid_votes
            total_sheets['total'][xcode] = count
            total_sheets['total']['total_votes_ec'] += party_votes_ec
            total_sheets['total']['total_valid_votes'] += party_valid_votes
            total_sheets['total']['total_votes'] += party_votes
            total_sheets['valid']['total_votes_ec'] += party_votes_ec
            total_sheets['valid']['total_votes'] += party_votes
            total_sheets['valid']['total_valid_votes'] += party_valid_votes
            total_sheets['valid']['total_ec_variance'] += party_ec_variance
            total_sheets['invalid']['total_votes_ec'] += 0
            total_sheets['invalid']['total_votes'] += 0
            if total_sheets['total'][xcode] > 0:
                column['has_votes'] = 1

        reports.append(report_sheet)
        p += 1
    # set the leading party
    if max_votes_party is not None:
        reports[max_votes_party]['lead'] = 1
    
    totals_row = [
                    total_sheets['valid'],
                    total_sheets['invalid'],
                    total_sheets['total']
                ]
    total_votes = totals_row[0]['total_votes']
    if total_votes > 0:
        for report in reports:
            report['percentage'] = round(100 * report['total_votes'] / total_votes, 20)
    context = dict(
        title=report_title,
        level=level,
        columns=columns,
        reports=reports,
        zone=zone,
        rid=rid,
        office_type=office_type,
        zone_type=zone_type,
        totals_row=totals_row,
        sub_zone_type=sub_zone_type,
        sub_zone_type_plural=sub_zone_type_plural,
        sub_zone_type_1=sub_zone_type_1,
        sub_zone_type_2=sub_zone_type_2,
        super_zone=super_zone,
        super_zone_link=super_zone_link,
        sub_zone_link=sub_zone_link,
    )   
    return render(request, template, context)

@login_required
def region_presidential_report(request, rpk=None):
    level = GeoLevelChoices.NATIONAL
    zone_ct_model = Nation
    zone_ct = get_zone_ct(zone_ct_model)
    report_title = f'Presidential Collation Results (Regional)'
    template = f'report/report.html'
    zone_type = 'region'
    sub_zone_type = 'constituency'
    sub_zone_type_plural = 'constituencies'
    sub_zone_link=f'/reports/presidential/constituency/'
    super_zone_link='/reports/presidential/nation/'
    sheet_model = RegionalCollationSheet
    column_model = Constituency
    page_model = Region
    zone = page_model.objects.filter(pk=rpk).first()
    super_zone = zone.nation if zone is not None else None
    key_field = 'title'
    rid=rpk
    office_type='presidential'

    # find all parties and stats for each (y-axis)
    xfields = ['id', 'code', 'title',
                'total_votes',
                'total_valid_votes',
                'total_votes_ec',
                'total_ec_variance',
                'total_invalid_votes',
                'sub_zone_total_votes_ec',
                'sub_zone_total_ec_variance',
                ]
    sub_xannotates = dict(
                # sum all total_votes (col) in the collation table
                sub_total_valid_votes=Sum(
                                        F('regional_collation_sheets__total_votes'),
                                        filter=Q(regional_collation_sheets__zone_ct=zone_ct)
                                                & Q(regional_collation_sheets__constituency__region_id=rpk)
                                    ),
                # sum all total_votes_ec (col) in the collation table
                sub_total_votes_ec=Sum(
                                    F('regional_collation_sheets__total_votes_ec'),
                                    filter=Q(regional_collation_sheets__zone_ct=zone_ct)
                                            & Q(regional_collation_sheets__constituency__region_id=rpk)

                                ),
                sub_total_ec_variance=F('sub_total_valid_votes') - F('sub_total_votes_ec'),
    )
    parties_sub_counts = Party.objects \
                    .filter(pk=OuterRef('pk')) \
                    .annotate(**sub_xannotates) \
                    .order_by('code')
    # run sub queries to include additional columns (national collation sheet)
    parties_sub_counts_votes = parties_sub_counts.values(*['sub_total_valid_votes'][:1])
    parties_sub_counts_votes_ec = parties_sub_counts.values(*['sub_total_votes_ec'])[:1]
    parties_sub_counts_variance = parties_sub_counts.values(*['sub_total_ec_variance'])[:1]
    xannotates = dict(
                        # sum all total_votes (col) in the collation table
                        total_valid_votes=Sum(
                                            F('national_collation_sheets__total_votes'),
                                            filter=Q(national_collation_sheets__zone_ct=zone_ct)
                                                    & Q(national_collation_sheets__region_id=rpk)
                                        ),
                        # sum all total_votes_ec (col) in the collation table
                        total_votes_ec=Sum(
                                            F('national_collation_sheets__total_votes_ec'),
                                            filter=Q(national_collation_sheets__zone_ct=zone_ct)
                                                    & Q(national_collation_sheets__region_id=rpk)
                                        ),
                        # sum all total_invalid_votes (col) in the collation table
                        total_invalid_votes=Sum(
                                                F('national_collation_sheets__total_invalid_votes'),
                                                filter=Q(national_collation_sheets__zone_ct=zone_ct)
                                                        & Q(national_collation_sheets__region_id=rpk)
                                            ),
                        total_votes=F('total_valid_votes') + F('total_invalid_votes'),
                        total_ec_variance=F('total_votes') - F('total_votes_ec'),
                        sub_zone_total_votes_ec=Subquery(parties_sub_counts_votes_ec, output_field=IntegerField()),
                        sub_zone_total_ec_variance=Subquery(parties_sub_counts_variance, output_field=IntegerField()),
                     )

    parties = Party.objects \
                    .annotate(**xannotates) \
                    .values(*xfields) \
                    .order_by('code').all()

    totals_row = dict(
                    valid={},
                    invalid={},
                    total={},
                )
    reports = []
    max_votes = 0
    max_votes_party = None
    p = 0
    total_sheets = get_blank_total_sheets()

    columns = column_model.objects.values('id', 'title') \
                    .annotate(key=Replace(
                                    Func(F(key_field), function='LOWER'),
                                    Value(' '),
                                    Value('_')
                                )) \
                    .filter(region=zone) \
                    .order_by('title').all()
    for party in parties:
        yid = party['id']
        total_votes = safe_get(party, 'total_votes', default=0)
        total_valid_votes = safe_get(party, 'total_valid_votes', default=0)
        total_invalid_votes = safe_get(party, 'total_invalid_votes', default=0)
        total_votes_ec = safe_get(party, 'total_votes_ec', default=0)
        total_ec_variance = safe_get(party, 'total_ec_variance', default=0)
        sub_zone_total_votes_ec = safe_get(party, 'sub_zone_total_votes_ec', default=0)
        sub_zone_total_ec_variance = safe_get(party, 'sub_zone_total_ec_variance', default=0)
        report_sheet = dict(
            party_id=party['id'],
            party_code=party['code'],
            party_title=party['title'],
            lead=0,
            total_votes=total_votes,
            total_votes_ec=total_votes_ec,
            total_valid_votes=total_valid_votes,
            total_ec_variance=total_ec_variance,
            total_invalid_votes=total_invalid_votes,
            sub_zone_total_votes_ec=sub_zone_total_votes_ec,
            sub_zone_total_ec_variance=sub_zone_total_ec_variance,
        )
        # find the leading party
        if total_valid_votes > max_votes:
            max_votes = total_valid_votes
            max_votes_party = p
        for column in columns:
            xid = column['id']
            xcode = column['key']
            party_sheet = sheet_model.objects \
                                    .annotate(total_ec_variance=F('total_votes') - F('total_votes_ec')) \
                                    .values('total_votes', 'total_votes_ec', 'total_ec_variance') \
                                    .filter(
                                        constituency_id=xid,
                                        party_id=yid,
                                        zone_ct=zone_ct,
                                    ).first()
            party_votes = safe_get(party_sheet, 'total_votes', default=0, force='int')
            party_votes_ec = safe_get(party_sheet, 'total_votes_ec', default=0, force='int')
            party_ec_variance = safe_get(party_sheet, 'total_ec_variance', default=0, force='int')
            party_valid_votes = party_votes
            # set the total votes and ec
            report_sheet[xcode] = party_votes
            count = total_sheets['invalid'].get(xcode, 0)
            count += 0
            total_sheets['invalid'][xcode] = count
            count = total_sheets['valid'].get(xcode, 0)
            count += party_votes
            total_sheets['valid'][xcode] = count
            count = total_sheets['total'].get(xcode, 0)
            count += party_votes
            total_sheets['total'][xcode] = count
            total_sheets['total']['total_votes_ec'] += party_votes_ec
            total_sheets['total']['total_votes'] += party_votes
            total_sheets['total']['total_valid_votes'] += party_valid_votes
            total_sheets['valid']['total_votes_ec'] += party_votes_ec
            total_sheets['valid']['total_votes'] += party_votes
            total_sheets['valid']['total_valid_votes'] += party_valid_votes
            total_sheets['valid']['total_ec_variance'] += party_ec_variance
            total_sheets['invalid']['total_votes_ec'] += 0
            total_sheets['invalid']['total_votes'] += 0
            if total_sheets['total'][xcode] > 0:
                column['has_votes'] = 1

        reports.append(report_sheet)
        p += 1
    # set the leading party
    if max_votes_party is not None:
        reports[max_votes_party]['lead'] = 1
    totals_row = [
                    total_sheets['valid'],
                    total_sheets['invalid'],
                    total_sheets['total']
                ]
    total_votes = totals_row[0]['total_votes']
    if total_votes > 0:
        for report in reports:
            report['percentage'] = round(100 * report['total_votes'] / total_votes, 20)
    context = dict(
        title=report_title,
        level=level,
        columns=columns,
        reports=reports,
        zone=zone,
        rid=rid,
        office_type=office_type,
        totals_row=totals_row,
        zone_type=zone_type,
        sub_zone_type=sub_zone_type,
        sub_zone_type_plural=sub_zone_type_plural,
        super_zone=super_zone,
        super_zone_link=super_zone_link,
        sub_zone_link=sub_zone_link,
    )   
    return render(request, template, context)

@login_required
def constituency_presidential_report(request, cpk=None):
    level = GeoLevelChoices.NATIONAL
    zone_ct_model = Nation
    zone_ct = get_zone_ct(zone_ct_model)
    report_title = f'Presidential Collation Results (Constituency)'
    template = f'report/report.html'
    zone_type = 'constituency'
    sub_zone_type = 'station'
    sub_zone_type_plural = 'stations'
    sub_zone_link=f'/reports/presidential/{sub_zone_type}/'
    super_zone_link='/reports/presidential/region/'
    sheet_model = ConstituencyCollationSheet
    column_model = Station
    page_model = Constituency
    zone = page_model.objects.filter(pk=cpk).first()
    super_zone = zone.region if zone is not None else None
    key_field = 'code'
    rid=cpk
    office_type='presidential'

    # find all parties and stats for each (y-axis)
    xfields = ['id', 'code', 'title',
                'total_votes',
                'total_valid_votes',
                'total_votes_ec',
                'total_ec_variance',
                'total_invalid_votes',
                'sub_zone_total_votes_ec',
                'sub_zone_total_ec_variance',
                ]
    sub_xannotates = dict(
                # sum all total_votes (col) in the collation table
                sub_total_valid_votes=Sum(
                                        F('constituency_collation_sheets__total_votes'),
                                        filter=Q(constituency_collation_sheets__zone_ct=zone_ct)
                                                & Q(constituency_collation_sheets__station__constituency_id=cpk)
                                    ),
                # sum all total_votes_ec (col) in the collation table
                sub_total_votes_ec=Sum(
                                    F('constituency_collation_sheets__total_votes_ec'),
                                    filter=Q(constituency_collation_sheets__zone_ct=zone_ct)
                                            & Q(constituency_collation_sheets__station__constituency_id=cpk)
                                ),
                sub_total_ec_variance=F('sub_total_valid_votes') - F('sub_total_votes_ec'),
    )
    parties_sub_counts = Party.objects \
                    .filter(pk=OuterRef('pk')) \
                    .annotate(**sub_xannotates) \
                    .order_by('code')
    # run sub queries to include additional columns (national collation sheet)
    parties_sub_counts_votes = parties_sub_counts.values(*['sub_total_valid_votes'][:1])
    parties_sub_counts_votes_ec = parties_sub_counts.values(*['sub_total_votes_ec'])[:1]
    parties_sub_counts_variance = parties_sub_counts.values(*['sub_total_ec_variance'])[:1]
    xannotates = dict(
                        # sum all total_votes (col) in the collation table
                        total_valid_votes=Sum(
                                            F('regional_collation_sheets__total_votes'),
                                            filter=Q(regional_collation_sheets__zone_ct=zone_ct)
                                                    & Q(regional_collation_sheets__constituency_id=cpk)
                                        ),
                        # sum all total_votes_ec (col) in the collation table
                        total_votes_ec=Sum(
                                            F('regional_collation_sheets__total_votes_ec'),
                                            filter=Q(regional_collation_sheets__zone_ct=zone_ct)
                                                    & Q(regional_collation_sheets__constituency_id=cpk)
                                        ),
                        # sum all total_invalid_votes (col) in the collation table
                        total_invalid_votes=Sum(
                                                F('regional_collation_sheets__total_invalid_votes'),
                                                filter=Q(regional_collation_sheets__zone_ct=zone_ct)
                                                        & Q(regional_collation_sheets__constituency_id=cpk)
                                            ),
                        total_votes=F('total_valid_votes') + F('total_invalid_votes'),
                        total_ec_variance=F('total_votes') - F('total_votes_ec'),
                        sub_zone_total_votes_ec=Subquery(parties_sub_counts_votes_ec, output_field=IntegerField()),
                        sub_zone_total_ec_variance=Subquery(parties_sub_counts_variance, output_field=IntegerField()),
                    )
    parties = Party.objects \
                    .annotate(**xannotates) \
                    .values(*xfields) \
                    .order_by('code').all()

    totals_row = dict(
                    valid={},
                    invalid={},
                    total={},
                )
    reports = []
    max_votes = 0
    max_votes_party = None
    p = 0

    total_sheets = get_blank_total_sheets()

    columns = column_model.objects.values('id', 'code', 'title') \
                    .filter(constituency=zone) \
                    .annotate(key=Replace(
                                    Func(F(key_field), function='LOWER'),
                                    Value(' '),
                                    Value('_')
                                )) \
                    .order_by('title').all()
    for party in parties:
        yid = party['id']
        total_votes = safe_get(party, 'total_votes', default=0)
        total_valid_votes = safe_get(party, 'total_valid_votes', default=0)
        total_invalid_votes = safe_get(party, 'total_invalid_votes', default=0)
        total_votes_ec = safe_get(party, 'total_votes_ec', default=0)
        total_ec_variance = safe_get(party, 'total_ec_variance', default=0)
        sub_zone_total_votes_ec = safe_get(party, 'sub_zone_total_votes_ec', default=0)
        sub_zone_total_ec_variance = safe_get(party, 'sub_zone_total_ec_variance', default=0)
        report_sheet = dict(
            party_id=party['id'],
            party_code=party['code'],
            party_title=party['title'],
            lead=0,
            total_votes=total_votes,
            total_votes_ec=total_votes_ec,
            total_valid_votes=total_valid_votes,
            total_ec_variance=total_ec_variance,
            total_invalid_votes=total_invalid_votes,
            sub_zone_total_votes_ec=sub_zone_total_votes_ec,
            sub_zone_total_ec_variance=sub_zone_total_ec_variance,
        )
        # find the leading party
        if total_valid_votes > max_votes:
            max_votes = total_valid_votes
            max_votes_party = p
        for column in columns:
            xid = column['id']
            xcode = column['key']
            party_sheet = sheet_model.objects \
                                    .annotate(total_ec_variance=F('total_votes') - F('total_votes_ec')) \
                                    .values('total_votes', 'total_votes_ec', 'total_ec_variance') \
                                    .filter(
                                        station_id=xid,
                                        party_id=yid,
                                        zone_ct=zone_ct,
                                    ).first()
            party_votes = safe_get(party_sheet, 'total_votes', default=0, force='int')
            party_votes_ec = safe_get(party_sheet, 'total_votes_ec', default=0, force='int')
            party_ec_variance = safe_get(party_sheet, 'total_ec_variance', default=0, force='int')
            party_valid_votes = party_votes
            # set the total votes and ec
            report_sheet[xcode] = party_votes
            count = total_sheets['invalid'].get(xcode, 0)
            count += 0
            total_sheets['invalid'][xcode] = count
            count = total_sheets['valid'].get(xcode, 0)
            count += party_votes
            total_sheets['valid'][xcode] = count
            count = total_sheets['total'].get(xcode, 0)
            count += party_votes
            total_sheets['total'][xcode] = count
            total_sheets['total']['total_votes_ec'] += party_votes_ec
            total_sheets['total']['total_votes'] += party_votes
            total_sheets['total']['total_valid_votes'] += party_valid_votes
            total_sheets['valid']['total_votes_ec'] += party_votes_ec
            total_sheets['valid']['total_votes'] += party_votes
            total_sheets['valid']['total_valid_votes'] += party_valid_votes
            total_sheets['valid']['total_ec_variance'] += party_ec_variance
            total_sheets['invalid']['total_votes_ec'] += 0
            total_sheets['invalid']['total_votes'] += 0
            if total_sheets['total'][xcode] > 0:
                column['has_votes'] = 1

        reports.append(report_sheet)
        p += 1
    # set the leading party
    if max_votes_party is not None:
        reports[max_votes_party]['lead'] = 1
    totals_row = [
                    total_sheets['valid'],
                    total_sheets['invalid'],
                    total_sheets['total']
                ]
    total_votes = totals_row[0]['total_votes']
    if total_votes > 0:
        for report in reports:
            report['percentage'] = round(100 * report['total_votes'] / total_votes, 20)
    context = dict(
        title=report_title,
        level=level,
        columns=columns,
        reports=reports,
        zone=zone,
        rid=rid,
        office_type=office_type,
        totals_row=totals_row,
        zone_type=zone_type,
        sub_zone_type=sub_zone_type,
        sub_zone_type_plural=sub_zone_type_plural,
        super_zone=super_zone,
        super_zone_link=super_zone_link,
        sub_zone_link=sub_zone_link,
    )   
    return render(request, template, context)

@login_required
def station_presidential_report(request, spk=None):
    level = GeoLevelChoices.NATIONAL
    zone_ct_model = Nation
    zone_ct = get_zone_ct(zone_ct_model)
    report_title = f'Presidential Collation Results (Station)'
    template = f'report/report.html'
    zone_type = 'station'
    sub_zone_type = None
    sub_zone_type_plural = None
    sub_zone_link='#'
    super_zone_link='/reports/presidential/constituency/'
    sheet_model = StationCollationSheet
    column_model = None
    page_model = Station
    zone = page_model.objects.filter(pk=spk).first()
    super_zone = zone.constituency if zone is not None else None
    rid=spk
    office_type='presidential'

    # find all parties and stats for each (y-axis)
    xfields = ['id', 'code', 'title',
                'total_votes',
                'total_valid_votes',
                'total_votes_ec',
                'total_ec_variance',
                'total_invalid_votes',
            ]
    xannotates = dict(
                        # sum all total_votes (col) in the collation table
                        total_valid_votes=Sum(
                                            F('constituency_collation_sheets__total_votes'),
                                            filter=Q(constituency_collation_sheets__zone_ct=zone_ct)
                                                    & Q(constituency_collation_sheets__station_id=spk)
                                        ),
                        # sum all total_votes_ec (col) in the collation table
                        total_votes_ec=Sum(
                                            F('constituency_collation_sheets__total_votes'),
                                            filter=Q(constituency_collation_sheets__zone_ct=zone_ct)
                                                    & Q(constituency_collation_sheets__station_id=spk)
                                        ),
                        # sum all total_invalid_votes (col) in the collation table
                        total_invalid_votes=Sum(
                                            F('constituency_collation_sheets__total_votes'),
                                            filter=Q(constituency_collation_sheets__zone_ct=zone_ct)
                                                    & Q(constituency_collation_sheets__station_id=spk)
                                            ),
                        total_votes=F('total_valid_votes') + F('total_invalid_votes'),
                        total_ec_variance=F('total_votes') - F('total_votes_ec'),
                    )
    parties = Party.objects \
                    .annotate(**xannotates) \
                    .values(*xfields) \
                    .order_by('code').all()

    totals_row = dict(
                    valid={},
                    invalid={},
                    total={},
                )
    reports = []
    max_votes = 0
    max_votes_party = None
    p = 0

    total_sheets = get_blank_total_sheets()

    columns = []
    for party in parties:
        yid = party['id']
        total_votes = safe_get(party, 'total_votes', default=0)
        total_valid_votes = safe_get(party, 'total_valid_votes', default=0)
        total_invalid_votes = safe_get(party, 'total_invalid_votes', default=0)
        total_votes_ec = safe_get(party, 'total_votes_ec', default=0)
        total_ec_variance = safe_get(party, 'total_ec_variance', default=0)
        sub_zone_total_votes_ec = safe_get(party, 'sub_zone_total_votes_ec', default=0)
        sub_zone_total_ec_variance = safe_get(party, 'sub_zone_total_ec_variance', default=0)
        report_sheet = dict(
            party_id=party['id'],
            party_code=party['code'],
            party_title=party['title'],
            lead=0,
            seats=0,
            total_votes=total_votes,
            total_valid_votes=total_valid_votes,
            total_votes_ec=total_votes_ec,
            total_ec_variance=total_ec_variance,
            total_invalid_votes=total_invalid_votes,
            sub_zone_total_votes_ec=sub_zone_total_votes_ec,
            sub_zone_total_ec_variance=sub_zone_total_ec_variance,
        )
        # find the leading party
        if report_sheet['total_valid_votes'] > max_votes:
            max_votes = report_sheet['total_valid_votes']
            max_votes_party = p
        # collate totals
        total_sheets['total']['total_votes_ec'] += total_votes_ec
        total_sheets['total']['total_votes'] += total_votes
        total_sheets['valid']['total_votes_ec'] += total_votes_ec
        total_sheets['valid']['total_votes'] += total_votes
        total_sheets['valid']['total_valid_votes'] += total_valid_votes
        total_sheets['valid']['total_ec_variance'] += total_ec_variance
        total_sheets['invalid']['total_votes_ec'] += 0
        total_sheets['invalid']['total_votes'] += 0
        # append the row the sheets
        reports.append(report_sheet)
        p += 1
    # set the leading party
    if max_votes_party is not None:
        reports[max_votes_party]['lead'] = 1
    totals_row = [
                    total_sheets['valid'],
                    total_sheets['invalid'],
                    total_sheets['total']
                ]
    total_votes = totals_row[0]['total_votes']
    if total_votes > 0:
        for report in reports:
            report['percentage'] = round(100 * report['total_votes'] / total_votes, 20)
    context = dict(
        title=report_title,
        level=level,
        columns=columns,
        reports=reports,
        zone=zone,
        rid=rid,
        office_type=office_type,
        totals_row=totals_row,
        zone_type=zone_type,
        sub_zone_type=sub_zone_type,
        sub_zone_type_plural=sub_zone_type_plural,
        super_zone=super_zone,
        super_zone_link=super_zone_link,
        sub_zone_link=sub_zone_link,
    )   
    return render(request, template, context)


@login_required
def nation_parliamentary_report(request, npk=None):
    level = GeoLevelChoices.CONSTITUENCY
    zone_ct_model = Constituency
    zone_ct = get_zone_ct(zone_ct_model)
    report_title = f'Parliamentary Collation Results (National)'
    template = f'report/report.html'
    zone_type='nation'
    sub_zone_type='region'
    sub_zone_type_plural = 'regions'
    sub_zone_link=f'/reports/parliamentary/{sub_zone_type}/'
    super_zone=None
    super_zone_link='#'
    sheet_model = NationalCollationSheet
    column_model = Region
    page_model = Nation
    zone = page_model.objects.first()
    key_field = 'title'
    rid=npk or 1
    office_type='parliamentary'

    # find all parties and stats for each (y-axis)
    xfields = ['id', 'code', 'title',
                'total_votes',
                'total_valid_votes',
                'total_votes_ec',
                'total_ec_variance',
                'total_invalid_votes',]
    xannotates = dict(
                        # sum all total_votes (col) in the collation table
                        total_valid_votes=Sum(
                                            F('supernational_collation_sheets__total_votes'),
                                            filter=Q(supernational_collation_sheets__zone_ct=zone_ct)
                                        ),
                        # sum all total_votes_ec (col) in the collation table
                        total_votes_ec=Sum(
                                            F('supernational_collation_sheets__total_votes_ec'),
                                            filter=Q(supernational_collation_sheets__zone_ct=zone_ct)
                                        ),
                        # sum all total_invalid_votes (col) in the collation table
                        total_invalid_votes=Sum(
                                                F('supernational_collation_sheets__total_invalid_votes'),
                                                filter=Q(supernational_collation_sheets__zone_ct=zone_ct)
                                            ),
                        total_votes=F('total_valid_votes') + F('total_invalid_votes'),
                        total_ec_variance=F('total_votes') - F('total_votes_ec'),
                    )
    parties = Party.objects \
                    .annotate(**xannotates) \
                    .values(*xfields) \
                    .order_by('code').all()

    totals_row = dict(
                    valid={},
                    invalid={},
                    total={},
                )
    reports = []
    max_votes = 0
    max_votes_party = None
    p = 0
    total_sheets = get_blank_total_sheets()
    columns = []
    seats = []

    columns = column_model.objects.values('id', 'title') \
                    .annotate(key=Replace(
                                    Func(F(key_field), function='LOWER'),
                                    Value(' '),
                                    Value('_')
                                )) \
                    .filter(nation=zone) \
                    .order_by('title').all()
    for party in parties:
        yid = party['id']
        seats = ParliamentarySummarySheet.objects \
                                        .filter(
                                            constituency__in=Constituency.objects \
                                                                    .values('id')
                                                                    .all(),
                                            candidate__in=Candidate.objects \
                                                                    .values('id')
                                                                    .filter(party_id=yid) \
                                                                    .all(),
                                            position__in=Position.objects \
                                                                    .values('id')
                                                                    .filter(zone_ct=zone_ct) \
                                                                    .all(),
                                        ).all().count()
        # find the leading party
        if max_votes <= seats:
            max_votes = seats
            max_votes_party = p
            total_sheets['valid']['seats'] += seats

        total_votes = safe_get(party, 'total_votes', default=0)
        total_valid_votes = safe_get(party, 'total_valid_votes', default=0)
        total_invalid_votes = safe_get(party, 'total_invalid_votes', default=0)
        total_votes_ec = safe_get(party, 'total_votes_ec', default=0)
        total_ec_variance = safe_get(party, 'total_ec_variance', default=0)
        sub_zone_total_votes_ec = safe_get(party, 'sub_zone_total_votes_ec', default=0)
        sub_zone_total_ec_variance = safe_get(party, 'sub_zone_total_ec_variance', default=0)
        report_sheet = dict(
            party_id=party['id'],
            party_code=party['code'],
            party_title=party['title'],
            lead=0,
            seats=seats,
            total_votes=total_votes,
            total_votes_ec=total_votes_ec,
            total_valid_votes=total_valid_votes,
            total_ec_variance=total_ec_variance,
            total_invalid_votes=total_invalid_votes,
            sub_zone_total_votes_ec=sub_zone_total_votes_ec,
            sub_zone_total_ec_variance=sub_zone_total_ec_variance,
        )
        for column in columns:
            xid = column['id']
            xcode = column['key']
            party_sheet = sheet_model.objects \
                                    .annotate(total_ec_variance=F('total_votes') - F('total_votes_ec')) \
                                    .values('total_votes', 'total_votes_ec', 'total_ec_variance') \
                                    .filter(
                                        region_id=xid,
                                        party_id=yid,
                                        zone_ct=zone_ct,
                                    ).first()
            party_votes = safe_get(party_sheet, 'total_votes', default=0, force='int')
            party_votes_ec = safe_get(party_sheet, 'total_votes_ec', default=0, force='int')
            party_ec_variance = safe_get(party_sheet, 'total_ec_variance', default=0, force='int')
            party_valid_votes = party_votes
            # set the total votes and ec
            report_sheet[xcode] = party_votes
            count = total_sheets['invalid'].get(xcode, 0)
            count += 0
            total_sheets['invalid'][xcode] = count
            count = total_sheets['valid'].get(xcode, 0)
            count += party_votes
            total_sheets['valid'][xcode] = count
            count = total_sheets['total'].get(xcode, 0)
            count += party_votes
            total_sheets['total'][xcode] = count
            total_sheets['total']['total_votes_ec'] += party_votes_ec
            total_sheets['total']['total_votes'] += party_votes
            total_sheets['total']['total_valid_votes'] += party_votes
            total_sheets['valid']['total_votes_ec'] += party_votes_ec
            total_sheets['valid']['total_votes'] += party_votes
            total_sheets['valid']['total_valid_votes'] += party_valid_votes
            total_sheets['valid']['total_ec_variance'] += party_ec_variance
            total_sheets['invalid']['total_votes_ec'] += 0
            total_sheets['invalid']['total_votes'] += 0
            if total_sheets['total'][xcode] > 0:
                column['has_votes'] = 1

        reports.append(report_sheet)
        p += 1
    # set the leading party
    if max_votes_party is not None:
        reports[max_votes_party]['lead'] = 1

    totals_row = [
                    total_sheets['valid'],
                    total_sheets['invalid'],
                    total_sheets['total']
                ]
    total_votes = totals_row[0]['total_votes']
    if total_votes > 0:
        for report in reports:
            report['percentage'] = round(100 * report['total_votes'] / total_votes, 20)

    context = dict(
        title=report_title,
        level=level,
        columns=columns,
        reports=reports,
        totals_row=totals_row,
        seats=seats,
        zone=zone,
        rid=rid,
        office_type=office_type,
        zone_type=zone_type,
        sub_zone_type=sub_zone_type,
        sub_zone_type_plural=sub_zone_type_plural,
        super_zone=super_zone,
        super_zone_link=super_zone_link,
        sub_zone_link=sub_zone_link,
    )
    return render(request, template, context)

@login_required
def region_parliamentary_report(request, rpk=None):
    level = GeoLevelChoices.CONSTITUENCY
    zone_ct_model = Constituency
    zone_ct = get_zone_ct(zone_ct_model)
    report_title = f'Parliamentary Collation Results (Regional)'
    template = f'report/report.html'
    zone_type = 'region'
    sub_zone_type = 'constituency'
    sub_zone_type_plural = 'constituencies'
    sub_zone_link = f'/reports/parliamentary/{sub_zone_type}/'
    super_zone_link = '/reports/parliamentary/nation/'
    sheet_model = RegionalCollationSheet
    column_model = Constituency
    page_model = Region
    zone = page_model.objects.filter(pk=rpk).first()
    super_zone = zone.nation if zone is not None else None
    key_field = 'title'
    rid=rpk
    office_type='parliamentary'

    # find all parties and stats for each (y-axis)
    xfields = ['id', 'code', 'title',
                'total_votes',
                'total_valid_votes',
                'total_votes_ec',
                'total_ec_variance',
                'total_invalid_votes',
                'sub_zone_total_votes_ec',
                'sub_zone_total_ec_variance',
                ]
    sub_xannotates = dict(
                # sum all total_votes (col) in the collation table
                sub_total_valid_votes=Sum(
                                        F('regional_collation_sheets__total_votes'),
                                        filter=Q(regional_collation_sheets__zone_ct=zone_ct)
                                                & Q(regional_collation_sheets__constituency__region_id=rpk)
                                    ),
                # sum all total_votes_ec (col) in the collation table
                sub_total_votes_ec=Sum(
                                    F('regional_collation_sheets__total_votes_ec'),
                                    filter=Q(regional_collation_sheets__zone_ct=zone_ct)
                                            & Q(regional_collation_sheets__constituency__region_id=rpk)

                                ),
                sub_total_ec_variance=F('sub_total_valid_votes') - F('sub_total_votes_ec'),
    )
    parties_sub_counts = Party.objects \
                    .filter(pk=OuterRef('pk')) \
                    .annotate(**sub_xannotates) \
                    .order_by('code')
    # run sub queries to include additional columns (national collation sheet)
    parties_sub_counts_votes = parties_sub_counts.values(*['sub_total_valid_votes'][:1])
    parties_sub_counts_votes_ec = parties_sub_counts.values(*['sub_total_votes_ec'])[:1]
    parties_sub_counts_variance = parties_sub_counts.values(*['sub_total_ec_variance'])[:1]
    xannotates = dict(
                        # sum all total_votes (col) in the collation table
                        total_valid_votes=Sum(
                                            F('national_collation_sheets__total_votes'),
                                            filter=Q(national_collation_sheets__zone_ct=zone_ct)
                                                    & Q(national_collation_sheets__region_id=rpk)
                                        ),
                        # sum all total_votes_ec (col) in the collation table
                        total_votes_ec=Sum(
                                            F('national_collation_sheets__total_votes_ec'),
                                            filter=Q(national_collation_sheets__zone_ct=zone_ct)
                                                    & Q(national_collation_sheets__region_id=rpk)
                                        ),
                        # sum all total_invalid_votes (col) in the collation table
                        total_invalid_votes=Sum(
                                                F('national_collation_sheets__total_invalid_votes'),
                                                filter=Q(national_collation_sheets__zone_ct=zone_ct)
                                                        & Q(national_collation_sheets__region_id=rpk)
                                            ),
                        total_votes=F('total_valid_votes') + F('total_invalid_votes'),
                        total_ec_variance=F('total_votes') - F('total_votes_ec'),
                        sub_zone_total_votes_ec=Subquery(parties_sub_counts_votes_ec, output_field=IntegerField()),
                        sub_zone_total_ec_variance=Subquery(parties_sub_counts_variance, output_field=IntegerField()),
                    )
    parties = Party.objects \
                    .annotate(**xannotates) \
                    .values(*xfields) \
                    .order_by('code').all()

    totals_row = dict(
                    valid={},
                    invalid={},
                    total={},
                )
    reports = []
    max_votes = 0
    max_votes_party = None
    p = 0
    total_sheets = get_blank_total_sheets()
    columns = []
    seats = []

    columns = column_model.objects.values('id', 'title') \
                    .annotate(key=Replace(
                                    Func(F(key_field), function='LOWER'),
                                    Value(' '),
                                    Value('_')
                                )) \
                    .filter(region=zone) \
                    .order_by('title').all()
    sub_zones = [c['id'] for c in columns]
    for party in parties:
        yid = party['id']
        seats = ParliamentarySummarySheet.objects \
                                        .filter(
                                            constituency_id__in=sub_zones,
                                            candidate__in=Candidate.objects \
                                                                    .values('id')
                                                                    .filter(party_id=yid) \
                                                                    .all(),
                                            position__in=Position.objects \
                                                                    .values('id')
                                                                    .filter(zone_ct=zone_ct) \
                                                                    .all(),
                                        ).all().count()
        # find the leading party
        if max_votes <= seats:
            max_votes = seats
            max_votes_party = p
            total_sheets['valid']['seats'] += seats

        total_votes = safe_get(party, 'total_votes', default=0)
        total_valid_votes = safe_get(party, 'total_valid_votes', default=0)
        total_invalid_votes = safe_get(party, 'total_invalid_votes', default=0)
        total_votes_ec = safe_get(party, 'total_votes_ec', default=0)
        total_ec_variance = safe_get(party, 'total_ec_variance', default=0)
        sub_zone_total_votes_ec = safe_get(party, 'sub_zone_total_votes_ec', default=0)
        sub_zone_total_ec_variance = safe_get(party, 'sub_zone_total_ec_variance', default=0)
        report_sheet = dict(
            party_id=party['id'],
            party_code=party['code'],
            party_title=party['title'],
            lead=0,
            seats=seats,
            total_votes=total_votes,
            total_votes_ec=total_votes_ec,
            total_valid_votes=total_valid_votes,
            total_ec_variance=total_ec_variance,
            total_invalid_votes=total_invalid_votes,
            sub_zone_total_votes_ec=sub_zone_total_votes_ec,
            sub_zone_total_ec_variance=sub_zone_total_ec_variance,
        )
        # find the leading party
        for column in columns:
            xid = column['id']
            xcode = column['key']
            party_sheet = sheet_model.objects \
                                    .annotate(total_ec_variance=F('total_votes') - F('total_votes_ec')) \
                                    .values('total_votes', 'total_votes_ec', 'total_ec_variance') \
                                    .filter(
                                        constituency_id=xid,
                                        party_id=yid,
                                        zone_ct=zone_ct,
                                    ).first()
            party_votes = safe_get(party_sheet, 'total_votes', default=0, force='int')
            party_votes_ec = safe_get(party_sheet, 'total_votes_ec', default=0, force='int')
            party_ec_variance = safe_get(party_sheet, 'total_ec_variance', default=0, force='int')
            party_valid_votes = party_votes
            # set the total votes and ec
            report_sheet[xcode] = party_votes
            count = total_sheets['invalid'].get(xcode, 0)
            count += 0
            total_sheets['invalid'][xcode] = count
            count = total_sheets['valid'].get(xcode, 0)
            count += party_votes
            total_sheets['valid'][xcode] = count
            count = total_sheets['total'].get(xcode, 0)
            count += party_votes
            total_sheets['total'][xcode] = count
            total_sheets['total']['total_votes_ec'] += party_votes_ec
            total_sheets['total']['total_votes'] += party_votes
            total_sheets['valid']['total_votes_ec'] += party_votes_ec
            total_sheets['valid']['total_votes'] += party_votes
            total_sheets['valid']['total_valid_votes'] += party_valid_votes
            total_sheets['valid']['total_ec_variance'] += party_ec_variance
            total_sheets['invalid']['total_votes_ec'] += 0
            total_sheets['invalid']['total_votes'] += 0
            if total_sheets['total'][xcode] > 0:
                column['has_votes'] = 1

        reports.append(report_sheet)
        p += 1
    # set the leading party
    if max_votes_party is not None:
        reports[max_votes_party]['lead'] = 1

    totals_row = [
                    total_sheets['valid'],
                    total_sheets['invalid'],
                    total_sheets['total']
                ]
    total_votes = totals_row[0]['total_votes']
    if total_votes > 0:
        for report in reports:
            report['percentage'] = round(100 * report['total_votes'] / total_votes, 20)

    context = dict(
        title=report_title,
        level=level,
        columns=columns,
        reports=reports,
        totals_row=totals_row,
        seats=seats,
        zone=zone,
        rid=rid,
        office_type=office_type,
        zone_type=zone_type,
        sub_zone_type=sub_zone_type,
        sub_zone_type_plural=sub_zone_type_plural,
        super_zone=super_zone,
        super_zone_link=super_zone_link,
        sub_zone_link=sub_zone_link,
    )
    return render(request, template, context)

@login_required
def constituency_parliamentary_report(request, cpk=None):
    level = GeoLevelChoices.CONSTITUENCY
    zone_ct_model = Constituency
    report_title = f'Parliamentary Collation Results (Constituency)'
    template = f'report/report.html'
    zone_type = 'constituency'
    sub_zone_type = 'station'
    sub_zone_type_plural = 'stations'
    sub_zone_link = f'/reports/parliamentary/{sub_zone_type}/'
    super_zone_link = '/reports/parliamentary/region/'
    sheet_model = ConstituencyCollationSheet
    column_model = Station
    page_model = Constituency
    zone = page_model.objects.filter(pk=cpk).first()
    super_zone = zone.region if zone is not None else None
    zone_ct = get_zone_ct(zone_ct_model)
    key_field = 'code'
    rid=cpk
    office_type='parliamentary'

    # find all parties and stats for each (y-axis)
    xfields = ['id', 'code', 'title',
                'total_votes',
                'total_valid_votes',
                'total_votes_ec',
                'total_ec_variance',
                'total_invalid_votes',
                'sub_zone_total_votes_ec',
                'sub_zone_total_ec_variance',
                ]
    sub_xannotates = dict(
                # sum all total_votes (col) in the collation table
                sub_total_valid_votes=Sum(
                                        F('constituency_collation_sheets__total_votes'),
                                        filter=Q(constituency_collation_sheets__zone_ct=zone_ct)
                                                & Q(constituency_collation_sheets__station__constituency_id=cpk)
                                    ),
                # sum all total_votes_ec (col) in the collation table
                sub_total_votes_ec=Sum(
                                    F('constituency_collation_sheets__total_votes_ec'),
                                    filter=Q(constituency_collation_sheets__zone_ct=zone_ct)
                                            & Q(constituency_collation_sheets__station__constituency_id=cpk)

                                ),
                sub_total_ec_variance=F('sub_total_valid_votes') - F('sub_total_votes_ec'),
    )
    parties_sub_counts = Party.objects \
                    .filter(pk=OuterRef('pk')) \
                    .annotate(**sub_xannotates) \
                    .order_by('code')
    # run sub queries to include additional columns (national collation sheet)
    parties_sub_counts_votes = parties_sub_counts.values(*['sub_total_valid_votes'][:1])
    parties_sub_counts_votes_ec = parties_sub_counts.values(*['sub_total_votes_ec'])[:1]
    parties_sub_counts_variance = parties_sub_counts.values(*['sub_total_ec_variance'])[:1]
    xannotates = dict(
                        # sum all total_votes (col) in the collation table
                        total_valid_votes=Sum(
                                            F('regional_collation_sheets__total_votes'),
                                            filter=Q(regional_collation_sheets__zone_ct=zone_ct)
                                                    & Q(regional_collation_sheets__constituency_id=cpk)
                                        ),
                        # sum all total_votes_ec (col) in the collation table
                        total_votes_ec=Sum(
                                            F('regional_collation_sheets__total_votes_ec'),
                                            filter=Q(regional_collation_sheets__zone_ct=zone_ct)
                                                    & Q(regional_collation_sheets__constituency_id=cpk)
                                        ),
                        # sum all total_invalid_votes (col) in the collation table
                        total_invalid_votes=Sum(
                                                F('regional_collation_sheets__total_invalid_votes'),
                                                filter=Q(regional_collation_sheets__zone_ct=zone_ct)
                                                        & Q(regional_collation_sheets__constituency_id=cpk)
                                            ),
                        total_votes=F('total_valid_votes') + F('total_invalid_votes'),
                        total_ec_variance=F('total_votes') - F('total_votes_ec'),
                        sub_zone_total_votes_ec=Subquery(parties_sub_counts_votes_ec, output_field=IntegerField()),
                        sub_zone_total_ec_variance=Subquery(parties_sub_counts_variance, output_field=IntegerField()),
                    )
    parties = Party.objects \
                    .annotate(**xannotates) \
                    .values(*xfields) \
                    .order_by('code').all()

    totals_row = dict(
                    valid={},
                    invalid={},
                    total={},
                )
    reports = []
    max_votes = 0
    max_votes_party = None
    p = 0
    total_sheets = get_blank_total_sheets()
    columns = []
    seats = []

    columns = column_model.objects.values('id', 'title', 'code') \
                    .annotate(key=Replace(
                                    Func(F(key_field), function='LOWER'),
                                    Value(' '),
                                    Value('_')
                                )) \
                    .filter(constituency=zone) \
                    .order_by('title').all()
    for party in parties:
        yid = party['id']
        seats = ParliamentarySummarySheet.objects \
                                        .filter(
                                            constituency=zone,
                                            candidate__in=Candidate.objects \
                                                                    .values('id')
                                                                    .filter(party_id=yid) \
                                                                    .all(),
                                            position__in=Position.objects \
                                                                    .values('id')
                                                                    .filter(zone_ct=zone_ct) \
                                                                    .all(),
                                        ).all().count()
        # find the leading party
        if max_votes <= seats:
            max_votes = seats
            max_votes_party = p
            total_sheets['valid']['seats'] += seats

        total_votes = safe_get(party, 'total_votes', default=0)
        total_valid_votes = safe_get(party, 'total_valid_votes', default=0)
        total_invalid_votes = safe_get(party, 'total_invalid_votes', default=0)
        total_votes_ec = safe_get(party, 'total_votes_ec', default=0)
        total_ec_variance = safe_get(party, 'total_ec_variance', default=0)
        sub_zone_total_votes_ec = safe_get(party, 'sub_zone_total_votes_ec', default=0)
        sub_zone_total_ec_variance = safe_get(party, 'sub_zone_total_ec_variance', default=0)
        report_sheet = dict(
            party_id=party['id'],
            party_code=party['code'],
            party_title=party['title'],
            lead=0,
            seats=seats,
            total_votes=total_votes,
            total_votes_ec=total_votes_ec,
            total_valid_votes=total_valid_votes,
            total_ec_variance=total_ec_variance,
            total_invalid_votes=total_invalid_votes,
            sub_zone_total_votes_ec=sub_zone_total_votes_ec,
            sub_zone_total_ec_variance=sub_zone_total_ec_variance,
        )
        for column in columns:
            xid = column['id']
            xcode = column['key']
            party_sheet = sheet_model.objects \
                                    .annotate(total_ec_variance=F('total_votes') - F('total_votes_ec')) \
                                    .values('total_votes', 'total_votes_ec', 'total_ec_variance') \
                                    .filter(
                                        station_id=xid,
                                        party_id=yid,
                                        zone_ct=zone_ct,
                                    ).first()
            
            party_votes = safe_get(party_sheet, 'total_votes', default=0, force='int')
            party_votes_ec = safe_get(party_sheet, 'total_votes_ec', default=0, force='int')
            party_ec_variance = safe_get(party_sheet, 'total_ec_variance', default=0, force='int')
            party_valid_votes = party_votes
            # set the total votes and ec
            report_sheet[xcode] = party_votes
            count = total_sheets['invalid'].get(xcode, 0)
            count += 0
            total_sheets['invalid'][xcode] = count
            count = total_sheets['valid'].get(xcode, 0)
            count += party_votes
            total_sheets['valid'][xcode] = count
            count = total_sheets['total'].get(xcode, 0)
            count += party_votes
            total_sheets['total'][xcode] = count
            total_sheets['total']['total_votes_ec'] += party_votes_ec
            total_sheets['total']['total_votes'] += party_votes
            total_sheets['valid']['total_votes_ec'] += party_votes_ec
            total_sheets['valid']['total_votes'] += party_votes
            total_sheets['valid']['total_valid_votes'] += party_valid_votes
            total_sheets['valid']['total_ec_variance'] += party_ec_variance
            total_sheets['invalid']['total_votes_ec'] += 0
            total_sheets['invalid']['total_votes'] += 0
            if total_sheets['total'][xcode] > 0:
                column['has_votes'] = 1
 
        reports.append(report_sheet)
        p += 1
    # set the leading party
    if max_votes_party is not None:
        reports[max_votes_party]['lead'] = 1

    totals_row = [
                    total_sheets['valid'],
                    total_sheets['invalid'],
                    total_sheets['total']
                ]
    total_votes = totals_row[0]['total_votes']
    if total_votes > 0:
        for report in reports:
            report['percentage'] = round(100 * report['total_votes'] / total_votes, 20)

    context = dict(
        title=report_title,
        level=level,
        columns=columns,
        reports=reports,
        totals_row=totals_row,
        seats=seats,
        zone=zone,
        rid=rid,
        office_type=office_type,
        zone_type=zone_type,
        sub_zone_type=sub_zone_type,
        sub_zone_type_plural=sub_zone_type_plural,
        super_zone=super_zone,
        super_zone_link=super_zone_link,
        sub_zone_link=sub_zone_link,
    )
    return render(request, template, context)

@login_required
def station_parliamentary_report(request, spk=None):
    level = GeoLevelChoices.CONSTITUENCY
    zone_ct_model = Constituency
    report_title = f'Parliamentary Collation Results (Station)'
    template = f'report/report.html'
    zone_type = 'station'
    sub_zone_type = ''
    sub_zone_type_plural = None
    sub_zone_link = '#'
    super_zone_link = '/reports/parliamentary/constituency/'
    sheet_model = StationCollationSheet
    column_model = None
    page_model = Station
    zone = page_model.objects.filter(pk=spk).first()
    super_zone = zone.constituency if zone is not None else None
    zone_ct = get_zone_ct(zone_ct_model)
    rid=spk
    office_type='parliamentary'
    sub_zone_type=None

    # find all parties and stats for each (y-axis)
    xfields = ['id', 'code', 'title',
                'total_votes',
                'total_valid_votes',
                'total_votes_ec',
                'total_ec_variance',
                'total_invalid_votes',]
    xannotates = dict(
                        # sum all total_votes (col) in the collation table
                        total_valid_votes=Sum(
                                            F('constituency_collation_sheets__total_votes'),
                                            filter=Q(constituency_collation_sheets__zone_ct=zone_ct)
                                                    & Q(constituency_collation_sheets__station_id=spk)
                                        ),
                        # sum all total_votes_ec (col) in the collation table
                        total_votes_ec=Sum(
                                            F('constituency_collation_sheets__total_votes'),
                                            filter=Q(constituency_collation_sheets__zone_ct=zone_ct)
                                                    & Q(constituency_collation_sheets__station_id=spk)
                                        ),
                        # sum all total_invalid_votes (col) in the collation table
                        total_invalid_votes=Sum(
                                            F('constituency_collation_sheets__total_votes'),
                                            filter=Q(constituency_collation_sheets__zone_ct=zone_ct)
                                                    & Q(constituency_collation_sheets__station_id=spk)
                                            ),
                        total_votes=F('total_valid_votes') + F('total_invalid_votes'),
                        total_ec_variance=F('total_votes') - F('total_votes_ec'),
                    )
    parties = Party.objects \
                    .annotate(**xannotates) \
                    .values(*xfields) \
                    .order_by('code').all()

    totals_row = dict(
                    valid={},
                    invalid={},
                    total={},
                )
    reports = []
    max_votes = 0
    max_votes_party = None
    p = 0
    total_sheets = get_blank_total_sheets()
    columns = []
    seats = []
    columns = []

    for party in parties:
        yid = party['id']
        seats = ParliamentarySummarySheet.objects \
                                        .filter(
                                            constituency=super_zone,
                                            candidate__in=Candidate.objects \
                                                                    .values('id')
                                                                    .filter(party_id=yid) \
                                                                    .all(),
                                            position__in=Position.objects \
                                                                    .values('id')
                                                                    .filter(zone_ct=zone_ct) \
                                                                    .all(),
                                        ).all().count()
        # find the leading party
        if max_votes <= seats:
            max_votes = seats
            max_votes_party = p
            total_sheets['valid']['seats'] += seats

        total_votes = safe_get(party, 'total_votes', default=0)
        total_valid_votes = safe_get(party, 'total_valid_votes', default=0)
        total_invalid_votes = safe_get(party, 'total_invalid_votes', default=0)
        total_votes_ec = safe_get(party, 'total_votes_ec', default=0)
        total_ec_variance = safe_get(party, 'total_ec_variance', default=0)
        sub_zone_total_votes_ec = safe_get(party, 'sub_zone_total_votes_ec', default=0)
        sub_zone_total_ec_variance = safe_get(party, 'sub_zone_total_ec_variance', default=0)
        report_sheet = dict(
            party_id=party['id'],
            party_code=party['code'],
            party_title=party['title'],
            lead=0,
            seats=seats,
            total_votes=total_votes,
            total_votes_ec=total_votes_ec,
            total_valid_votes=total_valid_votes,
            total_ec_variance=total_ec_variance,
            total_invalid_votes=total_invalid_votes,
            sub_zone_total_votes_ec=sub_zone_total_votes_ec,
            sub_zone_total_ec_variance=sub_zone_total_ec_variance,
        )
        # set the total votes and ec
        total_sheets['total']['total_votes_ec'] += total_votes_ec
        total_sheets['total']['total_votes'] += total_votes
        total_sheets['valid']['total_votes_ec'] += total_votes_ec
        total_sheets['valid']['total_votes'] += total_votes
        total_sheets['valid']['total_valid_votes'] += total_valid_votes
        total_sheets['valid']['total_ec_variance'] += total_ec_variance
        total_sheets['invalid']['total_votes_ec'] += 0
        total_sheets['invalid']['total_votes'] += 0

        reports.append(report_sheet)
        p += 1
    # set the leading party
    if max_votes_party is not None:
        reports[max_votes_party]['lead'] = 1

    totals_row = [
                    total_sheets['valid'],
                    total_sheets['invalid'],
                    total_sheets['total']
                ]
    total_votes = totals_row[0]['total_votes']
    if total_votes > 0:
        for report in reports:
            report['percentage'] = round(100 * report['total_votes'] / total_votes, 20)

    context = dict(
        title=report_title,
        level=level,
        columns=columns,
        reports=reports,
        totals_row=totals_row,
        seats=seats,
        zone=zone,
        rid=rid,
        office_type=office_type,
        zone_type=zone_type,
        sub_zone_type=sub_zone_type,
        sub_zone_type_plural=sub_zone_type_plural,
        super_zone=super_zone,
        super_zone_link=super_zone_link,
        sub_zone_link=sub_zone_link,
    )
    return render(request, template, context)



@login_required
def nation_presidential_report_raw(request):
    template = f'report/presidential/nation_report.html'
    report_title = f'Presidential Collation Results (National)'
    level = GeoLevelChoices.NATIONAL
    nation = Nation.objects.first()
    nation_id = 0
    if nation is not None:
        nation = nation.pk
    key_field = 'title'
    
    zone_ct = get_zone_ct(Nation)
    zone_ct_id = ""
    if zone_ct is not None:
        zone_ct_id = zone_ct.pk

    positions = Position.objects.filter(zone_ct=zone_ct).all()
    candidates = Candidate.objects \
                            .filter(
                                position__in=positions
                            ).all()

    position_ids = ''
    for p in positions:
        position_ids += ',' if len(position_ids) > 0 else ''
        position_ids += f'{p.id}'

    columns = Region.objects.values('id', 'title') \
                    .annotate(key=Replace(
                                    Func(F(key_field), function='LOWER'),
                                    Value(' '),
                                    Value('_')
                                )) \
                    .order_by('title').all()
    cursor = connection.cursor()

    sums = ''
    sum_joins = ''
    table = 'poll_national_collation_sheet'
    summary_table = 'poll_presidential_summary_sheet'
    fields = [
        'party_id', 'party_code', 'candidates', 'votes', 'seats',
    ]

    imax = 'max'
    max_query = f'''SELECT MAX(sums.votes) FROM (
        SELECT
            SUM(ncs{imax}.total_votes) AS votes
        FROM {table} ncs{imax}
            LEFT JOIN poll_party p{imax} ON p{imax}.id = ncs{imax}.party_id
            LEFT JOIN geo_region r{imax} ON r{imax}.id = ncs{imax}.region_id
            LEFT JOIN geo_nation n{imax} ON n{imax}.id = r{imax}.nation_id
        WHERE
            ncs{imax}.zone_ct_id = {zone_ct_id}
            AND n{imax}.id = {nation_id}
        GROUP BY p{imax}.id
        ) AS sums'''
    max_votes = 0
    try:
        cursor.execute(max_query)
        rows = cursor.fetchall()
        max_votes = max(rows)[0]
    except Exception as e:
        print("There was an error running raw query", e)
    if max_votes is None:
        max_votes = 0

    totals_row = dict(
                    valid={},
                    invalid={},
                    total={},
                )

    i = 0
    for column in columns:
        column_label = column['title']
        column_value = column['id']
        key = f'votes_{snakeify(column_label)}'
        sums += f' SUM(ncs{i}.total_votes) AS {key},'
        sum_joins += f''' LEFT JOIN (
                    SELECT
                            ncs{i}.id,
                            ncs{i}.total_votes
                        FROM {table} ncs{i}
                            LEFT JOIN poll_party p{i} ON p{i}.id = ncs{i}.party_id
                            LEFT JOIN geo_region r{i} ON r{i}.id = ncs{i}.region_id
                        WHERE
                            ncs{i}.zone_ct_id = {zone_ct_id}
                            AND ncs{i}.region_id = {column_value}
                        GROUP BY ncs{i}.id, ncs{i}.total_votes
                        ORDER BY ncs{i}.id ASC
                ) AS ncs{i} ON ncs{i}.id = ncs.id
        '''
        fields.append(key)

        total_valid = NationalCollationSheet.objects \
                                .values('total_votes') \
                                .filter(
                                    region_id=column_value,
                                    zone_ct=zone_ct,
                                ) \
                                .aggregate(Sum('total_votes'))['total_votes__sum']

        stations = Station.objects \
                            .values('id') \
                            .filter(constituency__in=Constituency.objects
                                                                .values('id')
                                                                .filter(region_id=column_value)
                                                                .all()) \
                            .all()
        total_invalid = ResultSheet.objects \
                    .values('total_invalid_votes') \
                    .filter(
                        position__in=positions,
                        station__in=stations
                    ).aggregate(Sum('total_invalid_votes'))['total_invalid_votes__sum']
        
        total_invalid = total_invalid or 0
        total_valid = total_valid or 0
        total = total_valid + total_invalid
        total_key = snakeify(column_label)
        totals_row['invalid'][total_key] = total_invalid
        totals_row['valid'][total_key] = total_valid
        totals_row['total'][total_key] = total
        i += 1

    query = f'''SELECT
        p.id, p.code,
        STRING_AGG(
            DISTINCT(CONCAT(ca.prefix, ' ', ca.first_name, ' ', ca.last_name)), ', '
        ) AS candidates,
        SUM(ncs.total_votes) votes,
        (CASE WHEN (SUM(ncs.total_votes) = {max_votes} AND SUM(ncs.total_votes) > 0) THEN 1 ELSE 0 END) AS seats,
        {sums}
        '|' AS row_end
    FROM {table} ncs
        LEFT JOIN poll_party p ON p.id = ncs.party_id
        LEFT JOIN geo_region r ON r.id = ncs.region_id

        LEFT JOIN people_candidate ca ON
            ca.party_id = ncs.party_id
            AND ca.position_id IN ({position_ids})

        -- LEFT JOIN {summary_table} summ ON
            -- summ.constituency_id IN (
                -- SELECT c.id
                    -- FROM geo_constituency c
                    -- WHERE c.region_id = r.id
            -- )
            -- AND summ.candidate_id IN (
                -- SELECT ca.id
                    -- FROM people_candidate ca
                    -- WHERE ca.party_id = p.id
            -- )

        {sum_joins}
    WHERE
        ncs.zone_ct_id = {zone_ct_id}
    GROUP BY p.id
    ORDER BY p.code ASC;'''

    reports = []
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            reports.append(dict(zip(fields, row)))
    except Exception as e:
        print("There was an error running raw query", e)

    context = dict(
        title=report_title,
        level=level,
        columns=columns,
        reports=reports,
        zone=nation,
        totals_row=totals_row,
        zone_type='nation',
        sub_zone_type='region',
        sub_zone_type_plural='regions',
        super_zone=None,
        super_zone_link='#',
        sub_zone_link='/reports/presidential/region/',
    )   
    return render(request, template, context)

@login_required
def region_presidential_report_raw(request, rpk=None):
    template = f'report/presidential/region_report.html'
    report_title = f'Regional Presidential Collation Results'
    level = GeoLevelChoices.NATIONAL
    zone_ct = get_zone_ct(Nation)
    zone_ct_id = ""
    if zone_ct is not None:
        zone_ct_id = zone_ct.pk
    region = Region.objects.filter(pk=rpk).first()
    columns = Constituency.objects.filter(region=region).order_by('title').all()
    cursor = connection.cursor()

    position_ids = ''
    for p in Position.objects.filter(zone_ct=zone_ct).all():
        position_ids += ',' if len(position_ids) > 0 else ''
        position_ids += f'{p.id}'

    sums = ''
    sum_joins = ''
    table = 'poll_regional_collation_sheet'
    summary_table = 'poll_presidential_summary_sheet'
    fields = [
        'party_id', 'party_code',
        'candidates',
        'votes', 'seats',
    ]

    imax = 'max'
    max_query = f'''SELECT
            SUM(ncs{imax}.total_votes) sum_votes
        FROM {table} ncs{imax}
            LEFT JOIN poll_party p{imax} ON p{imax}.id = ncs{imax}.party_id
            LEFT JOIN geo_constituency c{imax} ON c{imax}.id = ncs{imax}.constituency_id
            LEFT JOIN geo_region r{imax} ON r{imax}.id = c{imax}.region_id
        WHERE
            ncs{imax}.zone_ct_id = {zone_ct_id}
            AND r{imax}.id = {rpk}
        GROUP BY p{imax}.id'''
    max_votes = 0
    try:
        cursor.execute(max_query)
        rows = cursor.fetchall()
        max_votes = max(rows)[0]
    except Exception as e:
        print("There was an error running raw query", e)
    if max_votes is None:
        max_votes = 0

    i = 0
    for column in columns:
        key = f'votes_{snakeify(column.title)}'
        sums += f' SUM(ncs{i}.total_votes) AS {key},'
        sum_joins += f''' LEFT JOIN (
                    SELECT
                            ncs{i}.id,
                            ncs{i}.total_votes
                        FROM {table} ncs{i}
                            LEFT JOIN poll_party p{i} ON p{i}.id = ncs{i}.party_id
                            LEFT JOIN geo_constituency c{i} ON c{i}.id = ncs{i}.constituency_id
                            LEFT JOIN geo_region r{i} ON r{i}.id = c{i}.region_id
                        WHERE
                            ncs{i}.zone_ct_id = {zone_ct_id}
                            AND ncs{i}.constituency_id = {column.pk}
                            AND r{i}.id = {rpk}
                        GROUP BY ncs{i}.id, ncs{i}.total_votes
                        ORDER BY ncs{i}.id ASC
                ) AS ncs{i} ON ncs{i}.id = ncs.id
        '''
        fields.append(key)
        i += 1

    query = f'''SELECT
            p.id, p.code,
            STRING_AGG(
                DISTINCT(CONCAT(ca.prefix, ' ', ca.first_name, ' ', ca.last_name)), ', '
            ) AS candidates,
            SUM(ncs.total_votes) votes,
            (CASE WHEN (SUM(ncs.total_votes) = {max_votes} AND SUM(ncs.total_votes) > 0) THEN 1 ELSE 0 END) AS seats,
            {sums}
            '|' AS row_end
        FROM {table} ncs

            LEFT JOIN poll_party p ON p.id = ncs.party_id
            LEFT JOIN geo_constituency c ON c.id = ncs.constituency_id
            LEFT JOIN geo_region r ON r.id = c.region_id

            -- LEFT JOIN {summary_table} summ ON
                -- summ.constituency_id = c.id
                -- AND summ.constituency_id = ncs.constituency_id
                -- AND summ.candidate_id IN (
                    -- SELECT ca.id
                    -- FROM people_candidate ca
                    -- WHERE ca.party_id = p.id
                -- )

            LEFT JOIN people_candidate ca ON
                ca.party_id = p.id
                AND ca.position_id IN ({position_ids})

            {sum_joins}
        WHERE
            ncs.zone_ct_id = {zone_ct_id}
            AND r.id = {rpk}
        GROUP BY p.id
        ORDER BY p.code ASC;'''

    reports = []
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            reports.append(dict(zip(fields, row)))
    except Exception as e:
        print("There was an error running raw query", e)

    context = dict(
        title=report_title,
        level=level,
        columns=columns,
        reports=reports,
        zone=region,
        zone_type='region',
        sub_zone_type='constituency',
        sub_zone_type_plural='constituencies',
        super_zone=region.nation,
        super_zone_link='/reports/presidential/nation/',
        sub_zone_link='/reports/presidential/constituency/',
    )    
    return render(request, template, context)

@login_required
def constituency_presidential_report_raw(request, cpk=None):
    '''
    '''

    template = f'report/presidential/constituency_report.html'
    report_title = f'Constituency Presidential Collation Results'
    level = GeoLevelChoices.NATIONAL
    zone_ct = get_zone_ct(Nation)
    zone_ct_id = ""
    if zone_ct is not None:
        zone_ct_id = zone_ct.pk
    constituency = Constituency.objects.filter(pk=cpk).first()
    columns = Station.objects.filter(constituency=constituency).order_by('code').all()
    cursor = connection.cursor()

    position_ids = ''
    for p in Position.objects.filter(zone_ct=zone_ct).all():
        position_ids += ',' if len(position_ids) > 0 else ''
        position_ids += f'{p.id}'

    sums = ''
    sum_joins = ''
    table = 'poll_constituency_collation_sheet'
    summary_table = 'poll_presidential_summary_sheet'
    fields = [
        'party_id', 'party_code', 'candidates', 'votes', 'seats', 'max_votes'
    ]


    imax = 'max'
    max_query = f'''SELECT
            SUM(ncs{imax}.total_votes) sum_votes
        FROM {table} ncs{imax}
            LEFT JOIN poll_party p{imax} ON p{imax}.id = ncs{imax}.party_id
            LEFT JOIN geo_station s{imax} ON s{imax}.id = ncs{imax}.station_id
            LEFT JOIN geo_constituency c{imax} ON c{imax}.id = s{imax}.constituency_id
            -- LEFT JOIN geo_region r ON r{imax}.id = c{imax}.region_id
        WHERE
            ncs{imax}.zone_ct_id = {zone_ct_id}
            AND c{imax}.id = {cpk}
        GROUP BY p{imax}.id'''
    max_votes = 0
    try:
        cursor.execute(max_query)
        rows = cursor.fetchall()
        max_votes = max(rows)[0]
    except Exception as e:
        print("There was an error running raw query", e)
    if max_votes is None:
        max_votes = 0


    i = 0
    for column in columns:
        key = f'votes_{snakeify(column.title)}'
        sums += f' SUM(ncs{i}.total_votes) AS {key},'
        sum_joins += f''' LEFT JOIN (
                    SELECT
                            ncs{i}.id,
                            ncs{i}.total_votes
                        FROM {table} ncs{i}
                            LEFT JOIN poll_party p{i} ON p{i}.id = ncs{i}.party_id
                            LEFT JOIN geo_station s{i} ON s{i}.id = ncs{i}.station_id
                            LEFT JOIN geo_constituency c{i} ON c{i}.id = s{i}.constituency_id
                            LEFT JOIN geo_region r{i} ON r{i}.id = c{i}.region_id
                        WHERE
                            ncs{i}.zone_ct_id = {zone_ct_id}
                            AND ncs{i}.station_id = {column.pk}
                            AND c{i}.id = {cpk}
                        GROUP BY ncs{i}.id, ncs{i}.total_votes
                        ORDER BY ncs{i}.id ASC
                ) AS ncs{i} ON ncs{i}.id = ncs.id
        '''
        fields.append(key)
        i += 1

    query = f'''SELECT
        p.id, p.code,
        STRING_AGG(
            DISTINCT(CONCAT(ca.prefix, ' ', ca.first_name, ' ', ca.last_name)), ', '
        ) AS candidates,
        SUM(ncs.total_votes) votes,
        (CASE WHEN (SUM(ncs.total_votes) = {max_votes} AND SUM(ncs.total_votes) > 0) THEN 1 ELSE 0 END) AS seats,
        {max_votes} AS seats,
        {sums}
        '|' AS row_end
    FROM {table} ncs
        LEFT JOIN poll_party p ON p.id = ncs.party_id
        LEFT JOIN geo_station s ON s.id = ncs.station_id
        LEFT JOIN geo_constituency c ON c.id = s.constituency_id
        LEFT JOIN geo_region r ON r.id = c.region_id
        LEFT JOIN people_candidate ca ON
            ca.party_id = p.id
            AND ca.position_id IN ({position_ids})
        {sum_joins}
    WHERE
        ncs.zone_ct_id = {zone_ct_id}
        AND c.id = {cpk}
    GROUP BY p.id
    ORDER BY p.code ASC;'''

    reports = []
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            reports.append(dict(zip(fields, row)))
    except Exception as e:
        print("There was an error running raw query", e)

    context = dict(
        title=report_title,
        level=level,
        columns=columns,
        reports=reports,
        zone=constituency,
        zone_type='constituency',
        sub_zone_type='station',
        sub_zone_type_plural='stations',
        super_zone=constituency.region,
        super_zone_link='/reports/presidential/region/',
        sub_zone_link='/reports/presidential/station/',
    )
    return render(request, template, context)

@login_required
def station_presidential_report_raw(request, spk=None):
    template = f'report/presidential/station_report.html'
    report_title = f'Station Presidential Collation Results'
    level = GeoLevelChoices.NATIONAL
    zone_ct = get_zone_ct(Nation)
    zone_ct_id = ""
    if zone_ct is not None:
        zone_ct_id = zone_ct.pk
    station = Station.objects.filter(pk=spk).first()
    columns = [] # Station.objects.filter(constituency=constituency).order_by('code').all()

    sums = ''
    sum_joins = ''
    table = 'poll_station_collation_sheet'
    fields = [
        'party_id', 'party_code', 'candidate_name', 'votes', 'seats', 'max_votes',
    ]
    
    select_candidate_name = " CONCAT(ca.prefix, ' ', ca.first_name, ' ', ca.last_name) candidate_name,"
    group_candidate_name = ', ca.prefix, ca.first_name, ca.last_name'

    query = f'''SELECT
        p.id, p.code,
        {select_candidate_name}
        ncs.total_votes AS votes,
        (CASE WHEN (ncs.total_votes = MAX(summ_max.total_votes) AND ncs.total_votes > 0) THEN 1 ELSE 0 END) seats,
        -- MAX(summ_max.total_votes) AS max_votes,
        MAX(ncs.total_votes) AS max_votes,
        {sums}
        '|' AS row_end
    FROM {table} ncs
        LEFT JOIN people_candidate ca ON ca.id = ncs.candidate_id
        LEFT JOIN poll_party p ON p.id = ca.party_id
        LEFT JOIN geo_station s ON s.id = ncs.station_id
        LEFT JOIN geo_constituency c ON c.id = s.constituency_id
        LEFT JOIN geo_region r ON r.id = c.region_id
        {sum_joins}
        LEFT JOIN {table} summ_max ON summ_max.station_id = ncs.station_id
    WHERE
        ncs.zone_ct_id = {zone_ct_id}
        AND s.id = {spk}
    GROUP BY p.id
        , ncs.total_votes
        {group_candidate_name}
    ORDER BY p.code ASC;'''

    reports = []
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            reports.append(dict(zip(fields, row)))
    except Exception as e:
        print("There was an error running raw query", e)

    context = dict(
        title=report_title,
        level=level,
        columns=columns,
        reports=reports,
        zone=station,
        zone_type='station',
        sub_zone_type=None,
        super_zone=station.constituency,
        super_zone_link='/reports/presidential/constituency/',
        sub_zone_link='#',
    )
    return render(request, template, context)


@login_required
def nation_parliamentary_report_raw(request):
    template = f'report/parliamentary/nation_report.html'
    report_title = f'National Parliamentary Collation Results'
    level = GeoLevelChoices.CONSTITUENCY
    nation = Nation.objects.first()
    zone_ct = get_zone_ct(Constituency)
    zone_ct_id = ""
    if zone_ct is not None:
        zone_ct_id = zone_ct.pk
    columns = Region.objects.order_by('title').all()
    cursor = connection.cursor()

    sums = ''
    sum_joins = ''
    table = 'poll_national_collation_sheet'
    summary_table = 'poll_parliamentary_summary_sheet'
    fields = [
        'party_id', 'party_code', 'votes', 'seats',
    ]


    npk = 1
    iseat = 'seat'
    # party_id is this position in the select field array (below)
    party_pos = 2
    seat_fields = [
        'constituency_id', 'constituency',
        'party_id', 'party_code', 'party_title',
        'candidate_id', 'candidates',
        'votes', 'seats',
    ]
    seats = dict()
    seats_query = f'''SELECT
                c{iseat}.id AS constituency_id,
                c{iseat}.title,
                pa{iseat}.id,
                pa{iseat}.code,
                pa{iseat}.title,
                ca{iseat}.id AS candidate_id,
                STRING_AGG(CONCAT(ca{iseat}.prefix, ' ', ca{iseat}.first_name, ' ', ca{iseat}.last_name), ', ') AS candidates{iseat},
                SUM(ssheet{iseat}.votes) AS votes,
                COUNT(ssheet{iseat}.id) AS seats
            FROM
                geo_constituency c{iseat}
                LEFT JOIN geo_region r{iseat} ON r{iseat}.id = c{iseat}.region_id
                LEFT JOIN geo_nation n{iseat} ON n{iseat}.id = r{iseat}.nation_id
                LEFT JOIN poll_parliamentary_summary_sheet ssheet{iseat} ON ssheet{iseat}.constituency_id = c{iseat}.id
                LEFT JOIN people_candidate ca{iseat} ON ca{iseat}.id = ssheet{iseat}.candidate_id
                LEFT JOIN poll_party pa{iseat} ON pa{iseat}.id = ca{iseat}.party_id
            WHERE
                r{iseat}.nation_id = {npk}
            GROUP BY c{iseat}.id, ca{iseat}.id, pa{iseat}.id, pa{iseat}.code, pa{iseat}.title
            ORDER BY candidates{iseat} DESC'''

    try:
        cursor.execute(seats_query)
        rows = cursor.fetchall()
        for row in rows:
            party_seats = seats.get(row[party_pos], [])
            party_seats.append(dict(zip(seat_fields, row)))
            seats[row[party_pos]] = party_seats
    except Exception as e:
        print("There was an error running raw query", e)



    i = 0
    for column in columns:
        key = f'votes_{snakeify(column.title)}'
        sums += f' SUM(ncs{i}.total_votes) AS {key},'
        sum_joins += f''' LEFT JOIN (
                    SELECT
                            ncs{i}.id,
                            ncs{i}.total_votes
                        FROM {table} ncs{i}
                            LEFT JOIN poll_party p{i} ON p{i}.id = ncs{i}.party_id
                            LEFT JOIN geo_region r{i} ON r{i}.id = ncs{i}.region_id
                        WHERE
                            ncs{i}.zone_ct_id = {zone_ct_id}
                            AND ncs{i}.region_id = {column.pk}
                        GROUP BY ncs{i}.id, ncs{i}.total_votes
                        ORDER BY ncs{i}.id ASC
                ) AS ncs{i} ON ncs{i}.id = ncs.id
        '''
        fields.append(key)
        i += 1

    query = f'''SELECT
        p.id, p.code,
        SUM(ncs.total_votes) votes,
        COUNT(summ.id) seats,
        {sums}
        '|' AS row_end
    FROM {table} ncs
        LEFT JOIN poll_party p ON p.id = ncs.party_id
        LEFT JOIN geo_region r ON r.id = ncs.region_id

        LEFT JOIN {summary_table} summ ON
            summ.constituency_id IN (
                SELECT c.id
                    FROM geo_constituency c
                    WHERE c.region_id = r.id
            )
            AND summ.candidate_id IN (
                SELECT ca.id
                    FROM people_candidate ca
                    WHERE ca.party_id = p.id
            )

        {sum_joins}
    WHERE
        ncs.zone_ct_id = {zone_ct_id}
    GROUP BY p.id
    ORDER BY p.code ASC;'''

    reports = []
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            reports.append(dict(zip(fields, row)))
    except Exception as e:
        print("There was an error running raw query", e)

    context = dict(
        title=report_title,
        level=level,
        columns=columns,
        reports=reports,
        seats=seats,
        zone=nation,
        zone_type='nation',
        sub_zone_type='region',
        sub_zone_type_plural='regions',
        super_zone=None,
        super_zone_link='#',
        sub_zone_link='/reports/parliamentary/region/',
    )
    return render(request, template, context)

@login_required
def region_parliamentary_report_raw(request, rpk=None):
    template = f'report/parliamentary/region_report.html'
    report_title = f'Regional Parliamentary Collation Results'
    level = GeoLevelChoices.CONSTITUENCY
    zone_ct = get_zone_ct(Constituency)
    zone_ct_id = ""
    if zone_ct is not None:
        zone_ct_id = zone_ct.pk
    region = Region.objects.filter(pk=rpk).first()
    columns = Constituency.objects.filter(region=region).order_by('title').all()
    cursor = connection.cursor()

    sums = ''
    sum_joins = ''
    table = 'poll_regional_collation_sheet'
    summary_table = 'poll_parliamentary_summary_sheet'
    fields = [
        'party_id', 'party_code', 'votes',
        'seats',
    ]


    iseat = 'seat'
    # party_id is this position in the select field array (below)
    party_pos = 2
    seat_fields = [
        'constituency_id', 'constituency',
        'party_id', 'party_code', 'party_title',
        'candidate_id', 'candidates',
        'votes', 'seats',
    ]
    seats = dict()
    seats_query = f'''SELECT
                c{iseat}.id AS constituency_id,
                c{iseat}.title,
                pa{iseat}.id,
                pa{iseat}.code,
                pa{iseat}.title,
                ca{iseat}.id AS candidate_id,
                STRING_AGG(CONCAT(ca{iseat}.prefix, ' ', ca{iseat}.first_name, ' ', ca{iseat}.last_name), ', ') AS candidates{iseat},
                SUM(ssheet{iseat}.votes) AS votes,
                COUNT(ssheet{iseat}.id) AS seats
            FROM
                geo_constituency c{iseat}
                LEFT JOIN geo_region r{iseat} ON r{iseat}.id = c{iseat}.region_id
                LEFT JOIN poll_parliamentary_summary_sheet ssheet{iseat} ON ssheet{iseat}.constituency_id = c{iseat}.id
                LEFT JOIN people_candidate ca{iseat} ON ca{iseat}.id = ssheet{iseat}.candidate_id
                LEFT JOIN poll_party pa{iseat} ON pa{iseat}.id = ca{iseat}.party_id
            WHERE
                r{iseat}.id = {rpk}
            GROUP BY c{iseat}.id, ca{iseat}.id, pa{iseat}.id, pa{iseat}.code, pa{iseat}.title
            ORDER BY candidates{iseat} DESC'''

    try:
        cursor.execute(seats_query)
        rows = cursor.fetchall()
        for row in rows:
            party_seats = seats.get(row[party_pos], [])
            party_seats.append(dict(zip(seat_fields, row)))
            seats[row[party_pos]] = party_seats
    except Exception as e:
        print("There was an error running raw query", e)


    i = 0
    for column in columns:
        key = f'votes_{snakeify(column.title)}'
        sums += f' SUM(ncs{i}.total_votes) AS {key},'
        sum_joins += f''' LEFT JOIN (
                    SELECT
                            ncs{i}.id,
                            ncs{i}.total_votes
                        FROM {table} ncs{i}
                            LEFT JOIN poll_party p{i} ON p{i}.id = ncs{i}.party_id
                            LEFT JOIN geo_constituency c{i} ON c{i}.id = ncs{i}.constituency_id
                            LEFT JOIN geo_region r{i} ON r{i}.id = c{i}.region_id
                        WHERE
                            ncs{i}.zone_ct_id = {zone_ct_id}
                            AND ncs{i}.constituency_id = {column.pk}
                            AND r{i}.id = {rpk}
                        GROUP BY ncs{i}.id, ncs{i}.total_votes
                        ORDER BY ncs{i}.id ASC
                ) AS ncs{i} ON ncs{i}.id = ncs.id
        '''
        fields.append(key)
        i += 1

    query = f'''SELECT
            p.id, p.code,
            SUM(ncs.total_votes) votes,
            COUNT(summ.id) seats,
            {sums}
            '|' AS row_end
        FROM {table} ncs

            LEFT JOIN poll_party p ON p.id = ncs.party_id
            LEFT JOIN geo_constituency c ON c.id = ncs.constituency_id
            LEFT JOIN geo_region r ON r.id = c.region_id

            LEFT JOIN {summary_table} summ ON
                summ.constituency_id = c.id
                AND summ.constituency_id = ncs.constituency_id
                AND summ.candidate_id IN (
                    SELECT ca.id
                    FROM people_candidate ca
                    WHERE ca.party_id = p.id
                )

            {sum_joins}
        WHERE
            ncs.zone_ct_id = {zone_ct_id}
            AND r.id = {rpk}
        GROUP BY p.id
        ORDER BY p.code ASC;'''

    reports = []
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            reports.append(dict(zip(fields, row)))
    except Exception as e:
        print("There was an error running raw query", e)

    context = dict(
        title=report_title,
        level=level,
        columns=columns,
        reports=reports,
        seats=seats,
        zone=region,
        zone_type='region',
        sub_zone_type='constituency',
        sub_zone_type_plural='constituencies',
        super_zone=region.nation,
        super_zone_link='/reports/parliamentary/nation/',
        sub_zone_link='/reports/parliamentary/constituency/',
    )
    return render(request, template, context)

@login_required
def constituency_parliamentary_report_raw(request, cpk=None):
    template = f'report/parliamentary/constituency_report.html'
    report_title = f'Constituency Parliamentary Collation Results'
    level = GeoLevelChoices.CONSTITUENCY
    zone_ct = get_zone_ct(Constituency)
    zone_ct_id = ""
    if zone_ct is not None:
        zone_ct_id = zone_ct.pk
    constituency = Constituency.objects.filter(pk=cpk).first()
    columns = Station.objects.filter(constituency=constituency).order_by('code').all()
    cursor = connection.cursor()

    sums = ''
    sum_joins = ''
    table = 'poll_constituency_collation_sheet'
    summary_table = 'poll_parliamentary_summary_sheet'
    fields = [
        'party_id', 'party_code', 'votes', 'seats', 'max_votes'
    ]


    iseat = 'seat'
    # party_id is this position in the select field array (below)
    party_pos = 2
    seat_fields = [
        'constituency_id', 'constituency',
        'party_id', 'party_code', 'party_title',
        'candidate_id', 'candidates',
        'votes', 'seats',
    ]
    seats = dict()
    seats_query = f'''SELECT
                c{iseat}.id AS constituency_id,
                c{iseat}.title,
                pa{iseat}.id,
                pa{iseat}.code,
                pa{iseat}.title,
                ca{iseat}.id AS candidate_id,
                STRING_AGG(CONCAT(ca{iseat}.prefix, ' ', ca{iseat}.first_name, ' ', ca{iseat}.last_name), ', ') AS candidates{iseat},
                SUM(ssheet{iseat}.votes) AS votes,
                COUNT(ssheet{iseat}.id) AS seats
            FROM
                geo_constituency c{iseat}
                LEFT JOIN poll_parliamentary_summary_sheet ssheet{iseat} ON ssheet{iseat}.constituency_id = c{iseat}.id
                LEFT JOIN people_candidate ca{iseat} ON ca{iseat}.id = ssheet{iseat}.candidate_id
                LEFT JOIN poll_party pa{iseat} ON pa{iseat}.id = ca{iseat}.party_id
            WHERE
                c{iseat}.id = {cpk}
            GROUP BY c{iseat}.id, ca{iseat}.id, pa{iseat}.id, pa{iseat}.code, pa{iseat}.title
            ORDER BY candidates{iseat} DESC'''
    try:
        cursor.execute(seats_query)
        rows = cursor.fetchall()
        for row in rows:
            party_seats = seats.get(row[party_pos], [])
            party_seats.append(dict(zip(seat_fields, row)))
            seats[row[party_pos]] = party_seats
    except Exception as e:
        print("There was an error running raw query", e)

    imax = 'max'
    max_query = f'''SELECT
            SUM(ncs{imax}.total_votes) sum_votes
        FROM {table} ncs{imax}
            LEFT JOIN poll_party p{imax} ON p{imax}.id = ncs{imax}.party_id
            LEFT JOIN geo_station s{imax} ON s{imax}.id = ncs{imax}.station_id
            LEFT JOIN geo_constituency c{imax} ON c{imax}.id = s{imax}.constituency_id
            -- LEFT JOIN geo_region r ON r{imax}.id = c{imax}.region_id
        WHERE
            ncs{imax}.zone_ct_id = {zone_ct_id}
            AND c{imax}.id = {cpk}
        GROUP BY p{imax}.id'''
    max_votes = 0
    try:
        cursor.execute(max_query)
        rows = cursor.fetchall()
        max_votes = max(rows)[0]
    except Exception as e:
        print("There was an error running raw query", e)

    i = 0
    for column in columns:
        key = f'votes_{snakeify(column.title)}'
        sums += f' SUM(ncs{i}.total_votes) AS {key},'
        sum_joins += f''' LEFT JOIN (
                    SELECT
                            ncs{i}.id,
                            ncs{i}.total_votes
                        FROM {table} ncs{i}
                            LEFT JOIN poll_party p{i} ON p{i}.id = ncs{i}.party_id
                            LEFT JOIN geo_station s{i} ON s{i}.id = ncs{i}.station_id
                            LEFT JOIN geo_constituency c{i} ON c{i}.id = s{i}.constituency_id
                            LEFT JOIN geo_region r{i} ON r{i}.id = c{i}.region_id
                        WHERE
                            ncs{i}.zone_ct_id = {zone_ct_id}
                            AND ncs{i}.station_id = {column.pk}
                            AND c{i}.id = {cpk}
                        GROUP BY ncs{i}.id, ncs{i}.total_votes
                        ORDER BY ncs{i}.id ASC
                ) AS ncs{i} ON ncs{i}.id = ncs.id
        '''
        fields.append(key)
        i += 1

    query = f'''SELECT
        p.id, p.code,
        SUM(ncs.total_votes) AS votes,
        (CASE WHEN (SUM(ncs.total_votes) = {max_votes} AND SUM(ncs.total_votes) > 0) THEN 1 ELSE 0 END) seats,
        -- COUNT(summ.constituency_id) AS max_votes,
        -- COUNT(summ.seats) AS seats,
        '{max_votes}' AS max_votes,
        {sums}
        '|' AS row_end

        
    FROM {table} ncs
        LEFT JOIN poll_party p ON p.id = ncs.party_id
        LEFT JOIN geo_station s ON s.id = ncs.station_id
        LEFT JOIN geo_constituency c ON c.id = s.constituency_id
        LEFT JOIN geo_region r ON r.id = c.region_id
        -- LEFT JOIN people_candidate ca ON ca.party_id = p.id


        LEFT JOIN {summary_table} summ ON
            summ.constituency_id = {cpk}
            AND summ.constituency_id = c.id
            AND summ.constituency_id = s.constituency_id
            AND summ.candidate_id IN (
                SELECT ca.id
                    FROM people_candidate ca
                    WHERE ca.party_id = p.id
                        AND ca.party_id = ncs.party_id
            )

        {sum_joins}
    WHERE
        ncs.zone_ct_id = {zone_ct_id}
        AND c.id = {cpk}
    GROUP BY p.id
    ORDER BY p.code ASC;'''

    reports = []
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            reports.append(dict(zip(fields, row)))
    except Exception as e:
        print("There was an error running raw query", e)

    context = dict(
        title=report_title,
        level=level,
        columns=columns,
        reports=reports,
        seats=seats,
        zone=constituency,
        zone_type='constituency',
        sub_zone_type='station',
        sub_zone_type_plural='stations',
        super_zone=constituency.region,
        super_zone_link='/reports/parliamentary/region/',
        sub_zone_link='/reports/parliamentary/station/',
    )
    return render(request, template, context)

@login_required
def station_parliamentary_report_raw(request, spk=None):
    template = f'report/parliamentary/station_report.html'
    report_title = f'Station Parliamentary Collation Results'
    level = GeoLevelChoices.CONSTITUENCY
    zone_ct = get_zone_ct(Constituency)
    zone_ct_id = ""
    if zone_ct is not None:
        zone_ct_id = zone_ct.pk
    station = Station.objects.filter(pk=spk).first()
    columns = [] # Station.objects.filter(constituency=constituency).order_by('code').all()
    cursor = connection.cursor()

    sums = ''
    sum_joins = ''
    table = 'poll_station_collation_sheet'
    fields = [
        'party_id', 'party_code',
        'votes', 'max_votes', 'seats',
        'candidate_name',
    ]
    
    select_candidate_name = " CONCAT(ca.prefix, ' ', ca.first_name, ' ', ca.last_name) candidate_name,"
    group_candidate_name = ', ca.prefix, ca.first_name, ca.last_name'

    imax = 'max'
    max_query = f'''SELECT MAX(sums.votes) FROM (
        SELECT
            SUM(ncs{imax}.total_votes) AS votes
        FROM {table} ncs{imax}
            LEFT JOIN people_candidate c{imax} ON c{imax}.id = ncs{imax}.candidate_id
            LEFT JOIN poll_party p{imax} ON p{imax}.id = c{imax}.party_id
            LEFT JOIN geo_station s{imax} ON s{imax}.id = ncs{imax}.station_id
        WHERE
            ncs{imax}.zone_ct_id = {zone_ct_id}
            AND s{imax}.id = {station.pk}
        GROUP BY p{imax}.id
        ) AS sums'''
    max_votes = 0
    try:
        cursor.execute(max_query)
        rows = cursor.fetchall()
        max_votes = max(rows)[0]
    except Exception as e:
        print("There was an error running raw query", e)
    if max_votes is None:
        max_votes = 0


    i = 0
    for column in columns:
        key = f'votes_{snakeify(column.title)}'
        sums += f' SUM(ncs{i}.total_votes) AS {key},'
        sum_joins += f''' LEFT JOIN (
                    SELECT
                            ncs{i}.id,
                            ncs{i}.total_votes
                        FROM {table} ncs{i}
                            LEFT JOIN poll_party p{i} ON p{i}.id = ncs{i}.party_id
                            LEFT JOIN geo_station s{i} ON s{i}.id = ncs{i}.station_id
                            LEFT JOIN geo_constituency c{i} ON c{i}.id = s{i}.constituency_id
                            LEFT JOIN geo_region r{i} ON r{i}.id = c{i}.region_id
                        WHERE
                            ncs{i}.zone_ct_id = {zone_ct_id}
                            AND ncs{i}.station_id = {column.pk}
                            AND c{i}.id = {cpk}
                        GROUP BY ncs{i}.id, ncs{i}.total_votes
                        ORDER BY ncs{i}.id ASC
                ) AS ncs{i} ON ncs{i}.id = ncs.id
        '''
        fields.append(key)
        i += 1

    query = f'''SELECT
        p.id, p.code,
        SUM(ncs.total_votes) votes,
        {max_votes} max_votes,
        (CASE WHEN (SUM(ncs.total_votes) > 0 AND SUM(ncs.total_votes) = {max_votes}) THEN 1 ELSE 0 END) seats,
        {select_candidate_name}
        {sums}
        '|' AS row_end
    FROM {table} ncs
        LEFT JOIN people_candidate ca ON ca.id = ncs.candidate_id
        LEFT JOIN poll_party p ON p.id = ca.party_id
        LEFT JOIN geo_station s ON s.id = ncs.station_id
        LEFT JOIN geo_constituency c ON c.id = s.constituency_id
        LEFT JOIN geo_region r ON r.id = c.region_id
        {sum_joins}
    WHERE
        ncs.zone_ct_id = {zone_ct_id}
        AND s.id = {spk}
    GROUP BY p.id
        {group_candidate_name}
    ORDER BY p.code ASC;'''

    reports = []
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            reports.append(dict(zip(fields, row)))
    except Exception as e:
        print("There was an error running raw query", e)

    context = dict(
        title=report_title,
        level=level,
        columns=columns,
        reports=reports,
        zone=station,
        zone_type='station',
        sub_zone_type=None,
        super_zone=station.constituency,
        super_zone_link='/reports/parliamentary/constituency/',
        sub_zone_link='#',
    )
    return render(request, template, context)



@login_required
def dashboard(request, context_only=False):
    title='Dashboard'
    template = f'report/charts/dashboard.html'

    api_base_url = 'https://' if request.is_secure else 'http://'
    api_base_url += request.get_host() + '/'

    # print([k for k, v in vars(request).items()])
    # blue #0d6efd
    # indigo #6610f2
    # purple #6f42c1
    # pink #d63384
    # red #dc3545
    # orange #fd7e14
    # yellow #ffc107
    # green #198754
    # teal #20c997
    # cyan #0dcaf0
    # #696969 #808080 #A9A9A9 #C0C0C0 #D3D3D3


    pie = dict(labels=[], data=[], title='Total Votes',
            color='#0dcaf0',
            colors=['#0d6efd', '#6610f2', '#6f42c1', '#d63384', '#dc3545', '#fd7e14', '#ffc107', '#198754', '#20c997', '#0dcaf0'],)
    vote_validity = dict(title='Vote Validity',
                    labels=['Valid', 'Invalid'],
                    data=[], 
                    color='#20c997',
                    colors=['#20c997', '#D3D3D3',],
                    )
    ec_variance = dict(title='EC Variance',
                    labels=['Total Valid', 'Total from EC'],
                    data=[], 
                    color='#dc3545',
                    colors=['#20c997','#0dcaf0',],
                    )

    regional_counts = dict(title='Regional Counts',
                            labels=['Presidential', 'Parliamentary'],
                            data=[], 
                            color='#0dcaf0',
                            colors=['#0dcaf0', '#D3D3D3',],
                        )

    bar = dict(labels=[], data=[], title='Total Votes', color='#20c997',
            colors=['#0d6efd', '#6610f2', '#6f42c1', '#d63384', '#dc3545', '#fd7e14', '#ffc107', '#198754', '#20c997', '#0dcaf0'],)

    station_total_votes=dict(labels=[], data=[],
                        title='Total Votes',
                        color='#20c997',
                        colors=['#0d6efd', '#6610f2', '#6f42c1', '#d63384', '#dc3545', '#fd7e14', '#ffc107', '#198754', '#20c997', '#0dcaf0'],)
    station_parliametary_votes=dict(labels=[], data=[],
                            title='Parliamentary Votes',
                            color='#0dcaf0',
                            colors=['#0d6efd', '#6610f2', '#6f42c1', '#d63384', '#dc3545', '#fd7e14', '#ffc107', '#198754', '#20c997', '#0dcaf0'],)
    station_presidential_votes=dict(labels=[], data=[],
                            title='Presidential Votes',
                            color='#D3D3D3',
                            colors=['#0d6efd', '#6610f2', '#6f42c1', '#d63384', '#dc3545', '#fd7e14', '#ffc107', '#198754', '#20c997', '#0dcaf0'],)

    party_total_votes = dict(labels=[], data=[],
                        title='Total Votes',
                        color='#dc3545',
                        colors=['#0d6efd', '#6610f2', '#6f42c1', '#d63384', '#dc3545', '#fd7e14', '#ffc107', '#198754', '#20c997', '#0dcaf0'],)
    party_parliametary_votes = dict(labels=[], data=[],
                            title='Parliamentary Votes',
                            color='#fd7e14',
                            colors=['#0d6efd', '#6610f2', '#6f42c1', '#d63384', '#dc3545', '#fd7e14', '#ffc107', '#198754', '#20c997', '#0dcaf0'],)
    party_presidential_votes = dict(labels=[], data=[],
                            title='Presidential Votes',
                            color='#ffc107',
                            colors=['#0d6efd', '#6610f2', '#6f42c1', '#d63384', '#dc3545', '#fd7e14', '#ffc107', '#198754', '#20c997', '#0dcaf0'],)

    presidential_candidates = dict(labels=[], data=[],
                        title='Presidential Candidates',
                        color='#20c997',
                        colors=['#0d6efd', '#6610f2', '#6f42c1', '#d63384', '#dc3545', '#fd7e14', '#ffc107', '#198754', '#20c997', '#0dcaf0'],)

    parliamentary_candidates = dict(labels=[], data=[],
                        title='Parliamentary Candidates',
                        color='#20c997',
                        colors=['#0d6efd', '#6610f2', '#6f42c1', '#d63384', '#dc3545', '#fd7e14', '#ffc107', '#198754', '#20c997', '#0dcaf0'],)


    foo = 'foo'
    if foo == 'bar':

        nation_ct = get_zone_ct(Nation)
        constituency_ct = get_zone_ct(Constituency)

        # pie
        queryset = Result.objects.order_by('-votes')[:5]
        for result in queryset:
            pie['labels'].append(result.station.code)
            pie['data'].append(result.votes)


        # vote_validity
        sheets = SupernationalCollationSheet.objects.order_by('-total_votes')
        total_valid = 0
        total_invalid = 0

        if sheets is not None and len(sheets) > 0:
            if sheets[0] is not None:
                if sheets[0].total_invalid_votes is not None:
                    total_invalid += sheets[0].total_invalid_votes
            for sheet in sheets:
                total_valid += 0 if sheet.total_votes is None else sheet.total_votes

        vote_validity['data'] = [total_valid, total_invalid]
        vote_validity['labels'] = [
            'Valid ({} votes)'.format(vote_validity['data'][0]),
            'Invalid ({} votes)'.format(vote_validity['data'][1]),
        ]


        # ec_variance
        sheets = SupernationalCollationSheet.objects.order_by('-total_votes')
        total_valid = 0
        total_ec = 0
        for sheet in sheets:
            total_valid += 0 if sheet.total_votes is None else sheet.total_votes
            total_ec += 0 if sheet.total_votes_ec is None else sheet.total_votes_ec
        ec_variance['data'] = [total_valid, total_ec]


        # regional_counts
        sheets = SupernationalCollationSheet.objects.order_by('-total_votes')
        total_presidential = 0
        total_parliamentary = 0
        for sheet in sheets:
            if sheet.zone_ct == get_zone_ct(Nation):
                total_presidential += 0 if sheet.total_votes is None else sheet.total_votes
            elif sheet.zone_ct == get_zone_ct(Constituency):
                total_parliamentary += 0 if sheet.total_votes is None else sheet.total_votes
        regional_counts['data'] = [total_presidential, total_parliamentary]
        regional_counts['labels'] = [
            'Presidential ({} votes)'.format(regional_counts['data'][0]),
            'Parliamentary ({} votes)'.format(regional_counts['data'][1]),
        ]


        # bar
        queryset = Result.objects \
                        .values('station__code') \
                        .annotate(station_votes=Sum('votes'))[:10]
                        #  \
                        # .order_by('-station_votes') \
        for entry in queryset:
            bar['labels'].append(entry['station__code'])
            bar['data'].append(entry['station_votes'])


        # station_total_votes, station_parliametary_votes, station_presidential_votes
        cursor = connection.cursor()
        fields = [
            'station_id', 'station_code', 'station_title',
            'total_votes',
        ]
        reports = []
        col_table = 'poll_constituency_collation_sheet'
        query = f'''SELECT
                        s.id, s.code, s.title,
                        SUM(c.total_votes) AS votes
                    FROM
                        geo_station AS s
                        INNER JOIN {col_table} AS c ON c.station_id = s.id
                    GROUP BY s.id
                    ORDER BY votes DESC
                    LIMIT 10 OFFSET 0;'''
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            for row in rows:
                row = dict(zip(fields, row))
                if row['total_votes'] is not None:
                    reports.append(row)
        except Exception as e:
            print("There was an error running raw query", e)

        for report in reports:
            station_id = report['station_id']
            
            pre_sheets = ConstituencyCollationSheet.objects \
                                        .filter(
                                            station_id=station_id,
                                            zone_ct=nation_ct
                                        ).values('total_votes')
            par_sheets = ConstituencyCollationSheet.objects \
                                        .filter(
                                            station_id=station_id,
                                            zone_ct=constituency_ct
                                        ).values('total_votes')
            
            label = report['station_code']
            total_count = int(report['total_votes']) if report['total_votes'] is not None else 0
            
            par_count = 0
            for sheet in pre_sheets:
                if sheet is not None:
                    if sheet.get('total_votes', 0) > 0:
                        par_count += sheet.get('total_votes', 0)

            pre_count = 0
            for sheet in par_sheets:
                if sheet is not None:
                    if sheet.get('total_votes', 0) > 0:
                        pre_count += sheet.get('total_votes', 0)

            station_total_votes['labels'].append(label)
            station_presidential_votes['labels'].append(label)
            station_parliametary_votes['labels'].append(label)

            station_total_votes['data'].append(total_count)
            station_presidential_votes['data'].append(par_count)
            station_parliametary_votes['data'].append(pre_count)


        # party_total_votes, party_parliametary_votes, party_presidential_votes
        qs = Party.objects.all()
        for party in qs:
            party_total_votes['labels'].append(party.code)
            party_total_votes['data'].append(party.result_votes)
            party_parliametary_votes['labels'].append(party.code)
            party_parliametary_votes['data'].append(party.total_parliamentary_votes)
            party_presidential_votes['labels'].append(party.code)
            party_presidential_votes['data'].append(party.total_presidential_votes)


        # presidential_candidates
        candidates = Candidate.objects \
                            .filter(
                                position__in=Position.objects \
                                    .filter(zone_ct=nation_ct) \
                                    .all()
                            ).all()
        charts = dict()
        for candidate in candidates:
            if candidate.total_votes > 0:
                label = f'{candidate.first_name[0]}.  {candidate.last_name} ({candidate.party.code})'
                value = candidate.total_votes
                charts[label] = value
        charts = {k: v for k, v in sorted(charts.items(), key=lambda item: item[1], reverse=True)}
        for label, value in charts.items():
            presidential_candidates['labels'].append(label)
            presidential_candidates['data'].append(value)


        # parliamentary_candidates
        candidates = StationCollationSheet.objects \
                                        .filter(
                                            candidate__position__in=Position.objects \
                                                .filter(zone_ct=constituency_ct) \
                                                .all()
                                        ) \
                                        .values('candidate', 'candidate__prefix', 'candidate__first_name', 'candidate__last_name', 'candidate__party__code', 'candidate__party__title') \
                                        .annotate(candidate_count=Count('total_votes')) \
                                        .annotate(total_votes=Sum('total_votes')) \
                                        .order_by('-total_votes')[:10]
        charts = dict()
        for candidate in candidates:
            if candidate.get('total_votes', 0) > 0:
                first_name = candidate.get('candidate__first_name', '')
                last_name = candidate.get('candidate__last_name', '')
                party_code = candidate.get('candidate__party__code', '')
                label = f'{first_name[0]}.  {last_name} ({party_code})'
                value = candidate.get('total_votes', 0)
                charts[label] = value
        charts = {k: v for k, v in sorted(charts.items(), key=lambda item: item[1], reverse=True)}
        for label, value in charts.items():
            parliamentary_candidates['labels'].append(label)
            parliamentary_candidates['data'].append(value)


    context = dict(
        api_base_url=api_base_url,
        title=title,
        pie=pie,
        vote_validity=vote_validity,
        ec_variance=ec_variance,
        regional_counts=regional_counts,
        bar=bar,

        party_total_votes=party_total_votes,
        party_parliametary_votes=party_parliametary_votes,
        party_presidential_votes=party_presidential_votes,

        station_total_votes=station_total_votes,
        station_parliametary_votes=station_parliametary_votes,
        station_presidential_votes=station_presidential_votes,

        presidential_candidates=presidential_candidates,
        parliamentary_candidates=parliamentary_candidates,
    )

    # if context_only:
    #     return context

    return render(request, template, context)

@login_required
def dash_map(request):
    template = 'report/charts/map.html'
    context = {}
    return render(request, template, context)


@login_required
def bar(request):
    labels = []
    data = []

    queryset = Result.objects \
                    .values('station__code') \
                    .annotate(station_votes=Sum('votes')) \
                    .order_by('-station_votes')
    for entry in queryset:
        labels.append(entry['station__code'])
        data.append(entry['station_votes'])
    
    return JsonResponse(data={
        'labels': labels,
        'data': data,
    })


import json
import redis
from datetime import datetime
import django_rq
from django.urls import reverse
from django.conf import settings
from django.db import connection
from django.contrib.auth.decorators import login_required
from rq.job import Job, JobStatus, cancel_job, get_current_job
from rest_framework.decorators import api_view
from rest_framework.response import Response
from __report.tasks import collation_task, clear_collation_task
from django.shortcuts import render, redirect
from __poll.utils.utils import get_zone_ct, trim_vote_count, make_title_key
from __geo.models import Nation, Region , Constituency, Station
from __people.models import Party, Agent, Candidate 
from __poll.models import (
    Position, Result, ResultSheet, ResultSheetApproval,
    StationCollationSheet, ConstituencyCollationSheet,
    RegionalCollationSheet, NationalCollationSheet,
    SupernationalCollationSheet, ParliamentarySummarySheet
)
from django.db.models import (
    Q, Prefetch, Sum, Count, Max,
    F, Value, Func, Subquery, OuterRef, IntegerField, CharField, Case, When,
)
from django.db.models.functions import Concat
from django.http import JsonResponse
from django.apps import apps



# Connect to our Redis instance
REDIS_INSTANCE = redis.StrictRedis(host=settings.REDIS_HOST,
                                   port=settings.REDIS_PORT,
                                   db=settings.REDIS_DB)



def extract_all_values():
    keys = REDIS_INSTANCE.scan_iter('*')
    vals = []
    for key in keys:
        typeof = REDIS_INSTANCE.type(key)
        if typeof == "string":
            vals = [REDIS_INSTANCE.get(key)]
        if typeof == "hash":
            vals = REDIS_INSTANCE.hgetall(key)
        if typeof == "zset":
            vals = REDIS_INSTANCE.zrange(key, 0, -1)
        if typeof == "list":
            vals = REDIS_INSTANCE.lrange(key, 0, -1)
        if typeof == "set":
            vals = REDIS_INSTANCE.smembers(key)
    return vals


def extract_redis_value(REDIS_INSTANCE, redis_key):
    '''Extract the correct type of data based on the data type'''
    # https://stackoverflow.com/questions/37953019/wrongtype-operation-against-a-key-holding-the-wrong-kind-of-value-php
    redis_value = None
 
    # if not REDIS_INSTANCE:
    typeof = REDIS_INSTANCE.type(redis_key) # type(key)
    if typeof in [b'bytes', b'stream']:
        # redis_value = REDIS_INSTANCE.xread(redis_key.decode("utf-8"))
        pass
    elif typeof == b'string':
        redis_value = REDIS_INSTANCE.get(redis_key.decode("utf-8"))
    elif typeof == b'hash':
        redis_value = REDIS_INSTANCE.hgetall(redis_key.decode("utf-8")) # HGET or HMGET or HGETALL
    elif typeof == b'set':
        redis_value = REDIS_INSTANCE.smembers(redis_key.decode("utf-8"))
    elif typeof == b'zset':
        redis_value = REDIS_INSTANCE.zrange(redis_key.decode("utf-8"), 0, -1)
    elif typeof == b'list':
        redis_value = REDIS_INSTANCE.lrange(redis_key.decode("utf-8"), 0, -1)
    return redis_value



@api_view(['GET'])
def clear_collation(request):
    queue = django_rq.get_queue('default')
    job = queue.enqueue(clear_collation_task)
    job_key = job.key.decode("utf-8")
    response = dict(
        status=201,
        message='Currently processing.',
        job=job_key,
    )
    return redirect(reverse('dequeue', kwargs=dict(jid=job_key)), response, 201)


@api_view(['GET'])
def enqueue_collation(request):
    queue = django_rq.get_queue(
        'default',
        default_timeout=3600
    )
    started = datetime.now()
    context = dict(
        started=started,
    )
    job = queue.enqueue(collation_task, context=context)
    job_key = job.key.decode("utf-8")
    response = dict(
        status=201,
        started=started,
        message='Currently processing.',
        job=job_key,
    )
    return redirect(reverse('dequeue', kwargs=dict(jid=job_key)), response, 201)


@api_view(['GET'])
def dequeue_collation(request, jid=None):
    # job_id = job # request.GET.get('job_id')
    redis_conn = django_rq.get_connection()
    job_id=jid.split(':')[2] 

    job = None
    try:
        # fetch Job from redis
        job = Job.fetch(job_id, redis_conn)
    except Exception as e: # NoSuchJobError
        # logger.info(job_id)
        print(e)
    return_url = request.build_absolute_uri(reverse('enqueue'))
    stopped = datetime.now()
    if job is not None:
        if job.is_finished:
            # message=job.return_value
            response = dict(message='job completed',
                            job_key=jid,
                            return_path=return_url,
                            status=201,
                            # started=started,
                            stooped=stopped,
                            )
        elif job.is_queued:
            response = dict(message='job currently in queue',
                            job_key=jid,
                            return_path=return_url,
                            status=102,
                            )
        elif job.is_started:
            response = dict(message='job still waiting',
                            job_key=jid,
                            return_path=return_url,
                            status=100,
                            )
        elif job.is_failed:
            response = dict(message='job has failed',
                            job_key=jid,
                            return_path=return_url,
                            status=500,
                            stooped=stopped,
                            )
    else:
        response = dict(message='job not found',
                        job_key=jid,
                        return_path=return_url,
                        status=404,
                        )
    return Response(response, 201)


@api_view(['GET', 'POST'])
def manage_items(request, *args, **kwargs):
    if request.method == 'GET':
        items = {}
        count = 0
        for key in REDIS_INSTANCE.keys("*"):
            key_value = key.decode("utf-8")
            redis_value = extract_redis_value(REDIS_INSTANCE, key)
            # if redis_value is not None and type(key) == str: # in [str, int, float, bool]:
            if redis_value is not None \
                and ':' not in key_value:
                items[key_value] = redis_value
                count += 1
        response = dict(
            count=count,
            msg=f"Found {count} items.",
            items=items
        )
        return Response(response, status=200)
    elif request.method == 'POST':
        item = json.loads(request.body)
        key = list(item.keys())[0]
        value = item[key]
        REDIS_INSTANCE.set(key, value)
        response = dict(
            msg=f"{key} successfully set to {value}"
        )
        return Response(response, 201)


@api_view(['GET', 'PUT', 'DELETE'])
def manage_item(request, *args, **kwargs):
    if request.method == 'GET':
        if kwargs['key']:
            value = extract_redis_value(REDIS_INSTANCE, kwargs['key'])
            if value:
                response = {
                    'key': kwargs['key'],
                    'value': value,
                    'msg': 'success'
                }
                return Response(response, status=200)
            else:
                response = dict(
                    key=kwargs['key'],
                    value=None,
                    msg='Not found'
                )
                return Response(response, status=404)
    elif request.method == 'PUT':
        if kwargs['key']:
            request_data = json.loads(request.body)
            new_value = request_data['new_value']
            value = extract_redis_value(REDIS_INSTANCE, kwargs['key'])
            if value:
                REDIS_INSTANCE.set(kwargs['key'], new_value)
                response = dict(
                    key=kwargs['key'],
                    value=value,
                    msg=f"Successfully updated {kwargs['key']}"
                )
                return Response(response, status=200)
            else:
                response = dict(
                    key=kwargs['key'],
                    value=None,
                    msg='Not found'
                )
                return Response(response, status=404)

    elif request.method == 'DELETE':
        if kwargs['key']:
            result = REDIS_INSTANCE.delete(kwargs['key'])
            if result == 1:
                response = dict(
                    msg=f"{kwargs['key']} successfully deleted"
                )
                return Response(response, status=404)
            else:
                response = dict(
                    key=kwargs['key'],
                    value=None,
                    msg='Not found'
                )
                return Response(response, status=404)


@api_view(['GET', 'POST'])
def demo_dash(request, *args, **kwargs):
    if request.is_ajax():
        data = dict(
            message="...",
            staus=200
        )
    else:
        data = dict(
            message="Data not found",
            staus=404
        )
    return JsonResponse(data)

@login_required
@api_view(['GET', 'POST'])
def dashboard(request, *args, **kwargs):
    title='Dashboard'
    template = f'report/charts/dashboard.html'

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

    COLOR_COMB = [
        # '#0d6efd',
        'rgba(13, 110, 253, 1)',
        'rgba(13, 110, 253, .75)',
        'rgba(13, 110, 253, .5)',
        'rgba(13, 110, 253, .25)',
        # '#6610f2',
        'rgba(102, 16, 242, 1)',
        'rgba(102, 16, 242, .75)',
        'rgba(102, 16, 242, .5)',
        'rgba(102, 16, 242, .25)',
        # '#6f42c1',
        'rgba(111, 66, 193, 1)',
        'rgba(111, 66, 193, .75)',
        'rgba(111, 66, 193, .5)',
        'rgba(111, 66, 193, .25)',
        # '#d63384',
        'rgba(214, 51, 132, 1)',
        'rgba(214, 51, 132, .75)',
        'rgba(214, 51, 132, .5)',
        'rgba(214, 51, 132, .25)',
        # '#dc3545',
        'rgba(220, 53, 69, 1)',
        'rgba(220, 53, 69, .75)',
        'rgba(220, 53, 69, .5)',
        'rgba(220, 53, 69, .25)',
        # '#fd7e14',
        'rgba(253, 126, 20, 1)',
        'rgba(253, 126, 20, .75)',
        'rgba(253, 126, 20, .5)',
        'rgba(253, 126, 20, .25)',
        # '#ffc107',
        'rgba(255, 193, 7, 1)',
        'rgba(255, 193, 7, .75)',
        'rgba(255, 193, 7, .5)',
        'rgba(255, 193, 7, .25)',
        # '#198754',
        'rgba(25, 135, 84, 1)',
        'rgba(25, 135, 84, .75)',
        'rgba(25, 135, 84, .5)',
        'rgba(25, 135, 84, .25)',
        # '#20c997',
        'rgba(32, 201, 151, 1.0)',
        'rgba(32, 201, 151, 0.75)',
        'rgba(32, 201, 151, 0.5)',
        'rgba(32, 201, 151, 0.25)',
        # '#0dcaf0'
        'rgba(13, 202, 240, 1)',
        'rgba(13, 202, 240, .75)',
        'rgba(13, 202, 240, .5)',
        'rgba(13, 202, 240, .25)',
    ]

    nation_ct = get_zone_ct(Nation)
    constituency_ct = get_zone_ct(Constituency)




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

    regional_counts = dict(title='Votes by Region',
                            labels=[],
                            data=[], 
                            color='#0dcaf0',
                            colors=['#0dcaf0', '#D3D3D3',],
                        )

    constituency_counts = dict(title='Votes by Constituency',
                            labels=[],
                            data=[], 
                            color='#0dcaf0',
                            colors=['#0dcaf0', '#D3D3D3',],
                        )

    station_counts = dict(title='Votes by Station',
                            labels=[],
                            data=[], 
                            color='#0dcaf0',
                            colors=['#0dcaf0', '#D3D3D3',],
                        )
    
    votes_by_office = dict(title='Votes by Position',
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
                        colors=[
                            '#0d6efd',
                            # '#6610f2',
                            'rgba(102, 16, 242, 1)',
                            'rgba(102, 16, 242, .75)',
                            'rgba(102, 16, 242, .5)',
                            '#6f42c1',
                            '#d63384',
                            '#dc3545',
                            '#fd7e14',
                            '#ffc107',
                            # '#198754',
                            'rgba(25, 135, 84, 1)',
                            'rgba(25, 135, 84, .75)',
                            'rgba(25, 135, 84, .5)',
                            # '#20c997',
                            'rgba(32, 201, 151, 1.0)',
                            'rgba(32, 201, 151, 0.75)',
                            'rgba(32, 201, 151, 0.5)',
                            '#0dcaf0'
                        ],
                    )
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

    parliamentary_votes_by_party = dict(labels=[], data=[],
                        title='Parliamentary Votes by Party',
                        color='#20c997',
                        colors=['#0d6efd', '#6610f2', '#6f42c1', '#d63384', '#dc3545', '#fd7e14', '#ffc107', '#198754', '#20c997', '#0dcaf0'],)

    presidential_top = dict(labels=[], data=[],
                        title='Presidential Candidates',
                        color='#20c997',
                        colors=['#0d6efd', '#6610f2', '#6f42c1', '#d63384', '#dc3545', '#fd7e14', '#ffc107', '#198754', '#20c997', '#0dcaf0'],)

    parliamentary_top = dict(labels=[], data=[],
                        list=[],
                        title='Party Seats',
                        color='#20c997',
                        colors=[
                                '#0dcaf0'
                                'rgba(32, 201, 151, 0.5)',
                                'rgba(32, 201, 151, 0.75)',
                                'rgba(32, 201, 151, 1.0)',
                                # '#20c997',
                                'rgba(25, 135, 84, .5)',
                                'rgba(25, 135, 84, .75)',
                                'rgba(25, 135, 84, 1)',
                                # '#198754',
                                '#ffc107',
                                '#fd7e14',
                                '#dc3545',
                                '#d63384',
                                '#6f42c1',
                                'rgba(102, 16, 242, .5)',
                                'rgba(102, 16, 242, .75)',
                                'rgba(102, 16, 242, 1)',
                                # '#6610f2',
                                '#0d6efd',
                            ],
                        )

    polling_station_counts = dict(labels=[], data=[],
                        list=[],
                        title='Seat Counts',
                        color='#20c997',
                        colors=['#0d6efd', '#6610f2', '#6f42c1', '#d63384', '#dc3545', '#fd7e14', '#ffc107', '#198754', '#20c997', '#0dcaf0'],)

    seat_counts = dict(labels=[], data=[],
                        list=[],
                        title='Seat Counts',
                        color='#20c997',
                        colors=['#0d6efd', '#6610f2', '#6f42c1', '#d63384', '#dc3545', '#fd7e14', '#ffc107', '#198754', '#20c997', '#0dcaf0'],)


    # presidential_top
    '''
    presidential_top['list'] = [
        dict(name='Michael Esheh',
            photo='https://i.pinimg.com/736x/93/86/23/9386236e5137cc8f89bcb98ab92334b9.jpg',
            position='President',
            party='NDP',
            vote_percentage=52,
            votes=8372332,
            votes_display=''),
        dict(name='Bradley Davis Omi',
            photo='http://africanarguments.org/wp-content/uploads/2012/01/SAraia-Headshot.jpg',
            position='President',
            party='GCC',
            vote_percentage=38,
            votes=3453742,
            votes_display=''),
        dict(name='Abel Glenwood',
            photo='https://i.pinimg.com/originals/5c/20/39/5c203980b5c8302ace93a710761c84d1.png',
            position='President',
            party='ARC',
            vote_percentage=4,
            votes=238632,
            votes_display=''),
    ]
    '''
    chart_candidates = Candidate \
                        .objects \
                        .filter(
                            position__in=Position
                                            .objects
                                            .filter(
                                                zone_ct=get_zone_ct(Nation)
                                            ).all()
                        ).values(
                            'id',
                            'first_name', 'last_name', 'other_names', 'photo',
                            'party__code', 'party__title',
                        )
    total_votes = 0
    for candidate in chart_candidates:
        candidate['votes'] = Result.objects.filter(candidate=candidate['id']).aggregate(Sum('votes'))['votes__sum']
        candidate['votes_display'] = trim_vote_count(candidate['votes'])
        candidate['party'] = candidate['party__code']
        del candidate['party__code']
        candidate['position'] = 'President'
        candidate['name'] = '{} {} {}'.format(candidate['first_name'], candidate['other_names'], candidate['last_name'])
        candidate['short_name'] = '{} {}'.format(candidate['last_name'], candidate['party'])
        total_votes += int(candidate['votes'])
    chart_candidates = sorted(list(chart_candidates),
                              key=lambda candidate: candidate['votes'],
                              reverse=True)
    presidential_top['list'] = chart_candidates
    i = 0
    for item in presidential_top['list']:
        if total_votes > 0:
            presidential_top['list'][i]['vote_percentage'] = round(100 * int(candidate['votes']) / total_votes, 2)
        presidential_top['labels'].append('{}'.format(item['short_name']))
        presidential_top['data'].append(item['votes'])
        i += 1


    # parliamentary_top
    '''
    parliamentary_top['list'] = [
        dict(name='Koko Sim',
            photo='https://www.imagefitz.com/wp-content/uploads/2019/02/Professional-Headshot-Photography-1JF1398-Square.jpg',
            position='Rep. NEW EDUBIASE',
            party='NDP',
            votes=443473,
            vote_percentage=48,
            votes_display=''),
        dict(name='Racheal Gosim',
            photo='https://i0.wp.com/www.mlobiondo.com/wp-content/uploads/2015/08/chamber.jpg?fit=705%2C705&ssl=1',
            position='Rep. OBUASI WEST',
            party='NDP',
            vote_percentage=30,
            votes=323742,
            votes_display=''),
        dict(name='Mai Lui',
            photo='https://www.epicscotland.com/wp-content/uploads/2015/08/Business-Headshot_005.jpg',
            position='Rep. ATWIMA NWABIAGYA SOUTH',
            party='NDP',
            vote_percentage=18,
            votes=223764,
            votes_display=''),
    ]
    '''
    seat_sheets = ParliamentarySummarySheet.objects \
                                            .values('candidate__party__id',
                                                    'candidate__party__code',
                                                    'candidate__party__title',
                                                    'votes', 'total_votes')
    seat_collations = {}
    for sheet in seat_sheets:
        key = make_title_key(sheet['candidate__party__id'])
        collation = seat_collations.get(key, dict(
                                            party_id=sheet['candidate__party__id'],
                                            party_code=sheet['candidate__party__code'],
                                            party_title=sheet['candidate__party__title'],
                                            seats=0,
                                            votes=0,
                                            total_votes=0,
                                            vote_percentage=0,
                                        ))
        collation['seats'] += 1
        collation['votes'] = sheet['votes']
        collation['total_votes'] = sheet['total_votes']
        collation['party_seat_url'] = reverse('parliamentary_seat_report')
        if int(sheet['total_votes']) > 0:
            collation['vote_percentage'] = round((100 * int(sheet['votes']) / int(sheet['total_votes'])), 1)
        seat_collations[key] = collation
    seat_collations = list(seat_collations.values())
    i = 0
    parliamentary_top['list'] = sorted(seat_collations, key=lambda sheet : sheet['seats'], reverse=True)
    for item in parliamentary_top['list']:
        parliamentary_top['labels'].append(item['party_code'])
        parliamentary_top['data'].append(item['seats'])
        # parliamentary_votes_by_party
        parliamentary_votes_by_party['labels'].append(item['party_code'])
        parliamentary_votes_by_party['data'].append(item['votes'])
        i += 1



    # polling_station_counts
    all_polling_stations = Station.objects.values('pk')
    declared_polling_stations = Result.objects \
                                        .values('station_id').distinct()
                                    # .filter(
                                        # station_id__in=len(all_polling_stations.values())
                                    # )
    outstanding_polling_stations = all_polling_stations.count() - declared_polling_stations.count()
    polling_station_counts['list'] = [
        dict( title='outstanding', seats=outstanding_polling_stations ),
        dict( title='declared', seats=declared_polling_stations.count() ),
    ]
    for item in polling_station_counts['list']:
        polling_station_counts['labels'].append(item['title'])
        polling_station_counts['data'].append(item['seats'])


    # seat_counts
    seats_declared = ParliamentarySummarySheet.objects.count()
    seats_total = Constituency.objects.count()
    seats_outstanding = seats_total - seats_declared
    seats_won = ParliamentarySummarySheet.objects \
                    .filter(
                            candidate__in=Candidate.objects
                                                .filter(
                                                        party=Party
                                                                .objects
                                                                .filter(code='NDP').first()
                                                ).all()
                    ).all().count()
    seat_counts['list'] = [
        dict( title='won', seats=seats_won ),
        dict( title='outstanding', seats=seats_outstanding ),
        dict( title='declared', seats=seats_declared ),
    ]
    for item in seat_counts['list']:
        seat_counts['labels'].append(item['title'])
        seat_counts['data'].append(item['seats'])


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


    # constituency_counts
    constituency_collations = {}
    sheets = RegionalCollationSheet.objects \
                            .values('constituency__id', 'constituency__title', 'total_votes', 'zone_ct_id') \
                            .order_by('-total_votes')
    for sheet in sheets:
        sheet_total_votes = int(sheet.get('total_votes', 0))
        key = make_title_key(sheet['constituency__id'])
        collation = constituency_collations.get(key, dict(
                                                        label=sheet['constituency__title'],
                                                        value=0,
                                                    ))
        collation['value'] += sheet_total_votes
        constituency_collations[key] = collation
    constituency_counts['colors'] = []
    i = 0
    for collation in constituency_collations.values():
        if i > len(COLOR_COMB) - 1:
            break
        if collation.get('label', None) is not None \
            and collation.get('value', None) is not None:
            constituency_counts['labels'].append(collation['label'])
            constituency_counts['data'].append(collation['value'])
            constituency_counts['colors'].append(COLOR_COMB[i])
            i += 1


    # station_counts
    station_collations = {}
    sheets = ConstituencyCollationSheet.objects \
                            .values('station__id', 'station__code', 'station__title', 'total_votes', 'zone_ct_id') \
                            .order_by('-total_votes')
    for sheet in sheets:
        sheet_total_votes = int(sheet.get('total_votes', 0))
        key = make_title_key(sheet['station__id'])
        collation = station_collations.get(key, dict(
                                                        label=sheet['station__code'],
                                                        value=0,
                                                    ))
        collation['value'] += sheet_total_votes
        station_collations[key] = collation
    station_counts['colors'] = []
    i = 0
    for collation in station_collations.values():
        if i > len(COLOR_COMB) - 1:
            break
        if collation.get('label', None) is not None \
            and collation.get('value', None) is not None:
            station_counts['labels'].append(collation['label'])
            station_counts['data'].append(collation['value'])
            station_counts['colors'].append(COLOR_COMB[i])
            i += 1


    # regional_counts
    # votes_by_office
    sheets = NationalCollationSheet.objects \
                            .values('region__id', 'region__title', 'total_votes', 'zone_ct_id') \
                            .order_by('-total_votes')
    total_presidential = 0
    total_parliamentary = 0
    regional_collations = {}
    for sheet in sheets:
        sheet_total_votes = int(sheet.get('total_votes', 0))

        key = make_title_key(sheet['region__id'])
        collation = regional_collations.get(key, dict(
                                                        label=sheet['region__title'],
                                                        value=0,
                                                    ))
        collation['value'] += sheet_total_votes
        regional_collations[key] = collation

        if sheet_total_votes > 0:
            if sheet['zone_ct_id'] == get_zone_ct(Nation).pk:
                total_presidential += sheet_total_votes
            elif sheet['zone_ct_id'] == get_zone_ct(Constituency).pk:
                total_parliamentary += sheet_total_votes
    votes_by_office['data'] = [total_presidential, total_parliamentary]
    votes_by_office['labels'] = [
        'Presidential ({} votes)'.format(votes_by_office['data'][0]),
        'Parliamentary ({} votes)'.format(votes_by_office['data'][1]),
    ]

    regional_counts['colors'] = []
    i = 0
    for collation in regional_collations.values():
        if i > len(COLOR_COMB) - 1:
            break
        if collation.get('label', None) is not None \
            and collation.get('value', None) is not None:
            regional_counts['labels'].append(collation['label'])
            regional_counts['data'].append(collation['value'])
            regional_counts['colors'].append(COLOR_COMB[i])
            i += 1


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


    # map_data
    presidential_map_data = {
        'list': [],
    }
    c = 0
    colors = {}
    title = 'Presidential Wins'
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
    c = 0
    party_colors = {}
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

        # find records with the percentage
        # total_results = results.annotate(
        #                             sum_collated_votes=F('total_votes'),
        #                             ) \
        #                      .values_list('sum_collated_votes')
        # total_results = sum([item[0] for item in total_results])
        # filter in only the parties with the max votes

        # presidential_map_data['list'].extend([v for v in results if v['total_votes'] == max_result and max_result > 0])

        for result in results:
            if result['total_votes'] == max_result and max_result > 0:
                color = party_colors.get(result['party__pk'], None)
                # color is not set
                if color is None:
                    color = COLOR_COMB[c]
                    party_colors[result['party__pk']] = color
                    c += 1
                # set the color
                result['color'] = color
                # set the path
                report_url = reverse('region_presidential_report',
                                     kwargs={'rpk': result['region__pk']})
                result['report_url'] = report_url

                # add to regional report pile
                presidential_map_data['list'].append(result)

    # percentage = 0
    # if zones.count() > 0:
    #     percentage = round(100 * len(map_data) / zones.count(), 0)


    foo = 'foo'
    if foo == 'bar':
        # DEBUG NOTES: Segment still too slow

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


        # parliamentary_votes_by_party
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
            print(candidate)
            print("::::::::::::::::::::::::::::::::::::::::::::")
            if candidate.get('total_votes', 0) > 0:
                first_name = candidate.get('candidate__first_name', '')
                last_name = candidate.get('candidate__last_name', '')
                party_code = candidate.get('candidate__party__code', '')
                label = f'{first_name[0]}.  {last_name} ({party_code})'
                value = candidate.get('total_votes', 0)
                charts[label] = value
        charts = {k: v for k, v in sorted(charts.items(), key=lambda item: item[1], reverse=True)}
        for label, value in charts.items():
            parliamentary_votes_by_party['labels'].append(label)
            parliamentary_votes_by_party['data'].append(value)



    context = dict(
        title=title,
        pie=pie,
        vote_validity=vote_validity,
        ec_variance=ec_variance,
        regional_counts=regional_counts,
        constituency_counts=constituency_counts,
        station_counts=station_counts,
        votes_by_office=votes_by_office,
        bar=bar,

        party_total_votes=party_total_votes,
        party_parliametary_votes=party_parliametary_votes,
        party_presidential_votes=party_presidential_votes,

        station_total_votes=station_total_votes,
        station_parliametary_votes=station_parliametary_votes,
        station_presidential_votes=station_presidential_votes,

        presidential_candidates=presidential_candidates,
        parliamentary_votes_by_party=parliamentary_votes_by_party,

        presidential_top=presidential_top,
        parliamentary_top=parliamentary_top,
        polling_station_counts=polling_station_counts,
        seat_counts=seat_counts,

        presidential_map_data=presidential_map_data,

    )

    return JsonResponse(context)


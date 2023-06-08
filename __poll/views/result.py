import io, datetime
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
from __geo.models import Station, Constituency, Region, Nation
from __poll.models import ResultSheet, ResultSheetApproval, Result, ResultApproval, Position
from __people.models import Party, Candidate, Agent
from __poll.serializers import ResultSerializer, PositionSerializer, PositionCollationSerializer
from __geo.serializers import StationSerializer, StationCollationSerializer
from __people.serializers import PartySerializer, CandidateSerializer
from __poll.utils.utils import get_zone_ct
from __poll.forms import ResultForm
from __poll.constants import ROWS_PER_PAGE
from django.db.models import Q, Prefetch, Value, F, Sum, IntegerField, Case, When, OuterRef, Subquery
from django.db.models.functions import Cast
from __poll.constants import StatusChoices
from django.contrib import messages
from account.models import User


def result_list(request):
    template = "poll/result_list.html"
    data = []
    total_per_page = ROWS_PER_PAGE
    result = Result.objects.all()

    page = request.GET.get('page', 1)
    paginator = Paginator(result, total_per_page)
    try:
        data = paginator.page(page)
    except PageNotAnInteger:
        data = paginator.page(1)
    except EmptyPage:
        data = paginator.page(paginator.num_pages)
    serializer = ResultSerializer(data, context={'request': request}, many=True)

    context = dict(
                    title='Results',
                    data=serializer.data,
                )
    return render(request, template, context)


def get_result_station(q):
    fields = [
                'id', 'code', 'title',
                'constituency__title', 'constituency__region__title',
                'presidential_votes', 'parliamentary_votes', 'total_votes',
                'constituency__id',
                'constituency__region__id',
                'constituency__region__nation__id',
                'presidential_position_id', 'parliamentary_position_id',
            ]
    
    presidential_position_queryset = Position.objects \
                                            .filter(
                                                    zone_ct=get_zone_ct(Nation),
                                                    zone_id=OuterRef('constituency__region__nation_id'),
                                                    ) \
                                            .annotate(
                                                    nation_position_id=F('id'),
                                                    nation_position_title=F('title')
                                                    )
    parliamentary_position_queryset = Position.objects \
                                            .filter(
                                                    zone_ct=get_zone_ct(Constituency),
                                                    zone_id=OuterRef('constituency_id'),
                                                    ) \
                                            .annotate(
                                                    constituency_position_id=F('id'),
                                                    constituency_position_title=F('title')
                                                    )
    presidential_position_id_queryset = presidential_position_queryset.values('nation_position_id')[:1]
    presidential_position_title_queryset = presidential_position_queryset.values('nation_position_title')[:1]
    parliamentary_position_id_queryset = parliamentary_position_queryset.values('constituency_position_id')[:1]
    parliamentary_position_title_queryset = parliamentary_position_queryset.values('constituency_position_title')[:1]
    
    stations = Station.objects \
                      .filter(
                            Q(title__icontains=q)
                            | Q(code__icontains=q)
                            | Q(constituency__title__icontains=q)
                            | Q(constituency__region__title__icontains=q)
                            ) \
                      .annotate(**dict(
                            presidential_position_id=Subquery(presidential_position_id_queryset),
                            presidential_position_title=Subquery(presidential_position_title_queryset),
                            parliamentary_position_id=Subquery(parliamentary_position_id_queryset),
                            parliamentary_position_title=Subquery(parliamentary_position_title_queryset),
                            presidential_votes_or_none=Sum(
                                    F('results__votes'),
                                    filter=Q(results__candidate__position__zone_ct=get_zone_ct(Nation))
                                ),
                            parliamentary_votes_or_none=Sum(
                                    F('results__votes'),
                                    filter=Q(results__candidate__position__zone_ct=get_zone_ct(Constituency))
                                ),
                            presidential_votes=Case(When(presidential_votes_or_none__gte=0, then=F('presidential_votes_or_none')), default=0),
                            parliamentary_votes=Case(When(parliamentary_votes_or_none__gte=0, then=F('parliamentary_votes_or_none')), default=0),
                            total_votes=Cast(F('presidential_votes'), IntegerField()) + Cast(F('parliamentary_votes'), IntegerField()),
                        )) \
            .values(*fields)
    return stations


def result_station_list(request):
    data = []
    station_previous_page = -1
    station_next_page = 0
    total_per_page = 100 # ROWS_PER_PAGE

    station_page = request.GET.get('spage', 1)
    base_url = '/poll/result/stations?'

    q = request.GET.get('q', '')
    if len(q) > 0:
        base_url = f'{base_url}q={q}'

    qm = request.GET.get('qm', '')
    if len(qm) > 0:
        base_url = f'{base_url}&qm={qm}'
    
    # apply search filters
    page = int(station_page)
    start_page = total_per_page * page
    stop_page = start_page + total_per_page
    stations = get_result_station(q) \
                .all()[start_page:stop_page]

    '''
    station_page = request.GET.get('spage', 1)
    station_paginator = Paginator(stations, total_per_page)
    try:
        station_data = station_paginator.page(station_page)
    except PageNotAnInteger:
        station_data = station_paginator.page(1)
    except EmptyPage:
        station_data = station_paginator.page(station_paginator.num_pages)
    context = dict(request=request)
    station_serializer = StationCollationSerializer(station_data, context=context, many=True)

    if station_data.has_next():
        station_next_page = station_data.next_page_number()
    if station_data.has_previous():
        station_previous_page = station_data.previous_page_number()
    '''

    if page > 0:
        station_previous_page = page - 1
    else:
        station_previous_page = 0
        
    if stations.count() < total_per_page:
        station_next_page = None
    else:
        station_next_page = page + 1

    context = dict(
        title='Results',
        # 'data': serializer.data,
        stations=stations,
        q=q,
        # 'candidates': candidates.data,
        # 'columns': ['candidate_details', 'station.title', 'votes', 'constituency_agent', 'result_sheet'],
        # station_numpages=station_paginator.num_pages,
        # station_count=station_paginator.count,
        station_next_link=f'{base_url}&spage=' + str(station_next_page),
        station_prev_link=f'{base_url}&spage=' + str(station_previous_page)
    )
    template = "poll/result_list.html"
    return render(request, template, context)


def result_position_list(request, spk=None):
    data = []
    nextPage = 1
    previousPage = 1
    total_per_page = ROWS_PER_PAGE
    
    nation = Nation.objects.first()
    stations = get_result_station('') \
                .filter(pk=spk)

    station = stations.first()

    nation_ct = get_zone_ct(Nation)
    constituency_ct = get_zone_ct(Constituency)
    positions = []
    presidential_positions = []
    parliamentary_positions = []
    positions = Position.objects.filter(
        zone_ct__in=[nation_ct, 
                        constituency_ct],
        zone_id__in=[nation.pk, station['constituency__id']]
    )
    presidential_positions = Position.objects.filter(
        zone_ct=nation_ct,
        zone_id=nation.pk
    )
    parliamentary_positions = Position.objects.filter(
        zone_ct=constituency_ct,
        zone_id=station['constituency__id']
    )
    position_ids = [p.pk for p in presidential_positions] + [p.pk for p in parliamentary_positions]
    positions = Position.objects \
                        .filter(
                            pk__in=position_ids
                        )

    '''
    station_page = request.GET.get('spage', 1)
    station_paginator = Paginator(stations, total_per_page)
    try:
        station_data = station_paginator.page(station_page)
    except PageNotAnInteger:
        station_data = station_paginator.page(1)
    except EmptyPage:
        station_data = station_paginator.page(station_paginator.num_pages)
    context = dict(request=request)
    station_serializer = StationCollationSerializer(station_data, context=context, many=True)
    '''

    position_page = request.GET.get('spage', 1)
    position_paginator = Paginator(positions, total_per_page)
    try:
        position_data = position_paginator.page(position_page)
    except PageNotAnInteger:
        position_data = position_paginator.page(1)
    except EmptyPage:
        position_data = position_paginator.page(position_paginator.num_pages)
    context = dict(request=request, spk=spk)
    position_serializer = PositionCollationSerializer(position_data, context=context, many=True)

    context = {
        'title': 'Results',
        # 'data': serializer.data,
        'stations': stations,
        'positions': position_serializer.data,
        # 'candidates': candidates.data,
        # 'count': paginator.count,
        # 'numpages' : paginator.num_pages,
        # 'columns': ['candidate_details', 'station.title', 'votes', 'constituency_agent', 'result_sheet'],
        # 'next_link': '/poll/results/?page=' + str(nextPage),
        # 'prev_link': '/poll/results/?page=' + str(previousPage)
    }
    template = "poll/result_list.html"
    return render(request, template, context)


def result_candidate_list(request, spk=None, ppk=None):
    messages.get_messages(request)
    template = "poll/result_list.html"
    data = []
    nextPage = 1
    previousPage = 1
    total_per_page = ROWS_PER_PAGE
    
    nation = Nation.objects.first()
    stations = get_result_station('') \
                    .filter(pk=spk)

    station = stations.first()

    agent_ct = get_zone_ct(Agent)
    nation_ct = get_zone_ct(Nation)
    region_ct = get_zone_ct(Region)
    constituency_ct = get_zone_ct(Constituency)
    station_ct = get_zone_ct(Station)

    presidential_positions = []
    parliamentary_positions = []
    presidential_positions = Position.objects.filter(
                                        zone_ct=nation_ct,
                                        zone_id=nation.pk,
                                        pk=ppk
                                    )
    parliamentary_positions = Position.objects.filter(
                                                        zone_ct=constituency_ct,
                                                        zone_id=station['constituency__id'],
                                                        pk=ppk
                                                    )
    position_ids = [p.pk for p in presidential_positions] + [p.pk for p in parliamentary_positions]
    positions = Position.objects.filter(
        pk__in=position_ids
    )

    candidates = Candidate.objects \
                          .filter(position_id__in=[p.pk for p in positions]) \
                          .prefetch_related(
                                Prefetch(
                                    'results',
                                    queryset=Result.objects.filter(station_id=spk),
                                    to_attr="station_results"
                                )
                          )
    
    # fetch result sheet
    result_sheet = ResultSheet.objects \
                            .filter(station__in=stations.values('pk'), position__in=positions) \
                            .first()

    # fetch approving agents
    agents = {}
    agent_ids = []
    for station in stations.all():
        agent = Agent.objects \
                    .filter(
                        zone_ct=station_ct,
                        zone_id=station['id'],
                    ).first()
        # TECH NOTES: Investigate why a zone does not have a valid agent
        user = None
        if agent is not None:
            agent_ids.append(agent.pk)
            user = User.objects \
                        .filter(
                            role_ct=agent_ct,
                            role_id=agent.pk,
                        ).first()
        approval = ResultSheetApproval.objects \
                                        .filter(
                                            result_sheet=result_sheet,
                                            approving_agent=agent
                                        ).first()
        agents['station'] = dict(zone='Station', user=user,
                                 agent=agent, approval=approval,
                                 is_approving=False)
        station_approval = approval

        is_approving = approval is not None
        agent = Agent.objects \
                        .filter(
                            zone_ct=constituency_ct,
                            zone_id=station['constituency__id'],
                        ).first()
        user = None
        if agent is not None:
            agent_ids.append(agent.pk)
            user = User.objects \
                        .filter(
                            role_ct=agent_ct,
                            role_id=agent.pk,
                        ).first()
        approval = ResultSheetApproval.objects \
                                        .filter(
                                            result_sheet=result_sheet,
                                            approving_agent=agent
                                        ).first()
        agents['constituency'] = dict(zone='Constituency', user=user,
                                      agent=agent, approval=approval,
                                      is_approving=False)
        constituency_approval = approval

        is_approving = is_approving and approval is not None
        agent = Agent.objects \
                        .filter(
                            zone_ct=region_ct,
                            zone_id=station['constituency__region__id'],
                        ).first()
        user = None
        if agent is not None:
            agent_ids.append(agent.pk)
            user = User.objects \
                        .filter(
                            role_ct=agent_ct,
                            role_id=agent.pk,
                        ).first()
        approval = ResultSheetApproval.objects \
                                        .filter(
                                            result_sheet=result_sheet,
                                            approving_agent=agent
                                        ).first()
        agents['region'] = dict(zone='Region', user=user,
                                agent=agent, approval=approval,
                                is_approving=False)
        region_approval = approval
        
        is_approving = is_approving and approval is not None
        agent = Agent.objects \
                        .filter(
                            zone_ct=nation_ct,
                            zone_id=station['constituency__region__nation__id'],
                        ).first()
        user = None
        if agent is not None:
            agent_ids.append(agent.pk)
            user = User.objects \
                        .filter(
                            role_ct=agent_ct,
                            role_id=agent.pk,
                        ).first()
        approval = ResultSheetApproval.objects \
                                        .filter(
                                            result_sheet=result_sheet,
                                            approving_agent=agent
                                        ).first()
        agents['nation'] = dict(zone='Nation', user=user,
                                agent=agent, approval=approval,
                                is_approving=False)
        nation_approval = approval

        agents['station']['is_approving'] = station_approval is None \
                                            and constituency_approval is None \
                                            and region_approval is None \
                                            and nation_approval is None

        agents['constituency']['is_approving'] = station_approval is not None \
                                            and constituency_approval is None \
                                            and region_approval is None \
                                            and nation_approval is None

        agents['region']['is_approving'] = station_approval is not None \
                                            and constituency_approval is not None \
                                            and region_approval is None \
                                            and nation_approval is None

        agents['nation']['is_approving'] = station_approval is not None \
                                            and constituency_approval is not None \
                                            and region_approval is not None \
                                            and nation_approval is None
        is_approved = station_approval is not None \
                                            and constituency_approval is not None \
                                            and region_approval is not None \
                                            and nation_approval is not None

    result_sheet_approvals = None
    result_sheet_url = None
    if result_sheet:
        if result_sheet.result_sheet:
            result_sheet_url = request.build_absolute_uri(result_sheet.result_sheet.url)
        # fetch the approvals
        result_sheet_approvals = ResultSheetApproval.objects \
                                                    .filter(
                                                        result_sheet=result_sheet,
                                                        approving_agent_id__in=agent_ids,
                                                    ).all()

    ready_for_approval = result_sheet is not None \
                        and result_sheet.results.count() > 0 \
                        and result_sheet_url is not None

    parties = Party.objects \
                    .prefetch_related(
                        Prefetch(
                            'candidates',
                            queryset=Candidate.objects \
                                .filter(position=ppk)
                                .prefetch_related(
                                    Prefetch(
                                        'results',
                                        queryset=Result.objects.filter(station_id=spk),
                                        to_attr="station_results"
                                    )
                                ),
                            to_attr="party_candidates"
                        )
                    )

    # results = Result.objects.filter(
    #     candidate__in=candidates,
    #     station__in=stations
    # )

    '''
    station_page = request.GET.get('spage', 1)
    station_paginator = Paginator(stations, total_per_page)
    try:
        station_data = station_paginator.page(station_page)
    except PageNotAnInteger:
        station_data = station_paginator.page(1)
    except EmptyPage:
        station_data = station_paginator.page(station_paginator.num_pages)
    station_serializer = StationSerializer(station_data, context={'request': request}, many=True)
    '''

    position_page = request.GET.get('ppage', 1)
    position_paginator = Paginator(positions, total_per_page)
    try:
        position_data = position_paginator.page(position_page)
    except PageNotAnInteger:
        position_data = position_paginator.page(1)
    except EmptyPage:
        position_data = position_paginator.page(station_paginator.num_pages)
    context = dict(request=request, spk=spk)
    position_serializer = PositionCollationSerializer(position_data, context=context, many=True)

    party_page = request.GET.get('papage', 1)
    party_paginator = Paginator(parties, total_per_page)
    try:
        party_data = party_paginator.page(party_page)
    except PageNotAnInteger:
        party_data = party_paginator.page(1)
    except EmptyPage:
        party_data = party_paginator.page(party_paginator.num_pages)
    party_serializer = PartySerializer(party_data, context={'request': request}, many=True)

    context = dict(
        title='Results',
        # data=serializer.data,
        stations=stations,
        positions=position_serializer.data,
        # 'results=result_serializer.data,
        # 'candidates=candidate_data, # candidate_serializer.data,
        parties=party_data,
        result_sheet=result_sheet,
        result_sheet_url=result_sheet_url,
        result_sheet_approvals=result_sheet_approvals,
        spk=spk,
        ppk=ppk,
        agents=agents,
        ready_for_approval=ready_for_approval,
        is_approved=is_approved,
        # count=paginator.count,
        # numpages=paginator.num_pages,
        # columns=['candidate_details', 'station.title', 'votes', 'constituency_agent', 'result_sheet'],
        # next_link='/poll/results/?page=' + str(nextPage),
        # prev_link='/poll/results/?page=' + str(previousPage)
    )
    
    if request.method == 'POST':
        station = request.POST.get('station', 0)
        position = request.POST.get('position', 0)
        total_votes = request.POST.get('total_votes', 0)
        total_invalid_votes = request.POST.get('total_invalid_votes', 0)
        total_valid_votes = request.POST.get('total_valid_votes', 0)

        new_file_uploaded = False
        result_sheet_file = request.POST.get('result_sheet_file', None)
        if request.FILES:
            new_file_uploaded = True
            result_sheet_file = request.FILES['result_sheet']

        candidates = request.POST.getlist('candidate', [])
        votes = request.POST.getlist('votes', [])

        station = 0 if len(station) <= 0 else int(station)
        position = 0 if len(position) <= 0 else int(position)
        total_votes = 0 if len(total_votes) <= 0 else int(total_votes)
        total_invalid_votes = 0 if len(total_invalid_votes) <= 0 else int(total_invalid_votes)
        total_valid_votes = 0 if len(total_valid_votes) <= 0 else int(total_valid_votes)

        n = len(candidates)

        # create result sheet
        defaults=dict(
                    total_votes=total_votes,
                    total_valid_votes=total_valid_votes,
                    total_invalid_votes=total_invalid_votes,
                    station_agent=None,
                    station_approval_at=None,
                    status=StatusChoices.ACTIVE)
        if new_file_uploaded:
            defaults['result_sheet']=result_sheet_file

        result_sheet, _ = ResultSheet.objects \
                                    .update_or_create(
                                        station_id=station,
                                        position_id=position,
                                        defaults=defaults)

        # create results
        for i in range(0, n):
            # try:
                result_vote = 0 if len(votes[i]) <= 0 else int(votes[i])
                result_candidate = 0 if len(candidates[i]) <= 0 else int(candidates[i])
                result, _ = Result.objects.update_or_create(
                                            station_id=station,
                                            candidate_id=result_candidate,
                                            defaults=dict(
                                                votes=result_vote,
                                                result_sheet=result_sheet,
                                                station_agent=None,
                                                status=StatusChoices.ACTIVE
                                            )
                                        )
            # except Exception as e:
            #     print('Exception :', e)
            #     context = {
            #         'error': 'There was an error saving the result. Please try again.'
            #     }
        message="Result sheet successfully saved"
        context = {
            'message': message
        }
        messages.success(request, message)
        return redirect(reverse('result_candidate_list', kwargs=dict(spk=spk, ppk=ppk)), "Result sheet successfully saved")
    
    return render(request, template, context)


def result_detail(request, pk=None):
    data = get_object_or_404(Result, pk=pk)
    initial = {
        'pk': data.pk,
        'constituency_agent': data.constituency_agent,
        'candidate': data.candidate,
        'station': data.station,
        'votes': data.votes,
        'result_sheet': data.result_sheet,
        'status': data.status,
    }
    if request.method == "GET":
        form = ResultForm(initial=initial)
    else:
        form = ResultForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"]
            title = form.cleaned_data["title"]
            result = form.cleaned_data['result']
            try:
                # send_mail(subject, message, from_email, ["admin@example.com"])
                result = Result(code=code, title=title, result=result)
                result.save()
            except BadHeaderError:
                return HttpResponse("Error saving record.")
            return redirect("Record successfully saved")
    return render(request, "poll/result_form.html", {"form": form})


def success_view(request):
    form = ResultForm()
    context = {"form": form, "message": "Success! Thank you for your message."}
    return render(request, "poll/result_form.html", context)

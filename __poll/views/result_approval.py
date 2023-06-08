import datetime, json
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
from __poll.models import (
    Result,
    ResultSheet,
    Position,
    ResultApproval,
    ResultSheetApproval,
    StationCollationSheet,
    ConstituencyCollationSheet,
    RegionalCollationSheet,
    NationalCollationSheet,
    SupernationalCollationSheet
)
from __people.models import Party
from __poll.serializers import ResultApprovalSerializer
from __poll.forms import ResultApprovalForm
from __poll.constants import ROWS_PER_PAGE, StatusChoices
from __people.models import Agent
from __geo.models import Nation, Region, Constituency, Station
from account.models import User
from __poll.utils.utils import get_zone_ct
from django.db.models import F, Value, Q, Func, Sum
from django.db.models.functions import Concat, Left


TEMPLATE = "poll/result_approval_list.html"
OFFICE_TYPES = [
                'Presidential',
                'Parliamentary',
            ]
ZONE_LEVELS = [
                'Constituency',
                'Region',
                'Nation'
            ]


def result_approval_list(request):
    data = []
    nextPage = 1
    previousPage = 1
    total_per_page = ROWS_PER_PAGE
    result_approval = ResultApproval.objects.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(result_approval, total_per_page)
    try:
        data = paginator.page(page)
    except PageNotAnInteger:
        data = paginator.page(1)
    except EmptyPage:
        data = paginator.page(paginator.num_pages)
    serializer = ResultApprovalSerializer(data, context={'request': request}, many=True)
    if data.has_next():
        nextPage = data.next_page_number()
    if data.has_previous():
        previousPage = data.previous_page_number()
    
    title = 'Result Approvals'
    next_link = '/poll/result_approvals/?page=' + str(nextPage)
    prev_link = '/poll/result_approvals/?page=' + str(previousPage)
    columns = [{'title': 'result'}, {'title': 'approved_at'}, {'title': 'approving_agent.name'}, {'title': 'result.title'}]
    zone_level = 'constituency'
    zones = []
    if zone_level.lower() == 'constituency':
        zones = list(Constituency.objects.annotate(value=F('id')).values('value', 'title').values())
    elif zone_level.lower() == 'region':
        zones = list(Region.objects.annotate(value=F('id')).values('value', 'title').values())
    elif zone_level.lower() == 'nation':
        zones = list(Nation.objects.annotate(value=F('id')).values('value', 'title').values())

    context = dict(
        title=title,
        office_types=OFFICE_TYPES,
        zone_levels=ZONE_LEVELS,
        zones=zones,
        data=serializer.data,
        count=paginator.count,
        numpages=paginator.num_pages,
        columns=columns,
        next_link=next_link,
        prev_link=prev_link,
    )
    return render(request, TEMPLATE, context)



def get_party_candidates(data, zone_ct):
    if data is not None:
        for row in data:
            pk = row.get('party__id', 0)
            if pk > 0:
                candidates = Party.objects \
                            .filter(pk=pk).get() \
                            .candidates \
                            .filter(position__zone_ct=zone_ct) \
                            .annotate(full_name=Concat(
                                F('prefix'),
                                Value(' '), F('first_name'),
                                Value(' '), F('other_names'),
                                Value(' '), F('last_name')
                            )) \
                            .values('full_name')
                row['candidates'] = candidates
    return data

def get_approval_totals(data):
    totals = dict(
            party__id=0,
            party__code='-',
            party__title='Total Votes',
            total_votes=0,
            total_votes_ec=0,
            total_ec_variance=0,
            total_invalid_votes=0,
        )
    for row in data:
        totals['total_votes'] += row['total_votes']
        totals['total_votes_ec'] += row['total_votes_ec']
        totals['total_ec_variance'] = totals['total_votes_ec'] - totals['total_votes']
        totals['total_invalid_votes'] += row['total_invalid_votes']
    return totals

def result_is_approved(data):
    total_total_votes_ec = 0
    if data is not None:
        for row in data:
            total_total_votes_ec += row.get('total_votes_ec', 0)
            if total_total_votes_ec > 0:
                break
    return total_total_votes_ec > 0

def get_view_context(selected_office_type,
                     selected_zone_level,
                     pk=None):
    # page columns (not used)
    zone_choice_api = '/api/geo/{}/choices/'.format(selected_zone_level.lower())
    columns = [
            {'title': 'party__id'},
            {'title': 'party__code'},
            {'title': 'party__title'},
            {'title': 'total_votes'},
            {'title': 'total_votes_ec'},
            {'title': 'total_ec_variance'},
            {'title': 'total_invalid_votes'},
        ]
    fields = [
        'party__id',
        'party__code',
        'party__title',
        'total_votes',
        'total_votes_ec',
        'total_ec_variance',
        'total_invalid_votes',
    ]
    # zone model for zone_ct or office type
    zone_ct_model = Constituency
    if selected_office_type == 'presidential':
        zone_ct_model = Nation

    # model and zone model
    model = None
    if selected_zone_level.lower() == 'constituency':
        zone_model = Constituency
        model = RegionalCollationSheet
    elif selected_zone_level.lower() == 'region':
        model = NationalCollationSheet
        zone_model = Region
    elif selected_zone_level.lower() == 'nation':
        model = SupernationalCollationSheet
        zone_model = Nation

    # the selected zone (select option in the zone select box)
    selected_zone = None
    if pk is not None:
        selected_zone = int(pk)

    # get only zones that have valid result ids
    # valid result ids at all levels
    ids = dict(
                nation=[],
                region=[],
                constituency=[],
                station=[],
            )
    # fetch all result sheet
    result_sheets = ResultSheet.objects \
                                .values(
                                    'station_id', 'station__constituency_id',
                                    'station__constituency__region_id',
                                    'station__constituency__region__nation_id'
                                ).all()
    # loop through result sheets
    for result_sheet in result_sheets:
        # file away result ids at proper levels
        ids['nation'].append(result_sheet['station__constituency__region__nation_id'])
        ids['region'].append(result_sheet['station__constituency__region_id'])
        ids['constituency'].append(result_sheet['station__constituency_id'])
        ids['station'].append(result_sheet['station_id'])
    # page title
    title = '{} Result Approvals ({})'.format(selected_office_type.capitalize(), selected_zone_level.capitalize())
    zone_ct = get_zone_ct(zone_ct_model)
    # zones for select box
    zones = list(zone_model.objects
                            .annotate(value=F('id'))
                            .values('value', 'title')
                            # use ids to filter the zones to only zones that have result ids
                            .filter(id__in=ids[zone_model.__name__.lower()])
                            .values())

    return dict(
        title=title,
        zones=zones,
        fields=fields,
        office_types=OFFICE_TYPES,
        zone_levels=ZONE_LEVELS,
        selected_zone=selected_zone,
        selected_office_type=selected_office_type,
        selected_zone_level=selected_zone_level,
        zone_ct=zone_ct,
        zone_model=zone_model,
        model=model,
        columns=columns,
        zone_choice_api=zone_choice_api,
    )



def result_approval_list_presidential(request):
    selected_office_type = 'presidential'
    title = '{} Result Approvals'.format(selected_office_type.capitalize())
    context = dict(
        title=title,
        selected_office_type=selected_office_type,
        office_types=OFFICE_TYPES,
        zone_levels=ZONE_LEVELS,
    )
    return render(request, TEMPLATE, context)
    
def result_approval_list_parliamentary(request):
    selected_office_type = 'parliamentary'
    title = '{} Result Approvals'.format(selected_office_type.capitalize())
    context = dict(
        title=title,
        selected_office_type=selected_office_type,
        office_types=OFFICE_TYPES,
        zone_levels=ZONE_LEVELS,
    )
    return render(request, TEMPLATE, context)



def result_approval_list_presidential_constituency(request, pk=None):
    selected_office_type = 'presidential'
    selected_zone_level = 'constituency'
    context = get_view_context(
                               selected_office_type,
                               selected_zone_level,
                               pk=pk)
    model = context['model']
    zone_ct = context['zone_ct']
    data = model.objects \
                .filter(
                        constituency_id=pk,
                        zone_ct=zone_ct
                ) \
                .distinct('party__code') \
                .order_by('party__code') \
                .annotate(total_ec_variance=F('total_votes_ec') - F('total_votes')) \
                .values(*context['fields'])
    data = get_party_candidates(data, zone_ct)
    context['is_approved'] = result_is_approved(data)
    context['totals'] = get_approval_totals(data)
    context['data'] = data
    return render(request, TEMPLATE, context)

def result_approval_list_presidential_regional(request, pk=None):
    selected_office_type = 'presidential'
    selected_zone_level = 'region'
    context = get_view_context(
                               selected_office_type,
                               selected_zone_level,
                               pk=pk)
    model = context['model']
    zone_ct = context['zone_ct']
    data = model.objects \
                .filter(
                        region_id=pk,
                        zone_ct=zone_ct
                ) \
                .distinct('party__code') \
                .order_by('party__code') \
                .annotate(total_ec_variance=F('total_votes_ec') - F('total_votes')) \
                .values(*context['fields'])
    data = get_party_candidates(data, zone_ct)
    context['is_approved'] = result_is_approved(data)
    context['totals'] = get_approval_totals(data)
    context['data'] = data
    return render(request, TEMPLATE, context)

def result_approval_list_presidential_national(request, pk=None):
    selected_office_type = 'presidential'
    selected_zone_level = 'nation'
    context = get_view_context(
                               selected_office_type,
                               selected_zone_level,
                               pk=pk)
    model = context['model']
    zone_ct = context['zone_ct']
    data = model.objects \
                .filter(
                        nation_id=pk,
                        zone_ct=zone_ct
                ) \
                .distinct('party__code') \
                .order_by('party__code') \
                .annotate(total_ec_variance=F('total_votes_ec') - F('total_votes')) \
                .values(*context['fields'])
    data = get_party_candidates(data, zone_ct)
    context['is_approved'] = result_is_approved(data)
    context['totals'] = get_approval_totals(data)
    context['data'] = data
    return render(request, TEMPLATE, context)


def result_approval_list_parliamentary_constituency(request, pk=None):
    selected_office_type = 'parliamentary'
    selected_zone_level = 'constituency'
    context = get_view_context(
                               selected_office_type,
                               selected_zone_level,
                               pk=pk)
    model = context['model']
    zone_ct = context['zone_ct']
    data = model.objects \
                .filter(
                        constituency_id=pk,
                        zone_ct=zone_ct
                ) \
                .distinct('party__code') \
                .order_by('party__code') \
                .annotate(total_ec_variance=F('total_votes_ec') - F('total_votes')) \
                .values(*context['fields'])
    data = get_party_candidates(data, zone_ct)
    context['is_approved'] = result_is_approved(data)
    context['totals'] = get_approval_totals(data)
    context['data'] = data
    return render(request, TEMPLATE, context)

def result_approval_list_parliamentary_regional(request, pk=None):
    selected_office_type = 'parliamentary'
    selected_zone_level = 'region'
    context = get_view_context(
                               selected_office_type,
                               selected_zone_level,
                               pk=pk)
    model = context['model']
    zone_ct = context['zone_ct']
    data = model.objects \
                .filter(
                        region_id=pk,
                        zone_ct=zone_ct
                ) \
                .distinct('party__code') \
                .order_by('party__code') \
                .annotate(total_ec_variance=F('total_votes_ec') - F('total_votes')) \
                .values(*context['fields'])
    data = get_party_candidates(data, zone_ct)
    context['is_approved'] = result_is_approved(data)
    context['totals'] = get_approval_totals(data)
    context['data'] = data
    return render(request, TEMPLATE, context)

def result_approval_list_parliamentary_national(request, pk=None):
    selected_office_type = 'parliamentary'
    selected_zone_level = 'nation'
    context = get_view_context(
                               selected_office_type,
                               selected_zone_level,
                               pk=pk)
    model = context['model']
    zone_ct = context['zone_ct']
    data = model.objects \
                .filter(
                        nation_id=pk,
                        zone_ct=zone_ct
                ) \
                .distinct('party__code') \
                .order_by('party__code') \
                .annotate(total_ec_variance=F('total_votes_ec') - F('total_votes')) \
                .values(*context['fields'])
    data = get_party_candidates(data, zone_ct)
    context['is_approved'] = result_is_approved(data)
    context['totals'] = get_approval_totals(data)
    context['data'] = data
    return render(request, TEMPLATE, context)







def result_approval_detail(request, pk=None):
    data = get_object_or_404(ResultApproval, pk=pk)
    initial = {
        'pk': data.pk,
        'code': data.code,
        'title': data.title,
        'status': data.status,
    }
    if request.method == "GET":
        form = ResultApprovalForm(initial=initial)
    else:
        form = ResultApprovalForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"]
            title = form.cleaned_data["title"]
            result_approval = form.cleaned_data['result_approval']
            try:
                # send_mail(subject, message, from_email, ["admin@example.com"])
                result_approval = ResultApproval(code=code, title=title, result_approval=result_approval)
                result_approval.save()
            except BadHeaderError:
                return HttpResponse("Error saving record.")
            return redirect("Record successfully saved")
    return render(request, "poll/result_approval_form.html", {"form": form})


def success_view(request):
    form = ResultApprovalForm()
    context = {"form": form, "message": "Success! Thank you for your message."}
    return render(request, "poll/result_approval_form.html", context)


def result_approval_form(request, spk=None, ppk=None):
    template = "poll/result_approval_list.html"
    context = dict()

    if request.method == 'POST':

        station_ct = get_zone_ct(Station)
        constituency_ct = get_zone_ct(Constituency)
        region_ct = get_zone_ct(Region)
        nation_ct = get_zone_ct(Nation)

        user_id = request.POST.get('approving_agent_user_id', 0)
        ec_summary_total = request.POST.get('ec_summary_total', 0)
        # total_valid_votes = request.POST.get('approval_total_valid_votes', 0)
        # result_sheet_file = request.POST.get('result_sheet_file', 0)
        # agent_id = request.POST.get('approval_agent', 0)
        # station_id = request.POST.get('approval_station', 0)
        # total_votes = request.POST.get('approval_total_votes', 0)

        # validate
        validation_errors = []
        total_valid_votes = 0
        result_sheet = None
        result_sheet_file_exists = False
        result_sheet_has_approvals = True
        station_agent = None
        constituency_agent = None
        regional_agent = None
        national_agent = None

        try:
            result_sheet = ResultSheet.objects \
                        .filter(
                            station_id=spk,
                            position_id=ppk,
                        ).first()
            total_valid_votes = result_sheet.total_invalid_votes
        except Exception as e:
            print(e)
            validation_errors.append("Result sheet does not exist.")

        try:
            station = Station.objects.filter(pk=spk).first()
        except Exception as e:
            print(e)
            validation_errors.append("Station does not exist.")

        agent = None
        user = User.objects.filter(
                                pk=user_id,
                                role_ct=get_zone_ct(Agent),
                            ).first()
        if user is None:
            validation_errors.append("User account does not exist.")
        else:
            agent = Agent.objects.filter(pk=user.role_id).first()
            if agent is None:
                validation_errors.append("Agent record does not exist.")

        try:
            station_agent = Agent.objects.filter(
                                    zone_ct=station_ct,
                                    zone_id=station.pk
                                ).first()
        except Exception as e:
            validation_errors.append("Station Agent record does not exist.")
            print(e)
        try:
            constituency_agent = Agent.objects.filter(
                                    zone_ct=constituency_ct,
                                    zone_id=station.constituency.pk
                                ).first()
        except Exception as e:
            validation_errors.append("Constituency Agent record does not exist.")
            print(e)
        try:
            regional_agent = Agent.objects.filter(
                                    zone_ct=region_ct,
                                    zone_id=station.constituency.region.pk
                                ).first()
        except Exception as e:
            validation_errors.append("Regional Agent record does not exist.")
            print(e)
        try:
            national_agent = Agent.objects.filter(
                                    zone_ct=nation_ct,
                                    zone_id=station.constituency.region.nation.pk
                                ).first()
        except Exception as e:
            validation_errors.append("National Agent record does not exist.")
            print(e)

        has_station_approval = False
        has_constituency_approval = False
        has_regional_approval = False
        has_national_approval = False
        if station_agent is not None:
            has_station_approval = ResultSheetApproval.objects \
                                                .filter(
                                                    result_sheet=result_sheet,
                                                    approving_agent_id=station_agent.pk,
                                                ).first()
        if constituency_agent is not None:
            has_constituency_approval = ResultSheetApproval.objects \
                                                    .filter(
                                                        result_sheet=result_sheet,
                                                        approving_agent_id=constituency_agent.pk,
                                                    ).first()
        if regional_agent is not None:
            has_regional_approval = ResultSheetApproval.objects \
                                                .filter(
                                                    result_sheet=result_sheet,
                                                    approving_agent_id=regional_agent.pk,
                                                ).first()
        if national_agent is not None:
            has_national_approval = ResultSheetApproval.objects \
                                                .filter(
                                                    result_sheet=result_sheet,
                                                    approving_agent_id=national_agent.pk,
                                                ).first()

        if agent is not None:
            if agent.zone_ct == get_zone_ct(Nation):
                result_sheet_has_approvals = has_station_approval and has_constituency_approval and has_regional_approval and not has_national_approval
            elif agent.zone_ct == get_zone_ct(Region):
                result_sheet_has_approvals = has_station_approval and has_constituency_approval and not (has_regional_approval and has_national_approval)
            elif agent.zone_ct == get_zone_ct(Constituency):
                result_sheet_has_approvals = has_station_approval and not (has_constituency_approval and has_regional_approval and has_national_approval)
            elif agent.zone_ct == get_zone_ct(Station):
                result_sheet_has_approvals = not (has_station_approval and has_constituency_approval and has_regional_approval and has_national_approval)

        if result_sheet is not None:
            result_sheet_file_exists = result_sheet.result_sheet is not None
        else:
            validation_errors.append(f"Result sheet file does not exist. {result_sheet.result_sheet}")

        if not result_sheet_has_approvals:
            validation_errors.append("Proper approval trail record does not exist.")

        is_valid = False
        if result_sheet_file_exists and result_sheet_has_approvals:
            is_valid = True

        # approve result sheet
        if is_valid:
            ra, _ = ResultSheetApproval.objects \
                        .update_or_create(
                            result_sheet=result_sheet,
                            approving_agent=agent,
                            defaults=dict(
                                total_valid_votes=total_valid_votes,
                                ec_summary_total=ec_summary_total,
                                # variance=total_invalid_votes,
                                approved_at=datetime.datetime.now(),
                                status=StatusChoices.ACTIVE
                            )
                        )
            message="Result sheet successfully approved"
            context = dict(
                message=message
            )
            messages.success(request, message)
        else:
            validation_errors = '' + f"\r\n".join(validation_errors) + ''
            message=f"Invalid Result sheet. Approval cancelled. {validation_errors}"
            context = dict(
                message=message
            )
            messages.error(request, message)
        return redirect(reverse('result_candidate_list', kwargs=dict(spk=spk, ppk=ppk)), "Result sheet successfully saved")
    return render(request, template, context)




def approve_presidential():
    pass

def validate_approval_sheet(form):
    return False



# FORM HELPERS

def get_approval_context(
                        selected_office_type,
                        selected_zone_level,
                        ):
    office_type = 'parliamentary'
    zone_ct_model = Constituency
    if selected_office_type == 'presidential':
        office_type = 'presidential'
        zone_ct_model = Nation
    zone_ct = get_zone_ct(zone_ct_model)
    zone_type = selected_zone_level
    if selected_zone_level == 'nation':
        sheet_model = SupernationalCollationSheet
    elif selected_zone_level == 'region':
        sheet_model = NationalCollationSheet
    elif selected_zone_level == 'constituency':
        sheet_model = RegionalCollationSheet
    return dict(
            zone_ct=zone_ct,
            office_type=office_type,
            zone_type=zone_type,
            zone_ct_model=zone_ct_model,
            sheet_model=sheet_model,
            )

def get_updated_approval_sheet_queryset(model, pk, zone_ct, party_id):
    instance = None
    try:
        instance = model.objects \
                        .filter(
                            zone_ct=zone_ct,
                            party_id=int(party_id),
                        )
    except Exception as e:
        print(e)
    return instance

def update_approvals(request, model, instances, fields, pk, office_type, zone_type, path_name):
    messages.get_messages(request)
    context = dict()
    if len(instances) > 0:
        try:
            _ = model.objects.bulk_update(instances, fields=fields)
            message = f'{office_type.capitalize()} Results ({zone_type.capitalize()}) approved for {len(instances)} parties'
            context['message'] = message
            messages.success(request, message)
            return redirect(reverse(path_name, kwargs=dict(pk=pk)), context['message'])
        except Exception as e:
            print(e)
    message = f'There was an error approving {office_type.capitalize()} Results ({zone_type.capitalize()})'
    context['message'] = message
    messages.success(request, message)
    return redirect(reverse(path_name, kwargs=dict(pk=pk)), context['message'])

# FORM HELPERS


def approve_presidential_national(request, pk=None):
    office_type = 'presidential'
    zone_type = 'nation'

    fields = ['total_votes_ec',]
    path_name = f'result_approval_list_{office_type}_{zone_type}'
    approval_context = get_approval_context(office_type, zone_type)
    sheet_model = approval_context.get('sheet_model', None)
    zone_ct = approval_context.get('zone_ct', None)
    instances = []
    if sheet_model is not None and zone_ct is not None:
        if request.method == "POST":
            party_ids = request.POST.getlist('approval_party_id')
            total_votes_ec = request.POST.getlist('approval_total_votes_ec')
            for i in range(0, len(party_ids)):
                try:
                    instance = get_updated_approval_sheet_queryset(
                                                            model=sheet_model,
                                                            pk=pk,
                                                            zone_ct=zone_ct,
                                                            party_id=party_ids[i]
                                                        ) \
                                                        .filter(nation_id=pk) \
                                                        .get()
                    instance.total_votes_ec = int(total_votes_ec[i])
                    instances.append(instance)
                except Exception as e:
                    # TECH NOTES: Error approving result for party
                    party = Party.objects.values('title').filter(id=party_ids[i]).values()[0]['title']
                    print(f"Results for {party} party will not be included", e)
    # update approval sheet and return template
    return update_approvals(
                        request=request,
                        model=sheet_model,
                        instances=instances,
                        fields=fields, pk=pk,
                        office_type=office_type,
                        zone_type=zone_type,
                        path_name=path_name
                    )

def approve_presidential_regional(request, pk=None):
    office_type = 'presidential'
    zone_type = 'region'

    fields = ['total_votes_ec',]
    path_name = f'result_approval_list_{office_type}_{zone_type}'
    approval_context = get_approval_context(office_type, zone_type)
    sheet_model = approval_context.get('sheet_model', None)
    zone_ct = approval_context.get('zone_ct', None)
    instances = []
    if sheet_model is not None and zone_ct is not None:
        if request.method == "POST":
            party_ids = request.POST.getlist('approval_party_id')
            total_votes_ec = request.POST.getlist('approval_total_votes_ec')
            for i in range(0, len(party_ids)):
                try:
                    instance = get_updated_approval_sheet_queryset(
                                                            model=sheet_model,
                                                            pk=pk,
                                                            zone_ct=zone_ct,
                                                            party_id=party_ids[i]
                                                        ) \
                                                        .filter(region_id=pk) \
                                                        .get()
                    instance.total_votes_ec = int(total_votes_ec[i])
                    instances.append(instance)
                except Exception as e:
                    # TECH NOTES: Error approving result for party
                    party = Party.objects.values('title').filter(id=party_ids[i]).values()[0]['title']
                    print(f"Results for {party} party will not be included", e)
    # update approval sheet and return template
    return update_approvals(
                        request=request,
                        model=sheet_model,
                        instances=instances,
                        fields=fields, pk=pk,
                        office_type=office_type,
                        zone_type=zone_type,
                        path_name=path_name
                    )

def approve_presidential_constituency(request, pk=None):
    office_type = 'presidential'
    zone_type = 'constituency'

    fields = ['total_votes_ec',]
    path_name = f'result_approval_list_{office_type}_{zone_type}'
    approval_context = get_approval_context(office_type, zone_type)
    sheet_model = approval_context.get('sheet_model', None)
    zone_ct = approval_context.get('zone_ct', None)
    instances = []
    if sheet_model is not None and zone_ct is not None:
        if request.method == "POST":
            party_ids = request.POST.getlist('approval_party_id')
            total_votes_ec = request.POST.getlist('approval_total_votes_ec')
            for i in range(0, len(party_ids)):
                try:
                    instance = get_updated_approval_sheet_queryset(
                                                            model=sheet_model,
                                                            pk=pk,
                                                            zone_ct=zone_ct,
                                                            party_id=party_ids[i]
                                                        ) \
                                                        .filter(constituency_id=pk) \
                                                        .get()
                    instance.total_votes_ec = int(total_votes_ec[i])
                    instances.append(instance)
                except Exception as e:
                    # TECH NOTES: Error approving result for party
                    party = Party.objects.values('title').filter(id=party_ids[i]).values()[0]['title']
                    print(f"Results for {party} party will not be included", e)
    # update approval sheet and return template
    return update_approvals(
                        request=request,
                        model=sheet_model,
                        instances=instances,
                        fields=fields, pk=pk,
                        office_type=office_type,
                        zone_type=zone_type,
                        path_name=path_name
                    )


def approve_parliamentary_national(request, pk=None):
    office_type = 'parliamentary'
    zone_type = 'nation'

    fields = ['total_votes_ec',]
    path_name = f'result_approval_list_{office_type}_{zone_type}'
    approval_context = get_approval_context(office_type, zone_type)
    sheet_model = approval_context.get('sheet_model', None)
    zone_ct = approval_context.get('zone_ct', None)
    instances = []
    if sheet_model is not None and zone_ct is not None:
        if request.method == "POST":
            party_ids = request.POST.getlist('approval_party_id')
            total_votes_ec = request.POST.getlist('approval_total_votes_ec')
            for i in range(0, len(party_ids)):
                try:
                    instance = get_updated_approval_sheet_queryset(
                                                            model=sheet_model,
                                                            pk=pk,
                                                            zone_ct=zone_ct,
                                                            party_id=party_ids[i]
                                                        ) \
                                                        .filter(nation_id=pk) \
                                                        .get()
                    instance.total_votes_ec = int(total_votes_ec[i])
                    instances.append(instance)
                except Exception as e:
                    # TECH NOTES: Error approving result for party
                    party = Party.objects.values('title').filter(id=party_ids[i]).values()[0]['title']
                    print(f"Results for {party} party will not be included", e)
    # update approval sheet and return template
    return update_approvals(
                        request=request,
                        model=sheet_model,
                        instances=instances,
                        fields=fields, pk=pk,
                        office_type=office_type,
                        zone_type=zone_type,
                        path_name=path_name
                    )

def approve_parliamentary_regional(request, pk=None):
    office_type = 'parliamentary'
    zone_type = 'region'

    fields = ['total_votes_ec',]
    path_name = f'result_approval_list_{office_type}_{zone_type}'
    approval_context = get_approval_context(office_type, zone_type)
    sheet_model = approval_context.get('sheet_model', None)
    zone_ct = approval_context.get('zone_ct', None)
    instances = []
    if sheet_model is not None and zone_ct is not None:
        if request.method == "POST":
            party_ids = request.POST.getlist('approval_party_id')
            total_votes_ec = request.POST.getlist('approval_total_votes_ec')
            for i in range(0, len(party_ids)):
                try:
                    instance = get_updated_approval_sheet_queryset(
                                                            model=sheet_model,
                                                            pk=pk,
                                                            zone_ct=zone_ct,
                                                            party_id=party_ids[i]
                                                        ) \
                                                        .filter(region_id=pk) \
                                                        .get()
                    instance.total_votes_ec = int(total_votes_ec[i])
                    instances.append(instance)
                except Exception as e:
                    # TECH NOTES: Error approving result for party
                    party = Party.objects.values('title').filter(id=party_ids[i]).values()[0]['title']
                    print(f"Results for {party} party will not be included", e)
    # update approval sheet and return template
    return update_approvals(
                        request=request,
                        model=sheet_model,
                        instances=instances,
                        fields=fields, pk=pk,
                        office_type=office_type,
                        zone_type=zone_type,
                        path_name=path_name
                    )

def approve_parliamentary_constituency(request, pk=None):
    office_type = 'parliamentary'
    zone_type = 'constituency'

    fields = ['total_votes_ec',]
    path_name = f'result_approval_list_{office_type}_{zone_type}'
    approval_context = get_approval_context(office_type, zone_type)
    sheet_model = approval_context.get('sheet_model', None)
    zone_ct = approval_context.get('zone_ct', None)
    instances = []
    if sheet_model is not None and zone_ct is not None:
        if request.method == "POST":
            party_ids = request.POST.getlist('approval_party_id')
            total_votes_ec = request.POST.getlist('approval_total_votes_ec')
            for i in range(0, len(party_ids)):
                try:
                    instance = get_updated_approval_sheet_queryset(
                                                            model=sheet_model,
                                                            pk=pk,
                                                            zone_ct=zone_ct,
                                                            party_id=party_ids[i]
                                                        ) \
                                                        .filter(constituency_id=pk) \
                                                        .get()
                    instance.total_votes_ec = int(total_votes_ec[i])
                    instances.append(instance)
                except Exception as e:
                    # TECH NOTES: Error approving result for party
                    party = Party.objects.values('title').filter(id=party_ids[i]).values()[0]['title']
                    print(f"Results for {party} party will not be included", e)
    # update approval sheet and return template
    return update_approvals(
                        request=request,
                        model=sheet_model,
                        instances=instances,
                        fields=fields, pk=pk,
                        office_type=office_type,
                        zone_type=zone_type,
                        path_name=path_name
                    )



from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages

from __poll.constants import ROWS_PER_PAGE, FormMessages
from __geo.models import Station
from __geo.serializers import StationSerializer
from __geo.forms import StationForm


@login_required
def station_list(request, choice=False):
    template = 'geo/station_list.html'
    base_url = '/geo/stations?'
    data = []
    nextPage = 1
    previousPage = 1
    total_per_page = ROWS_PER_PAGE
    q = request.GET.get('q', '')
    if len(q) > 0:
        base_url = f'{base_url}q={q}'
    stations = Station.objects \
                        .filter(
                                Q(title__icontains=q)
                                | Q(code__icontains=q)
                                | Q(constituency__title__icontains=q)
                                | Q(constituency__region__title__icontains=q)
                                ) \
                        .all() \
                        .order_by('pk')
    page = request.GET.get('page', 1)
    paginator = Paginator(stations, total_per_page)
    try:
        data = paginator.page(page)
    except PageNotAnInteger:
        data = paginator.page(1)
    except EmptyPage:
        data = paginator.page(paginator.num_pages)
    serializer = StationSerializer(data, context=dict(request=request), many=True)
    if data.has_next():
        nextPage = data.next_page_number()
    if data.has_previous():
        previousPage = data.previous_page_number()
    context = dict(
        title='Stations',
        data=serializer.data,
        count=paginator.count,
        numpages=paginator.num_pages,
        columns=[
                    dict(title='code', width=10),
                    dict(title='title', width=40),
                    dict(title='constituency.title', width=15),
                    dict(title='agent.full_name', width=15),
                    dict(title='total_votes', width=5, type='vote_count'),
                    dict(title='total_presidential_votes', width=5, type='vote_count'),
                    dict(title='total_parliamentary_votes', width=5, type='vote_count'),
                ],
        next_link='/geo/stations/?page=' + str(nextPage),
        prev_link='/geo/stations/?page=' + str(previousPage)
    )
    return render(request, template, context)


@login_required
def station_detail(request, pk=None):
    title='Station'
    list_path =  'station_list'
    detail_path = 'station_detail'
    template = 'geo/station_form.html'
    data = get_object_or_404(Station, pk=pk)
    initial = dict(
                   pk=pk,
                   code=data.code,
                   title=data.title,
                   details=data.details,
                   constituency=data.constituency,
                   status=data.status,
                  )
    form = StationForm(initial=initial)
    context = dict(
                   pk=pk,
                   title=title,
                   elements=form,
                   list_path=list_path,
                   detail_path=detail_path,
                  )
    # TECH NOTES: Revisit this indicator for reporting during GET (404 and 200)
    context['message'] = ''
    context['form'] = form
    context['template'] = template
    if not request.method == "GET":
        error = 1
        form = StationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data.get('code', None)
            title = form.cleaned_data.get('title', None)
            constituency = form.cleaned_data.get('constituency', None)
            status = form.cleaned_data.get('status', None)
            details = form.cleaned_data.get('details', None)
            try:
                instance, _ = Station.objects \
                                    .update_or_create(pk=pk,
                                                      defaults=dict(code=code,
                                                                    title=title,
                                                                    constituency=constituency,
                                                                    status=status,
                                                                    details=details,
                                                                    ))
                error = 0
                context['form'] = StationForm(initial=dict(
                                        pk=instance.pk,
                                        code=instance.code,
                                        title=instance.title,
                                        details=instance.details,
                                        constituency=instance.constituency,
                                        status=instance.status,
                                    ))
            except Exception as e:
                context['message'] = FormMessages.ERROR
                # TECH NOTES: add logger
                print(e)
            else:
                context['message'] = FormMessages.SUCCESS
        else:
            context['message'] = '{} {}'.format(FormMessages.INVALID_FORM, form.errors)
        context['error'] = error
        return submit_complete(request, context=context)
    return render(request, template, context)


@login_required
def submit_complete(request,
                    context={}):
    title='Station'
    list_path='station_list'
    detail_path='station_detail'
    template = 'geo/station_form.html'
    pk = context.get('pk', 0)
    message = context.get('message', '')
    error = context.get('error', '')
    messages.success(request, message)
    data = get_object_or_404(Station, pk=pk)
    form = StationForm(dict(
                            pk=data.pk,
                            title=data.title,
                            constituency=data.constituency,
                            details=data.details,
                            status=data.status,
                            ))
    context = dict(
                    pk=pk,
                    title=title,
                    elements=form,
                    list_path=list_path,
                    detail_path=detail_path,
                    error=error,
                    message=message
                   )
    return render(request, template, context)

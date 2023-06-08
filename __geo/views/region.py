from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages

from __poll.constants import ROWS_PER_PAGE, FormMessages
from __geo.forms import RegionForm
from __geo.models import Region
from __geo.serializers import RegionSerializer


@login_required
def region_list(request, choice=False):
    data = []
    nextPage = 1
    previousPage = 1
    total_per_page = ROWS_PER_PAGE

    base_url = '/geo/regions?'
    q = request.GET.get('q', '')
    if len(q) > 0:
        base_url = f'{base_url}q={q}'
    regions = Region.objects \
                .filter(
                        Q(title__icontains=q)
                        | Q(nation__title__icontains=q)
                        ) \
                .all() \
                .order_by('pk')

    page = request.GET.get('page', 1)
    paginator = Paginator(regions, total_per_page)
    try:
        data = paginator.page(page)
    except PageNotAnInteger:
        data = paginator.page(1)
    except EmptyPage:
        data = paginator.page(paginator.num_pages)

    serializer = RegionSerializer(data, context={'request': request}, many=True)
    if data.has_next():
        nextPage = data.next_page_number()
    if data.has_previous():
        previousPage = data.previous_page_number()
    
    context = dict(
        title='Regions',
        data=serializer.data,
        count=paginator.count,
        columns=[
                        {'title': 'title', 'width': 35},
                        {'title': 'nation.title', 'width': 35},
                        {'title': 'agent.full_name', 'width': 25},
                        {'title': 'total_votes', 'width': 5, 'type': 'vote_count'},
                        {'title': 'total_presidential_votes', 'width': 5, 'type': 'vote_count'},
                        {'title': 'total_parliamentary_votes', 'width': 5, 'type': 'vote_count'},
                    ],
        numpages=paginator.num_pages,
        next_link='/geo/regions/?page=' + str(nextPage),
        prev_link='/geo/regions/?page=' + str(previousPage)
    )
    return render(request, "geo/region_list.html", context)


@login_required
def region_detail(request, pk=None):
    title='Region'
    list_path =  'region_list'
    detail_path = 'region_detail'
    template = "geo/region_form.html"
    data = get_object_or_404(Region, pk=pk)
    initial = dict(
        pk=data.pk,
        title=data.title,
        nation=data.nation,
        status=data.status,
    )
    form = RegionForm(initial=initial)
    context = dict(
                    pk=pk,
                    title=title,
                    elements=form,
                    list_path=list_path,
                    detail_path=detail_path,
                )
    context['message'] = ''
    if not request.method == "GET":
        error = 1
        form = RegionForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data.get('title', None)
            nation = form.cleaned_data.get('nation', None)
            details = form.cleaned_data.get('details', None)
            status = form.cleaned_data.get('status', None)
            try:
                instance, _ = Region.objects \
                                  .update_or_create(pk=pk,
                                                    defaults=dict(
                                                                title=title,
                                                                nation=nation,
                                                                status=status,
                                                                details=details,)
                                                    )
                context['message'] = FormMessages.SUCCESS
                error = 0
            except Exception as e:
                context['message'] = FormMessages.ERROR
                # TECH NOTES: add logger
                print(e)
        else:
            context['message'] = '{} {}'.format(FormMessages.INVALID_FORM, form.errors)
        
        messages.success(request, context['message'])
        return submit_complete(request, pk=pk, message=context['message'], error=error)
    return render(request, template, context)


@login_required
def submit_complete(request,
                    pk=None,
                    message=None,
                    error=0
                    ):
    title='Region'
    list_path='region_list'
    detail_path='region_detail'
    template = 'geo/region_form.html'
    messages.success(request, message)
    data = get_object_or_404(Region, pk=pk)
    form = RegionForm(dict(
                            pk=data.pk,
                            title=data.title,
                            nation=data.nation,
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

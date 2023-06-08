from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib import messages

from __poll.constants import ROWS_PER_PAGE, FormMessages
from __geo.serializers import ConstituencySerializer
from __geo.forms import ConstituencyForm
from __geo.models import Constituency


@login_required
def constituency_list(request):
    data = []
    nextPage = 1
    previousPage = 1
    total_per_page = ROWS_PER_PAGE

    base_url = '/geo/constituencies?'
    q = request.GET.get('q', '')
    if len(q) > 0:
        base_url = f'{base_url}q={q}'
    constituencies = Constituency.objects \
                                .filter(
                                        Q(title__icontains=q)
                                        | Q(region__title__icontains=q)
                                        | Q(region__nation__title__icontains=q)
                                        ) \
                                .all() \
                                .order_by('pk')

    page = request.GET.get('page', 1)
    paginator = Paginator(constituencies, total_per_page)
    try:
        data = paginator.page(page)
    except PageNotAnInteger:
        data = paginator.page(1)
    except EmptyPage:
        data = paginator.page(paginator.num_pages)

    serializer = ConstituencySerializer(data, context={'request': request}, many=True)
    if data.has_next():
        nextPage = data.next_page_number()
    if data.has_previous():
        previousPage = data.previous_page_number()
    
    context = dict(
        title='Constituencies',
        data=serializer.data,
        count=paginator.count,
        numpages=paginator.num_pages,
        columns=[
            dict(title='title', width=50),
            dict(title='region.title', width=15),
            dict(title='agent.full_name', width=30),
            dict(title='total_votes', width=5, type='vote_count'),
            dict(title='total_presidential_votes', width=5, type='vote_count'),
            dict(title='total_parliamentary_votes', width=5, type='vote_count'),
        ],
        next_link='/geo/constituencies/?page=' + str(nextPage),
        prev_link='/geo/constituencies/?page=' + str(previousPage)
    )
    return render(request, "geo/constituency_list.html", context)


@login_required
def constituency_detail(request, pk=None):
    title='Constituency'
    list_path =  'constituency_list'
    detail_path = 'constituency_detail'
    template = 'geo/constituency_form.html'
    data = get_object_or_404(Constituency, pk=pk)
    initial = dict(
        pk=data.pk,
        title=data.title,
        region=data.region,
        details=data.details,
        status=data.status,
    )
    form = ConstituencyForm(initial=initial)
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
        form = ConstituencyForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data.get('title', None)
            details = form.cleaned_data.get('details', None)
            status = form.cleaned_data.get('status', None)
            region = form.cleaned_data.get('region', None)
            try:
                instance, _ = Constituency.objects \
                                           .update_or_create(pk=pk,
                                                            defaults=dict(
                                                                          title=title,
                                                                          region=region,
                                                                          status=status,
                                                                          details=details,
                                                                          ))
                error = 0
            except Exception as e:
                context['message'] = FormMessages.ERROR
                # TECH NOTES: add logger
                print(e)
            else:
                context['message'] = FormMessages.SUCCESS
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
    title='Constituency'
    list_path='constituency_list'
    detail_path='constituency_detail'
    template = 'geo/constituency_form.html'
    messages.success(request, message)
    data = get_object_or_404(Constituency, pk=pk)
    form = ConstituencyForm(dict(
                                pk=data.pk,
                                title=data.title,
                                region=data.region,
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

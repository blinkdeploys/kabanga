from django.shortcuts import render, get_object_or_404
from __geo.serializers import NationSerializer
from django.urls import reverse
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages

from __poll.constants import ROWS_PER_PAGE, FormMessages
from __geo.forms import NationForm
from __geo.models import Nation


@login_required
def nation_list(request):
    data = []
    nextPage = 1
    previousPage = 1
    total_per_page = ROWS_PER_PAGE
    
    base_url = '/geo/regions?'
    q = request.GET.get('q', '')
    if len(q) > 0:
        base_url = f'{base_url}q={q}'
    nations = Nation.objects \
                .filter(
                        Q(title__icontains=q)
                        ) \
                .all() \
                .order_by('pk')

    page = request.GET.get('page', 1)
    paginator = Paginator(nations, total_per_page)
    try:
        data = paginator.page(page)
    except PageNotAnInteger:
        data = paginator.page(1)
    except EmptyPage:
        data = paginator.page(paginator.num_pages)

    serializer = NationSerializer(data, context={'request': request}, many=True)
    if data.has_next():
        nextPage = data.next_page_number()
    if data.has_previous():
        previousPage = data.previous_page_number()
    
    context = dict(
        title='Nations',
        data=serializer.data,
        count=paginator.count,
        request=request,
        columns=[
                    dict(title='code', width=10),
                    dict(title='title', width=50),
                    dict(title='agent.full_name', width=30),
                    dict(title='total_votes', width=5, type='vote_count'),
                    dict(title='total_presidential_votes', width=5, type='vote_count'),
                    dict(title='total_parliamentary_votes', width=5, type='vote_count'),
                ],
        numpages=paginator.num_pages,
        next_link='/geo/nations/?page=' + str(nextPage),
        prev_link='/geo/nations/?page=' + str(previousPage)
    )
    return render(request, "geo/nation_list.html", context)


@login_required
def nation_detail(request, pk=None):
    title='Nation'
    list_path = 'nation_list'
    detail_path = 'nation_detail'
    template = "geo/nation_form.html"
    messages.get_messages(request)
    data = get_object_or_404(Nation, pk=pk)
    initial = dict(
                    pk=data.pk,
                    code=data.code,
                    title=data.title,
                )
    form = NationForm(initial=initial)
    context = dict(
                    pk=pk,
                    title=title,
                    elements=form,
                    list_path=list_path,
                    detail_path=detail_path,
                    message=None,
                )
    context['message'] = FormMessages.INVALID_FORM
    if not request.method == "GET":
        form = NationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data.get('code', None)
            title = form.cleaned_data.get('title', None)
            try:
                nation_count = Nation.objects.count()
                if nation_count > 0:
                    nation = Nation.objects.update(code=code, title=title)
                else:
                    nation = Nation.objects.create(code=code, title=title)
            except BadHeaderError as e:
                context['message'] = FormMessages.ERROR
                # TECH NOTES: add logger
                print(e)
            else:
                context['message'] = FormMessages.SUCCESS
        messages.success(request, context['message'])
        return redirect(reverse(detail_path, kwargs=dict(pk=pk)), context['message'])
    return render(request, template, context)


@login_required
def submit_complete(request,
                    pk=None,
                    message=None,
                    error=0
                    ):
    title='Nation'
    list_path='nation_list'
    detail_path='nation_detail'
    template = 'geo/nation_form.html'
    messages.success(request, message)
    data = get_object_or_404(Nation, pk=pk)
    form = NationForm(dict(
                           pk=data.pk,
                           title=data.title,
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

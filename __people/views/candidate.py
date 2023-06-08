from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
from __people.models import Candidate, Party
from __poll.models import Position
from __people.serializers import CandidateSerializer
from __people.forms import CandidateForm
from __poll.constants import ROWS_PER_PAGE, FormMessages
from django.db.models import Q
from django.db.models import F, Value, Func
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse


@login_required
def candidate_list(request):
    title='Candidates'
    template = 'people/candidate_list.html'
    base_url = '/people/candidates?'
    data = []
    nextPage = 1
    previousPage = 1
    total_per_page = ROWS_PER_PAGE
    q = request.GET.get('q', '')
    if len(q) > 0:
        base_url = f'{base_url}q={q}'
    qparts = q.split(' ')
    candidates = Candidate.objects \
                          .annotate(full_name_complete = Func(F('prefix'),
                                Value(' '), F('first_name'),
                                Value(' '), F('last_name'),
                                Value(' '), F('other_names'),
                                function= 'CONCAT')) \
                          .filter(
                                Q(prefix__icontains=q)
                                | Q(
                                    Q(prefix__in=qparts)
                                    & Q(first_name__in=qparts)
                                    & Q(last_name__in=qparts)
                                )
                                | Q(first_name__icontains=q)
                                | Q(last_name__icontains=q)
                                | Q(other_names__icontains=q)
                                | Q(party__code__icontains=q)
                                | Q(party__title__icontains=q)
                                | Q(position__title__icontains=q)
                                # Q(prefix__in=qparts)
                                # | Q(first_name__in=qparts)
                                # | Q(last_name__in=qparts)
                                # | Q(other_names__in=qparts)
                                # | Q(party__code__in=qparts)
                                # | Q(party__title__in=qparts)
                                # | Q(position__title__in=qparts)
                          ) \
                          .all() \
                          .order_by('pk')
    page = request.GET.get('page', 1)
    paginator = Paginator(candidates, total_per_page)
    try:
        data = paginator.page(page)
    except PageNotAnInteger:
        data = paginator.page(1)
    except EmptyPage:
        data = paginator.page(paginator.num_pages)

    serializer = CandidateSerializer(data, context={'request': request}, many=True)

    if data.has_next():
        nextPage = data.next_page_number()
    if data.has_previous():
        previousPage = data.previous_page_number()

    context = dict(
        title=title,
        data=serializer.data,
        count=paginator.count,
        numpages=paginator.num_pages,
        columns=[
                dict(title='party.code', width=10),
                dict(title='full_name', width=30),
                dict(title='position.title', width=35),
                dict(title='total_votes', width=10, type='vote_count'),
                ],
        column_widths=[5, None, 15],
        next_link='/people/candidates/?page=' + str(nextPage),
        prev_link='/people/candidates/?page=' + str(previousPage)
    )
    return render(request, template, context)


@login_required
def candidate_detail(request, pk=None):
    title='Candidate'
    list_path = 'candidate_list'
    detail_path = 'candidate_detail'
    template = 'people/candidate_form.html'
    data = get_object_or_404(Candidate, pk=pk)
    initial = {
                'pk': data.pk,
                'photo': data.photo,
                'prefix': data.prefix,
                'first_name': data.first_name,
                'last_name': data.last_name,
                'other_names': data.other_names,
                'description': data.description,
                'position': data.position,
                'party': data.party,
                'status': data.status,
            }
    form = CandidateForm(initial=initial)
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
        form = CandidateForm(request.POST)
        if form.is_valid():
            prefix = form.cleaned_data['prefix']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            other_names = form.cleaned_data['other_names']
            description = form.cleaned_data['description']
            position = form.cleaned_data['position']
            party = form.cleaned_data['party']
            status = form.cleaned_data['status']

            position = Position.objects.filter(pk=position.pk).first()
            party = Party.objects.filter(pk=party.pk).first()

            new_file_uploaded = False
            photo = request.POST.get('photo_file', None)
            if request.FILES:
                new_file_uploaded = True
                photo = request.FILES['photo']    
            defaults = dict(prefix=prefix,
                            first_name=first_name,
                            last_name=last_name,
                            other_names=other_names,
                            description=description,
                            position=position,
                            party=party,
                            status=status,
                            )
            if new_file_uploaded:
                defaults['photo'] = photo

            try:
                instance, _ = Candidate.objects \
                                    .update_or_create(pk=pk,
                                                      defaults=defaults)
                error = 0
                context['form'] = CandidateForm(initial=dict(
                                                            pk=instance.pk,
                                                            prefix=instance.prefix,
                                                            first_name=instance.first_name,
                                                            last_name=instance.last_name,
                                                            other_names=instance.other_names,
                                                            photo=instance.photo,
                                                            description=instance.description,
                                                            position=instance.position,
                                                            party=instance.party,
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
        messages.success(request, context['message'])
        return redirect(reverse(detail_path, kwargs=dict(pk=pk)), context['message'])
    return render(request, template, context)

from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
from __people.models import Agent
from __people.serializers import AgentSerializer
from __people.forms import AgentForm
from __poll.constants import ROWS_PER_PAGE, FormMessages
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.db.models import Q
from django.db.models import F, Value, Func


@login_required
def agent_list(request):
    title='Agents'
    template = 'people/agent_list.html'
    base_url = '/people/agents?'
    data = []
    nextPage = 1
    previousPage = 1
    total_per_page = ROWS_PER_PAGE
    q = request.GET.get('q', '')
    if len(q) > 0:
        base_url = f'{base_url}q={q}'
    qparts = q.split(' ')
    agents = Agent.objects \
                  .annotate(full_name_complete = Func(F('first_name'),
                              Value(' '), F('last_name'),
                              function='CONCAT')) \
                  .filter(
                        Q(
                            Q(first_name__in=qparts)
                            & Q(last_name__in=qparts)
                        )
                        | Q(first_name__icontains=q)
                        | Q(last_name__icontains=q)
                        | Q(email__icontains=q)
                        | Q(phone__icontains=q)
                        | Q(address__icontains=q)
                        # zone, zone_ct, zone_id, status, user
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
    paginator = Paginator(agents, total_per_page)
    try:
        data = paginator.page(page)
    except PageNotAnInteger:
        data = paginator.page(1)
    except EmptyPage:
        data = paginator.page(paginator.num_pages)
    serializer = AgentSerializer(data, context={'request': request}, many=True)
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
                dict(title='full_name', width=30),
                dict(title='zone_type', width=10),
                dict(title='zone_title', width=20),
                dict(title='phone', width=15),
                ],
        column_widths=[5, None, 15],
        next_link='/people/agents/?page=' + str(nextPage),
        prev_link='/people/agents/?page=' + str(previousPage)
    )
    return render(request, template, context)


@login_required
def agent_detail(request, pk=None):
    title='Agent'
    list_path = 'agent_list'
    detail_path = 'agent_detail'
    template = 'people/agent_form.html'
    data = get_object_or_404(Agent, pk=pk)
    initial = {
               'pk': data.pk,
               'zone_ct_id': data.zone_ct.pk,
               'zone_id': data.zone_id,
               'first_name': data.first_name,
               'last_name': data.last_name,
               'email': data.email,
               'phone': data.phone,
               'address': data.address,
               'status': data.status,
              }
    form = AgentForm(initial=initial)
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
        form = AgentForm(request.POST)

        if form.is_valid():
            form_data = form.cleaned_data
            first_name = form_data.get('first_name')
            last_name = form_data.get('last_name')
            email = form_data.get('email')
            phone = form_data.get('phone')
            zone_ct_id = form_data.get('zone_ct_id')
            zone_id = form_data.get('zone_id').pk
            description = form_data.get('description')
            address = form_data.get('address')
            status = form_data.get('status')

            '''
            new_file_uploaded = False
            photo = request.POST.get('photo_file', None)
            if request.FILES:
                new_file_uploaded = True
                photo = request.FILES['photo']
            '''

            defaults = dict(first_name=first_name,
                            last_name=last_name,
                            description=description,
                            email=email,
                            phone=phone,
                            address=address,
                            zone_ct_id=zone_ct_id,
                            zone_id=zone_id,
                            status=status,
                            )
            '''
            if new_file_uploaded:
                defaults['photo'] = photo
            '''

            try:
                instance, _ = Agent.objects \
                                    .update_or_create(pk=pk,
                                                      defaults=defaults)
                error = 0
                context['form'] = AgentForm(initial=dict(
                                                         pk=instance.pk,
                                                         first_name=instance.first_name,
                                                         last_name=instance.last_name,
                                                         email=instance.email,
                                                         address=instance.address,
                                                         zone_ct_id=instance.zone_ct_id,
                                                         zone_id=instance.zone_id,
                                                         description=instance.description,
                                                         # photo=instance.photo,
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

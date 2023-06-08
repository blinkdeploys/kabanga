from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
from __people.models import Party
from __people.serializers import PartySerializer, PartyAsChildSerializer
from __people.forms import PartyForm
from __poll.constants import ROWS_PER_PAGE
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
def party_list(request):
    data = []
    nextPage = 1
    previousPage = 1
    total_per_page = ROWS_PER_PAGE
    party = Party.objects.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(party, total_per_page)
    try:
        data = paginator.page(page)
    except PageNotAnInteger:
        data = paginator.page(1)
    except EmptyPage:
        data = paginator.page(paginator.num_pages)

    serializer = PartyAsChildSerializer(data, context={'request': request}, many=True)
    if data.has_next():
        nextPage = data.next_page_number()
    if data.has_previous():
        previousPage = data.previous_page_number()
    
    context = {
        'title': 'Parties',
        'data': serializer.data,
        'count': paginator.count,
        'numpages' : paginator.num_pages,
        'columns': [
            dict(title='code', width=5),
            dict(title='title', width=45),
            dict(title='result_votes', width=5, type='vote_count'),
            dict(title='total_presidential_votes', width=5, type='vote_count'),
            dict(title='total_parliamentary_votes', width=5, type='vote_count'),
        ],
        'next_link': '/people/parties/?page=' + str(nextPage),
        'prev_link': '/people/parties/?page=' + str(previousPage)
    }
    return render(request, "people/party_list.html", context)


@login_required
def party_detail(request, pk=None):
    data = get_object_or_404(Party, pk=pk)
    initial = {
        'pk': data.pk,
        'code': data.code,
        'title': data.title,
        'status': data.status,
    }
    if request.method == "GET":
        form = PartyForm(initial=initial)
    else:
        form = PartyForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"]
            title = form.cleaned_data["title"]
            party = form.cleaned_data['party']
            try:
                party = Party(code=code, title=title, party=party)
                party.save()
            except BadHeaderError:
                return HttpResponse("Error saving record.")
            return redirect("Record successfully saved")
    return render(request, "people/party_form.html", {"form": form})

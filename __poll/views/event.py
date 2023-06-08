from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
from __poll.models import Event
from __poll.serializers import EventSerializer
from __poll.forms import EventForm
from __poll.constants import ROWS_PER_PAGE


def event_list(request):
    data = []
    nextPage = 1
    previousPage = 1
    total_per_page = ROWS_PER_PAGE
    event = Event.objects.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(event, total_per_page)
    try:
        data = paginator.page(page)
    except PageNotAnInteger:
        data = paginator.page(1)
    except EmptyPage:
        data = paginator.page(paginator.num_pages)

    serializer = EventSerializer(data, context={'request': request}, many=True)
    if data.has_next():
        nextPage = data.next_page_number()
    if data.has_previous():
        previousPage = data.previous_page_number()
    
    context = {
        'title': 'Events',
        'data': serializer.data,
        'count': paginator.count,
        'numpages' : paginator.num_pages,
        'columns': [{'title': 'position.title'}, {'title': 'office'}, {'title': 'title'}, {'title': 'start'}, {'title': 'end'}, {'title': 'status'}],
        'next_link': '/poll/events/?page=' + str(nextPage),
        'prev_link': '/poll/events/?page=' + str(previousPage)
    }
    return render(request, "poll/event_list.html", context)


def event_detail(request, pk=None):
    data = get_object_or_404(Event, pk=pk)
    initial = {
        'pk': data.pk,
        'code': data.code,
        'title': data.title,
        'status': data.status,
    }
    if request.method == "GET":
        form = EventForm(initial=initial)
    else:
        form = EventForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"]
            title = form.cleaned_data["title"]
            event = form.cleaned_data['event']
            try:
                event = Event(code=code, title=title, event=event)
                event.save()
            except BadHeaderError:
                return HttpResponse("Error saving record.")
            return redirect("Record successfully saved")
    return render(request, "poll/event_form.html", {"form": form})


def success_view(request):
    form = EventForm()
    context = {"form": form, "message": "Success! Thank you for your message."}
    return render(request, "poll/event_form.html", context)



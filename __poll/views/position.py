from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
from __poll.models import Position
from __poll.serializers import PositionSerializer
from __poll.forms import PositionForm
from __poll.constants import ROWS_PER_PAGE


def position_list(request):
    data = []
    nextPage = 1
    previousPage = 1
    total_per_page = ROWS_PER_PAGE
    position = Position.objects.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(position, total_per_page)
    try:
        data = paginator.page(page)
    except PageNotAnInteger:
        data = paginator.page(1)
    except EmptyPage:
        data = paginator.page(paginator.num_pages)

    serializer = PositionSerializer(data, context={'request': request}, many=True)
    if data.has_next():
        nextPage = data.next_page_number()
    if data.has_previous():
        previousPage = data.previous_page_number()
    
    context = {
        'title': 'Positions',
        'data': serializer.data,
        'count': paginator.count,
        'numpages' : paginator.num_pages,
        'columns': [
            {'title': 'zone', 'width': 10},
            {'title': 'title', 'width': 40}
        ],
        'next_link': '/poll/positions/?page=' + str(nextPage),
        'prev_link': '/poll/positions/?page=' + str(previousPage)
    }
    return render(request, "poll/position_list.html", context)


def position_detail(request, pk=None):
    data = get_object_or_404(Position, pk=pk)
    initial = dict(
        pk=data.pk,
        title=data.title,
        zone_ct_id=data.zone_ct_id,
        zone_id=data.zone_id,
        details=data.details,
    )
    if request.method == "GET":
        form = PositionForm(initial=initial)
    else:
        form = PositionForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            details = form.cleaned_data["details"]
            zone_ct_id = form.cleaned_data["zone_ct_id"]
            zone_id = form.cleaned_data['zone_id']
            try:
                position = Position(title=title, zone_ct_id=zone_ct_id, zone_id=zone_id, details=details)
                position.save()
            except BadHeaderError:
                return HttpResponse("Error saving record.")
            return redirect("Record successfully saved")
    return render(request, "poll/position_form.html", {"form": form})


def success_view(request):
    form = PositionForm()
    context = {"form": form, "message": "Success! Thank you for your message."}
    return render(request, "poll/position_form.html", context)



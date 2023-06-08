from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
from __poll.models import Office
from __poll.serializers import OfficeSerializer
from __poll.forms import OfficeForm
from __poll.constants import ROWS_PER_PAGE


def office_list(request):
    data = []
    nextPage = 1
    previousPage = 1
    total_per_page = ROWS_PER_PAGE
    office = Office.objects.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(office, total_per_page)
    try:
        data = paginator.page(page)
    except PageNotAnInteger:
        data = paginator.page(1)
    except EmptyPage:
        data = paginator.page(paginator.num_pages)

    serializer = OfficeSerializer(data, context={'request': request}, many=True)
    if data.has_next():
        nextPage = data.next_page_number()
    if data.has_previous():
        previousPage = data.previous_page_number()
    
    context = {
        'title': 'Offices',
        'data': serializer.data,
        'count': paginator.count,
        'numpages' : paginator.num_pages,
        'columns': [
            {'title': 'title'},
            # {'title': 'office_title'}
        ],
        'next_link': '/poll/offices/?page=' + str(nextPage),
        'prev_link': '/poll/offices/?page=' + str(previousPage)
    }
    return render(request, "poll/office_list.html", context)


def office_detail(request, pk=None):
    title='Office Form'
    data = get_object_or_404(Office, pk=pk)
    initial = {
        'pk': data.pk,
        'title': data.title,
    }
    if request.method == "GET":
        form = OfficeForm(initial=initial)
    else:
        form = OfficeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"]
            title = form.cleaned_data["title"]
            office = form.cleaned_data['office']
            try:
                # send_mail(subject, message, from_email, ["admin@example.com"])
                office = Office(code=code, title=title, office=office)
                office.save()
            except BadHeaderError:
                return HttpResponse("Error saving record.")
            return redirect("Record successfully saved")
    return render(request, "poll/office_form.html", {title: title, "form": form})


def success_view(request):
    form = OfficeForm()
    context = {"form": form, "message": "Success! Thank you for your message."}
    return render(request, "poll/office_form.html", context)



from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from __people.models import Party
from __people.serializers import PartySerializer
from __poll.constants import ROWS_PER_PAGE


@api_view(['GET', 'POST'])
def party_list(request):
    """
    List parties or create a new party
    """
    if request.method == "GET":
        data = []
        nextPage = 1
        previousPage = 1
        total_per_page = ROWS_PER_PAGE
        parties = Party.objects.all()
        page = request.GET.get('page', 1)
        paginator = Paginator(parties, total_per_page)
        try:
            data = paginator.page(page)
        except PageNotAnInteger:
            data = paginator.page(1)
        except EmptyPage:
            data = paginator.page(paginator.num_pages)

        serializer = PartySerializer(data, context={'request': request}, many=True)
        if data.has_next():
            nextPage = data.next_page_number()
        if data.has_previous():
            previousPage = data.previous_page_number()
        
        return Response({
            'data': serializer.data,
            'count': paginator.count,
            'numpages' : paginator.num_pages,
            'next_link': '/parties/?page=' + str(nextPage),
            'prev_link': '/parties/?page=' + str(previousPage)
        })
    elif request.method == 'POST':
        serializer = PartySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'POST'])
def party_detail(request, pk):
    """
    Retrieve, update or delete a custumer by id/pk
    """

    try:
        party = Party.objects.get(pk=pk)
    except Party.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = PartySerializer(party, context={'request': request})
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = PartySerializer(party, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        party.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

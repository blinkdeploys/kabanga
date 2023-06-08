from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from __geo.models import Candidate
from __geo.serializers import CandidateSerializer
from __poll.constants import ROWS_PER_PAGE


@api_view(['GET', 'POST'])
def candidate_list(request):
    """
    List candidate or create a new candidate
    """
    if request.method == "GET":
        data = []
        nextPage = 1
        previousPage = 1
        total_per_page = ROWS_PER_PAGE
        candidate = Candidate.objects.all()
        page = request.GET.get('page', 1)
        paginator = Paginator(candidate, total_per_page)
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
        
        return Response({
            'data': serializer.data,
            'count': paginator.count,
            'numpages' : paginator.num_pages,
            'next_link': '/people/candidates/?page=' + str(nextPage),
            'prev_link': '/people/candidates/?page=' + str(previousPage)
        })
    elif request.method == 'POST':
        serializer = CandidateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'POST'])
def candidate_detail(request, pk):
    """
    Retrieve, update or delete a custumer by id/pk
    """

    try:
        candidate = Candidate.objects.get(pk=pk)
    except Candidate.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CandidateSerializer(candidate, context={'request': request})
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = CandidateSerializer(candidate, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        candidate.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

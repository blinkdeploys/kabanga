from django.shortcuts import render

from django.http import HttpRequest
from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes
from rest_framework import status
from django.contrib.auth.decorators import login_required
from rest_framework.renderers import JSONRenderer
from rest_framework.exceptions import MethodNotAllowed
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.db.models import F, Value, Func

from __geo.helpers import apply_query_filter
from __geo.models import Constituency
from __geo.serializers import ConstituencySerializer, ConstituencyChoiceSerializer, ConstituencySubmitSerializer
from __poll.constants import ROWS_PER_PAGE
from django.middleware.csrf import get_token


@login_required
@api_view(['GET', 'POST'])
@renderer_classes([JSONRenderer])
def constituency_choices(request):
    http_request = HttpRequest()
    http_request.method = request.method
    http_request.path = request.path
    http_request.GET = request.GET
    http_request.POST = request.POST
    http_request.META = request.META
    http_request.user = request.user
    http_request.COOKIES = request.COOKIES
    http_request._request = request
    csrf_token = get_token(request)
    http_request.META['CSRF_COOKIE'] = csrf_token
    http_request.META['HTTP_X_CSRFTOKEN'] = csrf_token
    return constituency_list(http_request, **dict(choice=True, paginate=False))


@login_required
@api_view(['GET', 'POST'])
@renderer_classes([JSONRenderer])
def constituency_list(request, **kwargs):
    """
    List constituency or create a new constituency
    """
    choice = kwargs.get('choice')
    paginate = kwargs.get('paginate')
    if request.method in ["GET", "POST"]:
        data = []
        nextPage = 1
        previousPage = 1
        response = {}

        # query set
        rows = Constituency.objects \
                           .all().order_by('pk')
        rows = apply_query_filter(request, rows)
        data = rows

        # paginate: make pages
        if paginate:
            total_per_page = ROWS_PER_PAGE
            page = request.GET.get('page', 1)
            paginator = Paginator(data, total_per_page)
            try:
                data = paginator.page(page)
            except PageNotAnInteger:
                data = paginator.page(1)
            except EmptyPage:
                data = paginator.page(paginator.num_pages)
            response['count'] = paginator.count,
            response['numpages'] = paginator.num_pages,

        serializer = ConstituencySerializer(data, context={'request': request}, many=True)
        if choice:
            serializer = ConstituencyChoiceSerializer(data, context={'request': request}, many=True)
        response['data'] = serializer.data,
        
        # paginate: make pages
        if paginate:
            if data.has_next():
                nextPage = data.next_page_number()
            if data.has_previous():
                previousPage = data.previous_page_number()
            response['next_link'] = '/nations/?page=' + str(nextPage),
            response['prev_link'] = '/nations/?page=' + str(previousPage)

        return Response(response,
                        status=status.HTTP_200_OK,
                        content_type="application/json"
                        )
    raise MethodNotAllowed(request.method)


@login_required
@api_view(['POST'])
@renderer_classes([JSONRenderer])
def constituency_post(request):
    if request.method == 'POST':
        serializer = ConstituencySubmitSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED,
                            content_type="application/json")
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST,
                        content_type="application/json")
    raise MethodNotAllowed(request.method)


@login_required
@api_view(['GET', 'PUT', 'DELETE'])
@renderer_classes([JSONRenderer])
def constituency_detail(request, pk=None):
    """
    Retrieve, update or delete a custumer by id/pk
    """

    try:
        constituency = Constituency.objects.get(pk=pk)
    except Constituency.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND, content_type="application/json")

    if request.method == 'GET':
        serializer = ConstituencySubmitSerializer(constituency, context={'request': request})
        return Response(serializer.data,
                        status=status.HTTP_200_OK,
                        content_type="application/json")

    elif request.method == 'PUT':
        serializer = ConstituencySubmitSerializer(constituency, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_204_NO_CONTENT,
                            content_type="application/json")
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST,
                        content_type="application/json")

    elif request.method == 'DELETE':
        constituency.delete()
        return Response(status=status.HTTP_204_NO_CONTENT,
                        content_type="application/json")

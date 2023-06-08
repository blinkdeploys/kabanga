from django.db.models import Q
from django.db.models import F, Value, Func

def get_queryset_filter(model_name, qparts):
    ins = None
    if type(model_name) == str:
        model_name = model_name.lower()
        if model_name == 'nation':
            ins = Q(code__in=qparts) | Q(title__in=qparts)                
        elif model_name == 'region':
            ins = Q(title__in=qparts)                
        elif model_name == 'constituency':
            ins = Q(title__in=qparts)                
        elif model_name == 'station':
            ins = Q(code__in=qparts) | Q(title__in=qparts)
    if ins:
        for part in qparts:
            ins = ins | Q(title__icontains=part)
        ins = Q(ins)
    return ins

def apply_query_filter(request, queryset):
    if queryset is not None:
        q = request.GET.get('q', '')
        if len(q) > 0:
            qparts = q.strip().split(' ')
            if len(qparts) > 0:
                model_name = queryset.model.__name__
                query_filters = get_queryset_filter(model_name, qparts)
                if query_filters:
                    queryset = queryset.filter(query_filters)
    return queryset
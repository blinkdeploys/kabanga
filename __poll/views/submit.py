from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
def submit_complete_view(request,
                    context={}):
    pk=context.get('pk', 0)
    title=context.get('title', '')
    list_path=context.get('list_path', 'home')
    detail_path=context.get('detail_path', 'home')
    template=context.get('template', '/')
    form=context.get('form', None)
    message=context.get('message', '')
    error=context.get('error', 1)
    messages.success(request, message)
    return render(request,
                  template,
                  dict(
                       pk=pk,
                       title=title,
                       elements=form,
                       list_path=list_path,
                       detail_path=detail_path,
                       error=error,
                       message=message
                    )
                )

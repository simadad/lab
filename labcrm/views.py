from django.shortcuts import render, get_object_or_404, redirect
from .models import LabUser, UserAttr
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
# Create your views here.


@login_required
def user_list(request):
    users = LabUser.objects.all().order_by('user__date_joined')
    return render(request, 'labcrm/user_list.html', {
        'users': users
    })


@login_required
def user_detail(request):
    uid = request.GET.get('uid')
    user = get_object_or_404(LabUser, id=uid)
    print(222222, user, type(user))
    attrs = UserAttr.objects.all()
    attr_option = attrs.filter(is_option=True)
    return render(request, 'labcrm/user_detail.html', {
        'user': user,
        'attrs': attrs,
        'attr_option': attr_option
    })


@login_required
def ques_conf(request):
        attrs = UserAttr.objects.all()
        return render(request, 'labcrm/ques_conf.html', {
            'attrs': attrs
        })


@login_required
def ques_fill(request):
    return render(request, 'labcrm/ques_fill.html')


@login_required
def ques_add(request):
    return render(request, 'labcrm/ques_add.html')


@login_required
def ajax_preview(request, ids):
    return HttpResponse(render(request, 'labcrm/ajax/preview.html', {
        'ids': ids
    }))

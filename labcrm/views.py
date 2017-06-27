from django.shortcuts import render, get_object_or_404, redirect
from .models import LabUser, UserAttr, AttrOption, UserInfoA, UserInfoQ
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
    attrs = UserAttr.objects.all()
    attr_option = attrs.filter(is_option=True)

    if request.method == 'POST':
        questions = request.POST.getlist('tagQuestion')
        answers = request.POST.getlist('tagAnswer')
        print(questions, len(questions))
        print(answers, len(answers))
        for question, answer in zip(questions, answers):
            # 检验是否新增 UserAttr 或 AttrOption
            if question in [attr.attr for attr in attrs]:
                attr = get_object_or_404(UserAttr, attr=question)
                if attr.is_option and answer not in [option.option for option in attr.options.all()]:
                    AttrOption.objects.create(
                        option=answer,
                        attr=attr
                    )
            else:
                attr = UserAttr.objects.create(
                    attr=question
                )
            # 检验是否新增 UserInfoQ
            uiq = UserInfoQ.objects.filter(user=user, attr=attr)[0]
            if uiq is None:
                uiq = UserInfoQ.objects.create(
                    user=user,
                    attr=attr
                )
            # 检验新增 UserInfoA
            UserInfoA.objects.create(
                user=user,
                question=uiq,
                answer=answer
            )
        attrs = UserAttr.objects.all()
        attr_option = attrs.filter(is_option=True)
        # POST
        return HttpResponse(render(request, 'labcrm/ajax_user_detail.html', {
            'user': user,
            'attrs': attrs,
            'attr_option': attr_option
        }))
    # GET
    print(1111111111111, attr_option)
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
def ajax_conf_preview(request, ids):
    return HttpResponse(render(request, 'labcrm/ajax/preview.html', {
        'ids': ids
    }))


@login_required
def ajax_detail_modify(request):
    uid = request.GET.get('uid')
    attrs = UserAttr.objects.all()
    user = get_object_or_404(LabUser, id=uid)
    attrs = UserAttr.objects.all()
    attr_option = attrs.filter(is_option=True)
    # if request.method == 'POST':
    #     questions = request.POST.getlist('tagQuestion')
    #     answers = request.POST.getlist('tagAnswer')
    #     for item in zip(questions, answers):
    #         if item[0] in [attr.attr for attr in attrs]:

    return HttpResponse('aaaa')

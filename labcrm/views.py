from django.shortcuts import render, get_object_or_404, redirect
from .models import LabUser, UserAttr, AttrOption, UserInfoA, UserInfoQ, Dialog
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
# Create your views here.


def _save_new_detail(user, attr, answer):
    uiq, _ = UserInfoQ.objects.get_or_create(
        user=user, attr=attr
    )
    uias = UserInfoA.objects.filter(
        user=user, question=uiq, is_del=False
    )
    for uia in uias:
        uia.is_del = True
        uia.save()
    uia, _ = UserInfoA.objects.get_or_create(
        user=user, question=uiq, answer=answer
    )
    uia.is_del = False
    uia.save()
    return uiq


@login_required
def user_list(request):
    users = LabUser.objects.all().order_by('user__date_joined')
    return render(request, 'labcrm/user_list.html', {
        'users': users
    })


@login_required
def user_detail(request):
    uid = request.GET.get('uid')
    lab_user = get_object_or_404(LabUser, id=uid)
    dialogs = Dialog.objects.filter(user=lab_user)
    user_answers = UserInfoA.objects.filter(user=lab_user, is_del=False)
    attrs = UserAttr.objects.all()
    attr_option = attrs.filter(is_option=True)

    if request.method == 'GET' and request.GET.get('ajax') is None:
        return render(request, 'labcrm/user_detail.html', {
            'lab_user': lab_user,
            'attrs': attrs,
            'attr_option': attr_option,
            'answers': user_answers,
            'dialogs': dialogs
        })

    elif request.method == 'POST':
        dialog = request.POST.get('dialog')
        if dialog is not None:
            user = request.user
            Dialog.objects.create(
                dialog=dialog,
                user=lab_user,
                recorder=user
            )
            dialogs = Dialog.objects.filter(user=lab_user)
        else:
            print(2222222)
            questions = request.POST.getlist('tagQuestion')
            answers = request.POST.getlist('tagAnswer')
            info = dict(zip(questions, answers))
            # 已存在有选项的属性
            for question in set(questions) & {attr.attr for attr in attr_option}:
                attr = get_object_or_404(UserAttr, attr=question)
                print(33333)
                if info[question] not in [option.option for option in attr.options.all()]:
                    AttrOption.objects.create(
                        option=info[question],
                        attr=attr
                    )
                _save_new_detail(lab_user, attr, info[question])
            # 已存在无选项的属性
            for question in set(questions) & {attr.attr for attr in attrs} - {attr.attr for attr in attr_option}:
                attr = get_object_or_404(UserAttr, attr=question)
                print(44444)
                _save_new_detail(lab_user, attr, info[question])
            # 新属性
            for question in set(questions) - {attr.attr for attr in attrs}:
                attr = UserAttr.objects.create(
                    attr=question
                )
                _save_new_detail(lab_user, attr, info[question])
            # 被删除的属性
            for question in {question.attr.attr for question in lab_user.questions.filter(is_del=False)} - set(questions):
                attr = get_object_or_404(UserAttr, attr=question)
                print(555555555)
                print(question, attr)
                uiq = get_object_or_404(UserInfoQ, user=lab_user, attr=attr, is_del=False)
                print(66666)
                uiq.is_del = True
                uiq.save()
                uia = get_object_or_404(UserInfoA, user=lab_user, question=uiq, is_del=False)
                print(77777)
                uia.is_del = True
                uia.save()
            attrs = UserAttr.objects.all()
            attr_option = attrs.filter(is_option=True)
            user_answers = UserInfoA.objects.filter(user=lab_user, is_del=False)
    # POST and cancel
    return HttpResponse(render(request, 'labcrm/ajax_user_detail.html', {
        'labUser': lab_user,
        'attrs': attrs,
        'attr_option': attr_option,
        'answers': user_answers,
        'dialogs': dialogs
    }))


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
def ajax_conf_preview(request):
    attr_ids = request.POST.getlist('attr_checked')
    attrs = [get_object_or_404(UserAttr, id=aid) for aid in attr_ids]
    return HttpResponse(render(request, 'labcrm/ajax/preview.html', {
        'attrs': attrs
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

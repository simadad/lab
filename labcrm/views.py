from django.shortcuts import render, get_object_or_404, redirect
# from .models import LabUser, UserAttr, AttrOption, UserInfoA, UserInfoQ, Dialog, Paper
from .models import *
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from django import forms
from collections import namedtuple
from PIL import Image
import base64
import pymysql
import random
import datetime
# Create your views here.

picType = {
    'dialog': 'Dialog'
}
QuesTuple = namedtuple('QuesTuple', ['desc', 'aid', 'attr'])
QuesTuple2 = namedtuple('QuesTuple', ['desc', 'aid', 'attr', 'value'])


def _save_uiq_uia(user, attr, answer):
    # 保存用户属性、值
    uiq, _ = UserInfoQ.objects.get_or_create(
        user=user, attr=attr
    )
    uia, is_new = UserInfoA.objects.get_or_create(
        user=user,
        question=uiq,
        is_del=False,
        defaults={'answer': answer}
    )
    if not is_new:
        uia.is_del = True
        uia.save()
        UserInfoA.objects.create(
            user=user,
            question=uiq,
            answer=answer
        )
    return uiq


@login_required
def user_list(request):
    if request.method == 'POST':
        nickname = request.POST.get('nickname')
        wechat = request.POST.get('wechat')
        try:
            user = User.objects.create_user(nickname)
        except IntegrityError as e:
            users = LabUser.objects.all().filter(is_del=False).order_by('-user__date_joined')
            return render(request, 'labcrm/user_list.html', {
                'users': users,
                'repeat': True
            })
        new_lab_user = LabUser.objects.create(
            user=user,
            nickname=nickname,
            wechat=wechat,
        )
        return redirect('crm:detail2', new_id=new_lab_user.id)
    users = LabUser.objects.all().filter(is_del=False).order_by('-user__date_joined')
    return render(request, 'labcrm/user_list.html', {
        'users': users
    })


class ImgForm(forms.Form):
    pic = forms.ImageField()


@login_required
def user_detail(request, new_id=None):
    attrs = UserAttr.objects.all()
    attr_option = attrs.filter(is_option=True)
    if not new_id:
        new_id = request.GET.get('uid')
    lab_user = get_object_or_404(LabUser, id=new_id)
    dialogs = Dialog.objects.filter(user=lab_user).order_by('-log_time')
    pics = UserPic.objects.filter(user=lab_user, pic_type=picType['dialog'])
    user_answers = UserInfoA.objects.filter(user=lab_user, is_del=False)

    if request.method == 'GET' and request.GET.get('ajax') is None:
        print('GET: user_detail')
        print('labUser: ', lab_user)
        print('attrs: ', attrs)
        print('attr_option: ', attr_option)
        print('answers: ',  user_answers)
        print('dialogs-len: ', len(dialogs))
        print('pics-len: ', len(pics))
        print('===================')
        return render(request, 'labcrm/user_detail.html', {
            'labUser': lab_user,
            'attrs': attrs,
            'attr_option': attr_option,
            'answers': user_answers,
            'dialogs': dialogs,
            'pics': pics,
        })

    elif request.method == 'POST':
        dialog = request.POST.get('dialog')
        pic_post = request.POST.get('pic')
        pic_name = request.POST.get('pic_name')
        print('pic: ', pic_post)
        print('dialog is not None: ', dialog is not None)
        print('dialog: ', dialog)
        print('dialog is True: ', dialog is True)
        if dialog:
            print('POST: user_detail-dialog')
            user = request.user
            Dialog.objects.create(
                dialog=dialog,
                user=lab_user,
                recorder=user
            )
            dialogs = Dialog.objects.filter(user=lab_user).order_by('-log_time')
            pic_form = ImgForm(request.POST, request.FILES)
            print('pic_form: ', pic_form)
            if pic_form.is_valid():
                pic = pic_form.cleaned_data['pic']
                print('pic: ', pic)
                image = Image.open(pic)
                print('image: ', image)
                name = picType['dialog'] + '-' + lab_user.nickname + '-' +\
                       datetime.datetime.now().strftime('%Y-%m-%d') + '.' + pic_name.split('.')[-1]
                image.save('media/img/gallery/%s' % name)
                pic_obj, _ = PicData.objects.get_or_create(pic=pic, defaults={
                    'name': name
                })
                print('pic_obj: ', pic_obj)
                UserPic.objects.create(
                    user=lab_user,
                    pic=pic_obj,
                    pic_type=picType['dialog']
                )
                pics = UserPic.objects.filter(user=lab_user, pic_type=picType['dialog'])
        if not dialog and not pic_post:
            print(2222222)
            questions = request.POST.getlist('tagQuestion')
            answers = request.POST.getlist('tagAnswer')
            info = dict(zip(questions, answers))
            # 已存在有选项的属性
            for question in set(questions) & {attr.attr for attr in attr_option}:
                attr = get_object_or_404(UserAttr, attr=question)
                print(33333)
                # 保存新选项
                if info[question] not in [option.option for option in attr.options.all()]:
                    AttrOption.objects.create(
                        option=info[question],
                        attr=attr
                    )
                _save_uiq_uia(lab_user, attr, info[question])
            # 已存在无选项的属性
            for question in set(questions) & {attr.attr for attr in attrs} - {attr.attr for attr in attr_option}:
                attr = get_object_or_404(UserAttr, attr=question)
                print(44444)
                _save_uiq_uia(lab_user, attr, info[question])
            # 新属性
            for question in set(questions) - {attr.attr for attr in attrs}:
                attr = UserAttr.objects.create(
                    attr=question
                )
                _save_uiq_uia(lab_user, attr, info[question])
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
    else:
        print('GET-ajax: modify_cancel')
    # POST and cancel
    print('====================')
    return HttpResponse(render(request, 'labcrm/ajax_user_detail.html', {
        'labUser': lab_user,
        'attrs': attrs,
        'attr_option': attr_option,
        'answers': user_answers,
        'dialogs': dialogs,
        'pics': pics
    }))


@login_required
def ques_conf(request):
    if request.method == 'POST':
        # 预览 or 生成
        title = request.POST.get('paper_title')
        lab_user = request.POST.get('labUser')
        paper_desc = request.POST.get('paper_desc')
        ques_desc = request.POST.getlist('ques_desc')
        attr_ids = request.POST.getlist('attr_id')
        if request.POST.get('is_cre'):
            print('POST: ques_conf 生成问卷')
            data = '@@'.join([title, lab_user, paper_desc, '##'.join(ques_desc), '##'.join(attr_ids)])
            key = random.randint(100000000, 999999999)
            user = get_object_or_404(LabUser, nickname=lab_user)
            Paper.objects.create(
                user=user,
                key=key,
                data=data
            )
            data_key = str(key) + str(user.id)
            print('data: ', data)
            print('--------------')
            return redirect('crm:fill', data_key=data_key)
        else:
            print('POST: ques_conf 预览问卷')
            # attrs = UserAttr.objects.filter(id__in=attr_ids)
            attrs = [get_object_or_404(UserAttr, id=aid) for aid in attr_ids]
            # ques_value = request.POST.getlist('ques_value')
            quests = zip(ques_desc, attr_ids, attrs)
            quests = sorted(quests, key=lambda x: x[2].is_option, reverse=True)

            def questions():
                for ques in quests:
                    print('ques: ', ques)
                    yield QuesTuple(*ques)
                print('===================')

            return HttpResponse(render(request, 'labcrm/ques_to_fill.html', {
                'title': title,
                'labUser': lab_user,
                'paper_desc': paper_desc,
                'is_fill': False,
                'questions': questions(),
                'questions2': questions()
            }))
    print('GET: ques_conf 配置页面')
    attrs = UserAttr.objects.all()
    print('=================')
    return render(request, 'labcrm/ques_conf.html', {
        'attrs': attrs,
    })


def ques_fill(request, data_key=None):
    key = data_key[:9]
    uid = data_key[9:]
    paper = get_object_or_404(Paper, user=uid, key=key)
    title, lab_user, paper_desc, ques_desc_str, ques_ids_str = paper.data.split('@@')
    ques_desc = ques_desc_str.split('##')
    attr_ids = ques_ids_str.split('##')
    # attrs = UserAttr.objects.filter(id__in=attr_ids)
    attrs = [get_object_or_404(UserAttr, id=aid) for aid in attr_ids]
    if request.method == 'POST':
        print('POST: ques_fill')
        user = get_object_or_404(LabUser, nickname=lab_user, is_del=False)
        ques_values = [request.POST.get('ques_value' + aid) for aid in attr_ids]
        data = '@@'.join(
            [title, lab_user, paper_desc, '##'.join(ques_desc), '##'.join(attr_ids), '##'.join(ques_values)])
        key = random.randint(100000000, 999999999)
        paper_time = datetime.datetime.now()
        print('data: ', data)
        Paper.objects.create(
            user=user,
            key=key,
            data=data,
            is_fill=True,
            finished_time=paper_time
        )
        quests = zip(attrs, ques_values)
        for ques in quests:
            attr, value = ques
            _save_uiq_uia(user, attr, value)
        print('====================')
        return render(request, 'labcrm/fill_success.html')

    quests = zip(ques_desc, attr_ids, attrs)
    quests = sorted(quests, key=lambda x: x[2].is_option, reverse=True)
    print('GET: ques_fill')
    print('data: ', paper.data)
    print('====================')
    def questions():
        for ques in quests:
            yield QuesTuple(*ques)

    return HttpResponse(render(request, 'labcrm/ques_to_fill.html', {
        'title': title,
        'labUser': lab_user,
        'paper_desc': paper_desc,
        'data_key': data_key,
        'is_fill': True,
        'questions': questions(),
    }))


def paper_display(request):
    if request.method == 'GET':
        print('GET: paper_display')
        data_key = request.GET.get('data_key')
        key = data_key[:9]
        uid = data_key[9:]
        paper = get_object_or_404(Paper, user=uid, key=key)
        modal_display = False
        # title, lab_user, paper_desc, ques_desc_str, ques_ids_str, ques_values_str = paper.data.split('@@')
        data = paper.data.split('@@')
        if len(data) == 6:
            title, lab_user, paper_desc, ques_desc_str, ques_ids_str, ques_values_str = data
            ques_values = ques_values_str.split('##')
            paper_time = paper.finished_time
        else:
            title, lab_user, paper_desc, ques_desc_str, ques_ids_str = data
            ques_values = None
            paper_time = paper.create_time
        ques_desc = ques_desc_str.split('##')
        attr_ids = ques_ids_str.split('##')
        if not ques_values:
            ques_values = ['']*len(attr_ids)
    else:
        print('POST: paper_display')
        data_key = request.POST.get('data_key')
        # attr_ids = request.POST.getlist('attr_id')
        key = data_key[:9]
        uid = data_key[9:]
        paper = get_object_or_404(Paper, user=uid, key=key)
        title, lab_user, paper_desc, ques_desc_str, ques_ids_str = paper.data.split('@@')
        # attrs = UserAttr.objects.filter(id__in=attr_ids)
        user = get_object_or_404(LabUser, nickname=lab_user, is_del=False)
        # ques_values = request.POST.getlist('ques_value')
        ques_desc = ques_desc_str.split('##')
        attr_ids = ques_ids_str.split('##')
        ques_values = [request.POST.get('ques_value'+aid) for aid in attr_ids]
        # data = '@@'.join([title, lab_user, paper_desc, '##'.join(ques_desc), '##'.join(attr_ids), '##'.join(ques_values)])
        # key = random.randint(100000000, 999999999)
        paper_time = False
        modal_display = True
        # Paper.objects.create(
        #     user=user,
        #     key=key,
        #     data=data,
        #     is_fill=True,
        #     finished_time=paper_time
        # )
    attrs = [get_object_or_404(UserAttr, id=aid) for aid in attr_ids]
    quests = zip(ques_desc, attr_ids, attrs, ques_values)
    quests = sorted(quests, key=lambda x: x[2].is_option, reverse=True)

    def questions():
        for ques in quests:
            print('paper-ques: ', ques)
            yield QuesTuple2(*ques)
        print('====================')

    return HttpResponse(render(request, 'labcrm/paper_display.html', {
        'title': title,
        'labUser': lab_user,
        'paper_desc': paper_desc,
        'data_key': data_key,
        'modal_display': modal_display,
        'questions': questions(),
        'paper_time': paper_time
    }))


@login_required
def link_to_class(request):
    uid = request.GET.get('uid')
    user = get_object_or_404(LabUser, id=uid)
    if user.class_id:
        cid = user.class_id
    else:
        db = pymysql.connect('47.93.61.70', 'markdev', 'mark2017', 'codeclass', charset="utf8")
        cur = db.cursor()
        cur.execute('''
            SELECT id FROM auth_user user
            WHERE user.username = '{username}'
        '''.format(username=user.nickname))
        cid = cur.fetchone()
        if cid:
            cid = cid[0]
            user.class_id = cid
            user.save()
        else:
            return redirect('crm:list')
    url = 'http://crossincode.com/crm/info/?sid=' + str(cid)
    return redirect(url)


@login_required
def ajax_conf_add(request):
    attr = request.POST.get('attr')
    is_option = request.POST.get('is_option')
    # is_preview = request.POST.get('is_preview')
    # print('attr-option-preview: ', attr, is_option, is_preview)
    print('attr-option: ', attr, is_option)
    if is_option:
        attr, _ = UserAttr.objects.update_or_create(attr=attr, defaults={
            'is_option': True
        })
        options = request.POST.getlist('options')
        print('options: ', options)
        for option in options:
            print('attr-option: ', attr, option)
            AttrOption.objects.get_or_create(
                attr=attr,
                option=option
            )
    else:
        attr, _ = UserAttr.objects.update_or_create(attr=attr, defaults={
            'is_option': False
        })
    # attr_ids = request.POST.getlist('attr_checked')
    # attr_ids.append(attr.id)
    # print('attr_ids: ', attr_ids)
    # attrs = UserAttr.objects.filter(id__in=attr_ids).order_by('-is_option')
    return render(request, 'labcrm/ques_add.html', {
        # 'attrs': attrs,
        'attr': attr,
        # 'is_preview': is_preview
    })


@login_required
def ajax_conf_preview(request):
    print('aaaaaaaaaaaaaa', request.POST.getlist('aaa'))
    attr_ids = request.POST.getlist('attr_checked')
    print(attr_ids)
    attrs = UserAttr.objects.filter(id__in=attr_ids).order_by('-is_option')
    users = LabUser.objects.all().filter(is_del=False).order_by('-user__date_joined')
    return HttpResponse(render(request, 'labcrm/ajax/preview.html', {
        'attrs': attrs,
        'users': users
    }))

'''
@login_required
def ajax_detail_modify(request):
    uid = request.GET.get('uid')
    attrs = UserAttr.objects.all()
    user = get_object_or_404(LabUser, id=uid, is_del=False)
    attrs = UserAttr.objects.all()
    attr_option = attrs.filter(is_option=True)
    # if request.method == 'POST':
    #     questions = request.POST.getlist('tagQuestion')
    #     answers = request.POST.getlist('tagAnswer')
    #     for item in zip(questions, answers):
    #         if item[0] in [attr.attr for attr in attrs]:

    return HttpResponse('aaaa')
'''


@login_required
def ajax_user_del(request):
    userId = request.POST.getlist('userId')
    print('userId: ', userId)
    users = LabUser.objects.filter(id__in=userId)
    for user in users:
        user.is_del = True
        user.save()
    users = LabUser.objects.all().filter(is_del=False).order_by('-user__date_joined')
    return render(request, 'labcrm/ajax/user_del.html', {
        'users': users
    })

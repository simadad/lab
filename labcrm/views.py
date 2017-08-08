from django.shortcuts import render, get_object_or_404, redirect
# from .models import LabUser, UserAttr, AttrOption, UserInfoA, UserInfoQ, Dialog, Paper
from .models import *
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
# from django.db.utils import IntegrityError
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
markPaper = {
    'tofill': 'TF',
    'default': 'DF'
}
QuesTuple = namedtuple('QuesTuple', ['desc', 'aid', 'attr'])
QuesTuple2 = namedtuple('QuesTuple', ['desc', 'aid', 'attr', 'value'])


def _save_uiq_uia(user, attr, answer):
    # 保存用户属性、值
    print('MODE: save')
    uiq, _ = UserInfoQ.objects.get_or_create(
        user=user, attr=attr
    )
    uia, is_new = UserInfoA.objects.get_or_create(
        user=user,
        question=uiq,
        is_del=False,
        defaults={'answer': answer}
    )
    print('uiq-uia-is_new_uia: ', uiq, uia, is_new)
    if not is_new:
        uia.is_del = True
        uia.save()
        UserInfoA.objects.create(
            user=user,
            question=uiq,
            answer=answer
        )
    print('---------------')
    return uiq


@login_required
def user_list(request):
    if request.method == 'POST':
        nickname = request.POST.get('nickname')
        wechat = request.POST.get('wechat')
        username = request.POST.get('username')
        user, is_new = User.objects.get_or_create(username=nickname)
        print('POST: user_list')
        print('nickname wechat username is_new: ', nickname, wechat, username, is_new)
        if username:
            print('@添加用户名')
            LabUser.objects.filter(user__username=nickname).update(nickname=username)
            users = LabUser.objects.all().filter(is_del=False).order_by('-user__date_joined')
            return render(request, 'labcrm/ajax/user_del.html', {
                'users': users
            })
        elif not is_new:
            print('@昵称重复')
        # try:
        #     user = User.objects.create_user(nickname)
        # except IntegrityError as e:
        #     users = LabUser.objects.all().filter(is_del=False).order_by('-user__date_joined')
            print('====================')
            # return render(request, 'labcrm/user_list.html', {
            #     'users': users,
            #     'repeat': True
            # })
            return HttpResponse()
        else:
            print('@添加新用户')
            new_lab_user = LabUser.objects.create(
                user=user,
                # nickname=nickname,
                wechat=wechat,
            )
            print('========================')
            # return redirect('crm:detail2', new_id=new_lab_user.id)
            return HttpResponse(render(request, 'labcrm/ajax/user_add.html', {
                'lab_user': new_lab_user,
            }))
    else:
        print('GET: user_list')
        wechat = request.GET.get('wechat')
        uid = request.GET.get('uid')
        print('wechat-uid: ', wechat, uid)
        LabUser.objects.filter(id=uid).update(wechat=wechat)
    users = LabUser.objects.all().filter(is_del=False).order_by('-user__date_joined')
    print('==================')
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
        print('\nPOST: user_detail')
        dialog = request.POST.get('dialog')
        pic_post = request.POST.get('pic')
        pic_name = request.POST.get('pic_name')
        questions = request.POST.getlist('tagQuestion')
        answers = request.POST.getlist('tagAnswer')
        print('pic_name is-dialog is-ques is-answ: ', pic_name, dialog is True, questions is True, answers is True)
        if dialog:
            print('POST: user_detail-dialog')
            user = request.user
            Dialog.objects.create(
                dialog=dialog,
                user=lab_user,
                recorder=user
            )
            print('dialog-len: ', len(dialog))
            dialogs = Dialog.objects.filter(user=lab_user).order_by('-log_time')
            print('-------------')
        pic_form = ImgForm(request.POST, request.FILES)
        print('pic_form.is_valid(): ', pic_form.is_valid())
        if pic_form.is_valid():
            print('POST: user_detail-pic')
            pic = pic_form.cleaned_data['pic']
            print('pic: ', pic)
            image = Image.open(pic)
            print('image: ', image)
            name = picType['dialog'] + '-' + lab_user.user.username + '-' +\
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
            print('---------------------')
        if questions and answers:
            print('POST: user_detial-modify')
            info = dict(zip(questions, answers))
            print('info: ', info)
            # 已存在有选项的属性
            for question in set(questions) & {attr.attr for attr in attr_option}:
                print('MODE: option-ques')
                attr = get_object_or_404(UserAttr, attr=question)
                print('question: ', question)
                # 保存新选项
                if info[question] not in [option.option for option in attr.options.all()]:
                    print('new-question-option: ', question, info[question])
                    AttrOption.objects.create(
                        option=info[question],
                        attr=attr
                    )
                _save_uiq_uia(lab_user, attr, info[question])
            # 已存在无选项的属性
            for question in set(questions) & {attr.attr for attr in attrs} - {attr.attr for attr in attr_option}:
                print('MODE: no-option')
                attr = get_object_or_404(UserAttr, attr=question)
                print('question: ', question)
                _save_uiq_uia(lab_user, attr, info[question])
            # 新属性
            for question in set(questions) - {attr.attr for attr in attrs}:
                print('MODE: new-attr')
                attr = UserAttr.objects.create(
                    attr=question
                )
                print('question: ', question)
                _save_uiq_uia(lab_user, attr, info[question])
            # 被删除的属性
            for question in {question.attr.attr for question in lab_user.questions.filter(is_del=False)} - set(questions):
                print('MODE: ques-del')
                attr = get_object_or_404(UserAttr, attr=question)
                uiq = get_object_or_404(UserInfoQ, user=lab_user, attr=attr, is_del=False)
                uiq.is_del = True
                uiq.save()
                uia = get_object_or_404(UserInfoA, user=lab_user, question=uiq, is_del=False)
                uia.is_del = True
                uia.save()
                print('ques-uiq-uia: ', question, uiq, uia)
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
        mark = request.POST.get('mark')     # TODO 增加返回字段 Mark
        if not mark:
            mark = markPaper['default']
        print('mark: ', mark)
        if request.POST.get('is_cre'):
            print('POST: ques_conf 生成问卷')
            # data = '@@'.join([title, lab_user, paper_desc, '##'.join(ques_desc), '##'.join(attr_ids)])
            data = '@@'.join([title, paper_desc, '##'.join(ques_desc), '##'.join(attr_ids)])
            key = random.randint(100000000, 999999999)
            # user = get_object_or_404(LabUser, nickname=lab_user)
            # user = get_object_or_404(LabUser, user__username=lab_user)
            print('lab_user-data-key: ', lab_user, data, key)
            Paper.objects.create(
                key=key,
                data=data,
                mark=mark
            )
            if lab_user:
                user0, _ = User.objects.get_or_create(username=lab_user)
                user, _ = LabUser.objects.get_or_create(
                    user=user0
                )
                key = random.randint(100000000, 999999999)
                Paper.objects.create(
                    user=user,
                    key=key,
                    data=data,
                    mark=markPaper['tofill'] + '-' + mark
                )
                data_key = str(key) + str(user.id)
                print('data_key: ', data_key)
                print('===========================')
                return redirect('crm:fill', data_key=data_key)
            data_key = str(key)
            print('data_key: ', data_key)
            print('=============================')
            return redirect('crm:paper2', data_key=data_key)
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
                'mark': mark,
                'questions': questions(),
                'questions2': questions()
            }))
    aid = request.GET.get('attrDel')
    if aid:
        attr = get_object_or_404(UserAttr, id=aid)
        attr.is_del = True
        attr.save()
        return HttpResponse('T')
    print('GET: ques_conf 配置页面')
    attrs = UserAttr.objects.filter(is_del=False)
    papers = Paper.objects.filter(user__isnull=True).order_by('-create_time')
    print('=================')
    return render(request, 'labcrm/ques_conf.html', {
        'attrs': attrs,
        'papers': papers[:10]
    })


def ques_fill(request, data_key=None):
    key = data_key[:9]
    uid = data_key[9:]
    paper = get_object_or_404(Paper, user=uid, key=key)
    mark = paper.mark.lstrip(markPaper['tofill'])
    # title, lab_user, paper_desc, ques_desc_str, ques_ids_str = paper.data.split('@@')
    title, paper_desc, ques_desc_str, ques_ids_str = paper.data.split('@@')
    ques_desc = ques_desc_str.split('##')
    attr_ids = ques_ids_str.split('##')
    # attrs = UserAttr.objects.filter(id__in=attr_ids)
    attrs = [get_object_or_404(UserAttr, id=aid) for aid in attr_ids]
    user = get_object_or_404(LabUser, id=uid)
    if request.method == 'POST':
        print('POST: ques_fill')
        # user = get_object_or_404(LabUser, nickname=lab_user, is_del=False)
        ques_values = [request.POST.get('ques_value' + aid) for aid in attr_ids]
        data = '@@'.join(
            # [title, lab_user, paper_desc, '##'.join(ques_desc), '##'.join(attr_ids), '##'.join(ques_values)])
            [title, paper_desc, '##'.join(ques_desc), '##'.join(attr_ids), '##'.join(ques_values)])
        print('data: ', data)
        paper.user = user
        paper.data = data
        paper.is_fill = True
        paper.mark = user.user.username + mark
        paper.finished_time = datetime.datetime.now()
        paper.save()
        # Paper.objects.create(
        #     user=user,
        #     key=random.randint(100000000, 999999999),
        #     data=data,
        #     is_fill=True,
        #     mark=user.user.username + mark,
        #     finished_time=datetime.datetime.now()
        # )
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
        'labUser': user,
        'paper_desc': paper_desc,
        'data_key': data_key,
        'is_fill': True,
        'questions': questions(),
    }))


def paper_display(request, data_key=None):
    if request.method == 'GET':
        new_paper_name = request.GET.get('reName')
        modal_display = False
        if not data_key:
            data_key = request.GET.get('data_key')
        print('GET: paper_display')
        print(data_key)
        key = data_key[:9]
        if len(data_key) > 9:
            uid = data_key[9:]
            lab_user = get_object_or_404(LabUser, id=uid)
        else:
            lab_user = None
        paper = get_object_or_404(Paper, key=key)
        if new_paper_name:
            paper.mark = new_paper_name
            paper.save()
            return HttpResponse(paper.__str__())
        data = paper.data.split('@@')
        if len(data) == 5:
            # title, lab_user, paper_desc, ques_desc_str, ques_ids_str, ques_values_str = data
            title, paper_desc, ques_desc_str, ques_ids_str, ques_values_str = data
            ques_values = ques_values_str.split('##')
            # paper_time = paper.finished_time
            filled = True
        else:
            filled = False
            # title, lab_user, paper_desc, ques_desc_str, ques_ids_str = data
            title, paper_desc, ques_desc_str, ques_ids_str = data
            ques_values = None
            # paper_time = paper.create_time
        ques_desc = ques_desc_str.split('##')
        attr_ids = ques_ids_str.split('##')
        if not ques_values:
            ques_values = ['']*len(attr_ids)
    else:
        print('POST: paper_display')
        data_key = request.POST.get('data_key')
        # attr_ids = request.POST.getlist('attr_id')
        key = data_key[:9]
        if len(data_key) > 9:
            uid = data_key[9:]
            lab_user = get_object_or_404(LabUser, id=uid)
        else:
            lab_user = None
        paper = get_object_or_404(Paper, user=uid, key=key)
        # title, lab_user, paper_desc, ques_desc_str, ques_ids_str = paper.data.split('@@')
        title, paper_desc, ques_desc_str, ques_ids_str = paper.data.split('@@')
        # attrs = UserAttr.objects.filter(id__in=attr_ids)
        # user = get_object_or_404(LabUser, nickname=lab_user, is_del=False)
        # user = get_object_or_404(LabUser, user__username=lab_user, is_del=False)
        # ques_values = request.POST.getlist('ques_value')
        ques_desc = ques_desc_str.split('##')
        attr_ids = ques_ids_str.split('##')
        ques_values = [request.POST.get('ques_value'+aid) for aid in attr_ids]
        # data = '@@'.join([title, lab_user, paper_desc, '##'.join(ques_desc), '##'.join(attr_ids), '##'.join(ques_values)])
        # key = random.randint(100000000, 999999999)
        # paper_time = False
        modal_display = True
        filled = False
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

    users = LabUser.objects.all().filter(is_del=False).order_by('-user__date_joined')
    return HttpResponse(render(request, 'labcrm/paper_display.html', {
        'title': title,
        'labUser': lab_user,
        'paper_desc': paper_desc,
        'data_key': data_key,
        'modal_display': modal_display,
        'questions': questions(),
        'paper': paper,
        'filled': filled,
        'users': users
    }))


@login_required
def papers_create(request):
    paper_type = request.GET.get('PType')
    pid = request.GET.get('paperDel')
    if paper_type:
        if paper_type == 'M':
            papers = Paper.objects.filter(is_fill=False, user__isnull=True, is_del=False).order_by('-create_time')
        elif paper_type == 'TF':
            papers = Paper.objects.filter(is_fill=False, user__isnull=False, is_del=False).order_by('-create_time')
        elif paper_type == 'F':
            papers = Paper.objects.filter(is_fill=True, is_del=False).order_by('-create_time')
        elif paper_type == 'A':
            papers = Paper.objects.filter(is_del=False).order_by('-create_time')
        # return HttpResponse(render(request, 'labcrm/ajax/papers.html', {
        #     'papers': papers
        # }))
    elif pid:
        get_object_or_404(Paper, id=pid).delete()
        return HttpResponse('T')
    elif request.method == 'POST':
        print('POST: paper_creaete')
        data_key = request.POST.get('data_key')
        uid_list = request.POST.getlist('userId')
        users = (get_object_or_404(LabUser, id=uid) for uid in uid_list)
        paper = get_object_or_404(Paper, key=data_key)
        papers = (Paper.objects.create(
            key=random.randint(100000000, 999999999),
            data=paper.data,
            mark=markPaper['tofill'] + '-' + paper.mark,
            user=user
        ) for user in users)
        paper_type = 'N'
        print('data_key-uid_list: ', data_key, uid_list)
    return render(request, 'labcrm/paper_list.html', {
        'papers': papers,
        'PType': paper_type
    })


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
def ajax_new_user(request):
    lab_user = request.GET.get('nickname').strip()
    print('lab_user: ', lab_user)
    user0, is_new = User.objects.get_or_create(username=lab_user)
    print('is_new: ', is_new)
    if is_new:
        user = LabUser.objects.create(user=user0)
        print('user.id: ', user.id)
        return HttpResponse(str(user.id))
    else:
        return HttpResponse()


@login_required
def ajax_conf_add(request):
    attr = request.POST.get('attr')
    is_option = request.POST.get('is_option')
    # is_preview = request.POST.get('is_preview')
    # print('attr-option-preview: ', attr, is_option, is_preview)
    print('attr-option: ', attr, is_option)
    if is_option:
        attr, _ = UserAttr.objects.update_or_create(attr=attr, defaults={
            'is_option': True,
            'is_del': False
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
            'is_option': False,
            'is_del': False
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

from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django import forms
from collections import namedtuple
from PIL import Image
import base64
import pymysql
import random
import datetime
# from mytool import log_this
from testools.declog import log_this
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


class ImgForm(forms.Form):
    pic = forms.ImageField()


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
    print('uiq-uia-is_new_uia:\t', uiq, uia, is_new)
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


@log_this
def _user_list_post(request):
    # username -> 本站用户名，    nickname -> 学习站用户名
    nickname = request.POST.get('nickname')
    wechat = request.POST.get('wechat')
    username = request.POST.get('username')
    user, is_new = User.objects.get_or_create(username=username)
    print('nickname wechat username is_new: \t', nickname, wechat, username, is_new)
    if nickname or wechat:
        if nickname:
            print('@添加用户名')
            LabUser.objects.filter(user=user).update(nickname=nickname)
        elif wechat:
            print('@添加微信号')
            LabUser.objects.filter(user=user).update(wechat=wechat)
        users = LabUser.objects.filter(is_del=False).order_by('-user__date_joined')
        return render(request, 'labcrm/ajax/user_del.html', {
            'users': users
        })
    elif not is_new:
        print('@昵称重复')
        return HttpResponse()
    else:
        print('@添加新用户')
        new_lab_user = LabUser.objects.create(
            user=user,
            wechat=wechat,
        )
        return HttpResponse(render(request, 'labcrm/ajax/user_add.html', {
            'lab_user': new_lab_user,
        }))


@log_this
def _user_list_get(request):
    uid = request.GET.get('uid')
    print('uid:\t', uid)
    if uid:
        print('@用户数据修改')
        wechat = request.GET.get('wechat')
        username = request.GET.get('username')
        nickname = request.GET.get('nickname')
        if wechat:
            print('wechat:\t', wechat)
            LabUser.objects.filter(id=uid).update(wechat=wechat)
        elif nickname:
            print('nickname:\t', nickname)
            LabUser.objects.filter(id=uid).update(nickname=nickname)
        else:
            print('username:\t', username)
            uuid = get_object_or_404(LabUser, id=uid).user.id
            User.objects.filter(id=uuid).update(username=username)
        return HttpResponse()
    elif request.GET.get('refresh'):
        print('@修改完毕，刷新列表')
        users = LabUser.objects.filter(is_del=False).order_by('-user__date_joined')
        return render(request, 'labcrm/ajax/user_del.html', {
            'users': users
        })
    print('@用户列表展示')
    users = LabUser.objects.filter(is_del=False).order_by('-user__date_joined')
    return render(request, 'labcrm/user_list.html', {
        'users': users
    })


@log_this
@login_required
def user_list(request):
    print('request\t', request)
    if request.method == 'POST':
        return _user_list_post(request)
    else:
        return _user_list_get(request)


@log_this
def _user_detail_get(request, lab_user):
    attrs = UserAttr.objects.all()
    attr_option = attrs.filter(is_option=True)
    dialogs = Dialog.objects.filter(user=lab_user).order_by('-log_time')
    pics = UserPic.objects.filter(user=lab_user, pic_type=picType['dialog'])
    user_answers = UserInfoA.objects.filter(user=lab_user, is_del=False)
    print('labUser:\t', lab_user)
    print('attrs:\t', attrs)
    print('attr_option:\t', attr_option)
    print('answers:\t', user_answers)
    print('dialogs-len:\t', len(dialogs))
    print('pics-len:\t', len(pics))
    if request.GET.get('ajax') is None:
        print('@用户信息展示')
        return render(request, 'labcrm/user_detail.html', {
            'labUser': lab_user,
            'attrs': attrs,
            'attr_option': attr_option,
            'answers': user_answers,
            'dialogs': dialogs,
            'pics': pics,
        })
    else:
        print('@取消修改')
        return HttpResponse(render(request, 'labcrm/ajax_user_detail.html', {
            'labUser': lab_user,
            'attrs': attrs,
            'attr_option': attr_option,
            'answers': user_answers,
            'dialogs': dialogs,
            'pics': pics
        }))


@log_this
def _user_detail_post(request, lab_user):
    attrs = UserAttr.objects.all()
    attr_option = attrs.filter(is_option=True)
    dialog = request.POST.get('dialog')
    # pic_post = request.POST.get('pic')
    pic_name = request.POST.get('pic_name')
    questions = request.POST.getlist('tagQuestion')
    answers = request.POST.getlist('tagAnswer')
    dialogs = Dialog.objects.filter(user=lab_user).order_by('-log_time')
    pics = UserPic.objects.filter(user=lab_user, pic_type=picType['dialog'])
    user_answers = UserInfoA.objects.filter(user=lab_user, is_del=False)
    print('pic_name is-dialog is-ques is-answ:\t', pic_name, bool(dialog), bool(questions), bool(answers))
    if dialog:
        print('@添加沟通记录')
        user = request.user
        Dialog.objects.create(
            dialog=dialog,
            user=lab_user,
            recorder=user
        )
        dialogs = Dialog.objects.filter(user=lab_user).order_by('-log_time')
        print('dialog-len:\t', len(dialogs))
    print('---------------------')
    pic_form = ImgForm(request.POST, request.FILES)
    print('pic_form.is_valid():\t', pic_form.is_valid())
    if pic_form.is_valid():
        print('@添加图片')
        pic = pic_form.cleaned_data['pic']
        print('pic:\t', pic)
        image = Image.open(pic)
        print('image:\t', image)
        name = picType['dialog'] + '-' + lab_user.user.username + '-' + \
            datetime.datetime.now().strftime('%Y-%m-%d') + '.' + pic_name.split('.')[-1]
        image.save('media/img/gallery/%s' % name)
        pic_obj, _ = PicData.objects.get_or_create(pic=pic, defaults={
            'name': name
        })
        print('pic_obj:\t', pic_obj)
        UserPic.objects.create(
            user=lab_user,
            pic=pic_obj,
            pic_type=picType['dialog']
        )
        pics = UserPic.objects.filter(user=lab_user, pic_type=picType['dialog'])
        print('---------------------')
    if questions and answers:
        print('@修改资料')
        info = dict(zip(questions, answers))
        print('info:\t', info)
        for question in set(questions) & {attr.attr for attr in attr_option}:
            print('MODE: 已存在有选项的属性')
            attr = get_object_or_404(UserAttr, attr=question)
            print('question:\t', question)
            if info[question] not in [option.option for option in attr.options.all()]:
                print('mode: 保存新选项')
                print('new-question-option:\t', question, info[question])
                AttrOption.objects.create(
                    option=info[question],
                    attr=attr
                )
            _save_uiq_uia(lab_user, attr, info[question])
        for question in set(questions) & {attr.attr for attr in attrs} - {attr.attr for attr in attr_option}:
            print('MODE: 已存在无选项的属性')
            attr = get_object_or_404(UserAttr, attr=question)
            print('question:\t', question)
            _save_uiq_uia(lab_user, attr, info[question])
        for question in set(questions) - {attr.attr for attr in attrs}:
            print('MODE: 新属性')
            attr = UserAttr.objects.create(
                attr=question
            )
            print('question:\t', question)
            _save_uiq_uia(lab_user, attr, info[question])
        for question in {question.attr.attr for question in lab_user.questions.filter(is_del=False)} - set(questions):
            print('MODE: 被删除的属性')
            attr = get_object_or_404(UserAttr, attr=question)
            uiq = get_object_or_404(UserInfoQ, user=lab_user, attr=attr, is_del=False)
            uiq.is_del = True
            uiq.save()
            uia = get_object_or_404(UserInfoA, user=lab_user, question=uiq, is_del=False)
            uia.is_del = True
            uia.save()
            print('ques-uiq-uia:\t', question, uiq, uia)
        attrs = UserAttr.objects.all()
        attr_option = attrs.filter(is_option=True)
        user_answers = UserInfoA.objects.filter(user=lab_user, is_del=False)
    return HttpResponse(render(request, 'labcrm/ajax_user_detail.html', {
        'labUser': lab_user,
        'attrs': attrs,
        'attr_option': attr_option,
        'answers': user_answers,
        'dialogs': dialogs,
        'pics': pics
    }))


@log_this
@login_required
def user_detail(request, new_id=None):
    print('request\t', request)
    if not new_id:
        new_id = request.GET.get('uid')
    lab_user = get_object_or_404(LabUser, id=new_id)
    if request.method == 'GET':
        return _user_detail_get(request, lab_user)
    else:
        return _user_detail_post(request, lab_user)


@log_this
@login_required
def ques_conf(request):
    print('request\t', request)
    if request.method == 'POST':
        title = request.POST.get('paper_title')
        lab_user = request.POST.get('labUser')
        paper_desc = request.POST.get('paper_desc')
        ques_desc = request.POST.getlist('ques_desc')
        attr_ids = request.POST.getlist('attr_id')
        mark = request.POST.get('mark')
        print('len-ques attr-ids:\t', len(ques_desc), attr_ids)
        if not mark:
            mark = markPaper['default']
        print('is_title is_desc user mark:\t', bool(title), bool(paper_desc), lab_user, mark)
        if request.POST.get('is_cre'):
            print('@生成问卷')
            data = '@@'.join([title, paper_desc, '##'.join(ques_desc), '##'.join(attr_ids)])
            key = random.randint(100000000, 999999999)
            Paper.objects.create(
                key=key,
                data=data,
                mark=mark
            )
            if lab_user:
                print('@@生成问卷列表')
                print('lab_user-data-key:\t', lab_user, data, key)
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
                print('data_key:\t', data_key)
                return redirect('crm:fill', data_key=data_key)
            else:
                print('@@生成问卷模版')
                data_key = str(key)
                print('data_key:\t', data_key)
                return redirect('crm:paper2', data_key=data_key)
        else:
            print('@问卷配置预览')
            attrs = [get_object_or_404(UserAttr, id=aid) for aid in attr_ids]
            quests = zip(ques_desc, attr_ids, attrs)
            quests = sorted(quests, key=lambda x: x[2].is_option, reverse=True)

            def questions():
                for ques in quests:
                    print('ques:\t', ques)
                    yield QuesTuple(*ques)

            return HttpResponse(render(request, 'labcrm/ques_to_fill.html', {
                'title': title,
                'labUser': lab_user,
                'paper_desc': paper_desc,
                'is_fill': False,
                'mark': mark,
                'questions': questions(),
                'questions2': questions()
            }))
    else:
        aid = request.GET.get('attrDel')
        if aid:
            print('@删除问题')
            print('attr-id:\t', aid)
            attr = get_object_or_404(UserAttr, id=aid)
            attr.is_del = True
            attr.save()
            return HttpResponse('T')
        print('@问卷配置展示')
        attrs = UserAttr.objects.filter(is_del=False)
        papers = Paper.objects.filter(user__isnull=True).order_by('-create_time')
        print('attrs-len papers-len:\t', attrs.count(), papers.count())
        return render(request, 'labcrm/ques_conf.html', {
            'attrs': attrs,
            'papers': papers[:10]
        })


@log_this
def ques_fill(request, data_key=None):
    print('request\t', request)
    key = data_key[:9]
    uid = data_key[9:]
    paper = get_object_or_404(Paper, user=uid, key=key)
    mark = paper.mark.lstrip(markPaper['tofill'])
    title, paper_desc, ques_desc_str, ques_ids_str = paper.data.split('@@')
    ques_desc = ques_desc_str.split('##')
    attr_ids = ques_ids_str.split('##')
    attrs = [get_object_or_404(UserAttr, id=aid) for aid in attr_ids]
    user = get_object_or_404(LabUser, id=uid)
    print('user mark paper:\t', user, mark, paper)
    print('paper.data:\t', paper.data)
    if request.method == 'POST':
        print('@问卷填写')
        ques_values = [request.POST.get('ques_value' + aid) for aid in attr_ids]
        data = '@@'.join(
            [title, paper_desc, '##'.join(ques_desc), '##'.join(attr_ids), '##'.join(ques_values)])
        print('data:\t', data)
        paper.user = user
        paper.data = data
        paper.is_fill = True
        paper.mark = user.user.username + mark
        paper.finished_time = datetime.datetime.now()
        paper.save()
        quests = zip(attrs, ques_values)
        for quest in quests:
            attr, value = quest
            print('attr value:\t', attr, value)
            _save_uiq_uia(user, attr, value)
        return render(request, 'labcrm/fill_success.html')
    print('@问卷填写展示')
    quests = zip(ques_desc, attr_ids, attrs)
    quests = sorted(quests, key=lambda x: x[2].is_option, reverse=True)
    print('data:\t', paper.data)
    
    def questions():
        for ques in quests:
            print('ques:\t', ques)
            yield QuesTuple(*ques)

    return HttpResponse(render(request, 'labcrm/ques_to_fill.html', {
        'title': title,
        'labUser': user,
        'paper_desc': paper_desc,
        'data_key': data_key,
        'is_fill': True,
        'questions': questions(),
    }))


@log_this
def paper_display(request, data_key=None):
    print('request\t', request)
    if request.method == 'GET':
        new_paper_name = request.GET.get('reName')
        modal_display = False
        if not data_key:
            data_key = request.GET.get('data_key')
        print('data_key:\t', data_key)
        key = data_key[:9]
        if len(data_key) > 9:
            uid = data_key[9:]
            lab_user = get_object_or_404(LabUser, id=uid)
        else:
            lab_user = None
        paper = get_object_or_404(Paper, key=key)
        if new_paper_name:
            print('@问卷模版重命名')
            print('paper new_paper_name:\t', paper, new_paper_name)
            paper.mark = new_paper_name
            paper.save()
            return HttpResponse(paper.__str__())
        print('@问卷生成前展示')
        data = paper.data.split('@@')
        if len(data) == 5:
            title, paper_desc, ques_desc_str, ques_ids_str, ques_values_str = data
            ques_values = ques_values_str.split('##')
            filled = True
        else:
            filled = False
            title, paper_desc, ques_desc_str, ques_ids_str = data
            ques_values = None
        print('data filled:\t', data, filled)
        ques_desc = ques_desc_str.split('##')
        attr_ids = ques_ids_str.split('##')
        if not ques_values:
            ques_values = ['']*len(attr_ids)
    else:       # POST
        print('@问卷提交预览')
        data_key = request.POST.get('data_key')
        key = data_key[:9]
        if len(data_key) > 9:
            uid = data_key[9:]
            lab_user = get_object_or_404(LabUser, id=uid)
        else:
            lab_user = None
        paper = get_object_or_404(Paper, key=key)
        title, paper_desc, ques_desc_str, ques_ids_str = paper.data.split('@@')
        ques_desc = ques_desc_str.split('##')
        attr_ids = ques_ids_str.split('##')
        ques_values = [request.POST.get('ques_value'+aid) for aid in attr_ids]
        modal_display = True
        filled = False
        print('paper:\t', paper)
    attrs = [get_object_or_404(UserAttr, id=aid) for aid in attr_ids]
    quests = zip(ques_desc, attr_ids, attrs, ques_values)
    quests = sorted(quests, key=lambda x: x[2].is_option, reverse=True)

    def questions():
        for ques in quests:
            print('ques:\t', ques)
            yield QuesTuple2(*ques)

    users = LabUser.objects.filter(is_del=False).order_by('-user__date_joined')
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


@log_this
@login_required
def papers_create(request):
    print('request\t', request)
    paper_type = request.GET.get('PType')
    pid = request.GET.get('paperDel')
    papers = []
    if paper_type:
        if paper_type == 'M':
            papers = Paper.objects.filter(is_fill=False, user__isnull=True, is_del=False).order_by('-create_time')
        elif paper_type == 'TF':
            papers = Paper.objects.filter(is_fill=False, user__isnull=False, is_del=False).order_by('-create_time')
        elif paper_type == 'F':
            papers = Paper.objects.filter(is_fill=True, is_del=False).order_by('-create_time')
        elif paper_type == 'A':
            papers = Paper.objects.filter(is_del=False).order_by('-create_time')
    elif pid:
        get_object_or_404(Paper, id=pid).delete()
        return HttpResponse('T')
    elif request.method == 'POST':
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
        print('data_key-uid_list:\t', data_key, uid_list)
    return render(request, 'labcrm/paper_list.html', {
        'papers': papers,
        'PType': paper_type
    })


@log_this
@login_required
def link_to_class(request):
    print('request\t', request)
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


@log_this
@login_required
def ajax_new_user(request):
    print('request\t', request)
    lab_user = request.GET.get('nickname').strip()
    print('lab_user:\t', lab_user)
    user0, is_new = User.objects.get_or_create(username=lab_user)
    print('is_new:\t', is_new)
    if is_new:
        user = LabUser.objects.create(user=user0)
        print('user.id:\t', user.id)
        return HttpResponse(str(user.id))
    else:
        return HttpResponse()


@log_this
@login_required
def ajax_conf_add(request):
    print('request\t', request)
    attr = request.POST.get('attr')
    is_option = request.POST.get('is_option')
    print('attr-option:\t', attr, is_option)
    if is_option:
        attr, _ = UserAttr.objects.update_or_create(attr=attr, defaults={
            'is_option': True,
            'is_del': False
        })
        options = request.POST.getlist('options')
        print('options:\t', options)
        for option in options:
            print('attr-option:\t', attr, option)
            AttrOption.objects.get_or_create(
                attr=attr,
                option=option
            )
    else:
        attr, _ = UserAttr.objects.update_or_create(attr=attr, defaults={
            'is_option': False,
            'is_del': False
        })
    return render(request, 'labcrm/ques_add.html', {
        'attr': attr,
    })


@log_this
@login_required
def ajax_conf_preview(request):
    print('request\t', request)
    print('@问卷配置')
    attr_ids = request.POST.getlist('attr_checked')
    print('attr_ids:\t', attr_ids)
    attrs = UserAttr.objects.filter(id__in=attr_ids).order_by('-is_option')
    users = LabUser.objects.filter(is_del=False).order_by('-user__date_joined')
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


@log_this
@login_required
def ajax_user_del(request):
    print('request\t', request)
    uid = request.POST.getlist('userId')
    print('userId:\t', uid)
    users = LabUser.objects.filter(id__in=uid)
    for user in users:
        user.is_del = True
        user.save()
    users = LabUser.objects.filter(is_del=False).order_by('-user__date_joined')
    return render(request, 'labcrm/ajax/user_del.html', {
        'users': users
    })

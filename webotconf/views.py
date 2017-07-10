from django.shortcuts import render
from .models import ChatRoom, RuleAddFriend
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import re
# Create your views here.


@login_required
def rule_conf(request):
    rooms = ChatRoom.objects.all().order_by('order')
    if request.method == 'POST':
        list_room = request.POST.getlist('rooms')
        list_keywords = request.POST.getlist('keywords')
        list_orders = request.POST.getlist('orders')
        rules = zip(list_room, list_orders, list_keywords)
        print(len(list_keywords), len(list_orders), len(list_room))
        if len(set(list_room)) < len(list_room):
            return HttpResponse()
        for rule in rules:
            keywords = re.split(r'[,，;；.。| +-]+', rule[2].strip(',，;；.。| +-'))
            print(rule, keywords)
            room, _ = ChatRoom.objects.update_or_create(nickname=rule[0], defaults={
                'order': rule[1]
            })
            for keyword in keywords:
                RuleAddFriend.objects.get_or_create(
                    keyword=keyword,
                    chatroom=room
                )
        rooms = ChatRoom.objects.all().order_by('order')
        return HttpResponse(render(request, 'webotconf/ajax/rules.html', {
            'rooms': rooms
        }))
    return render(request, 'webotconf/webot.html', {
        'rooms': rooms
    })


@login_required
def ajax_conf_modify(request):
    rooms = ChatRoom.objects.all().order_by('order')
    return HttpResponse(render(request, 'webotconf/ajax/modify.html', {
        'rooms': rooms
    }))

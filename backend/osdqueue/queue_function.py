from django.http import HttpResponse
from django.utils import timezone
from .utils import DateEncoder
from django.views.decorators.csrf import csrf_exempt
import json
from osdqueue.models import user, queue, relation


@csrf_exempt
def create_queue(request):
    open_id = request.POST.get('open_id', None)
    re = {'Code': 'Error'}
    try:
        creator = user.objects.get(open_id=open_id)
        if creator.role() != 'teacher' and creator.role() != 'admin':
            re['ErrorMessage'] = 'Not Authorized'
        else:
            new_queue = queue(creator=creator)
            new_queue.save()
            name = request.POST.get('name', None)
            if name is "":
                name = '队列【' + str(new_queue.id) + '】'
            new_queue.name = name
            new_queue.save()

            re['Code'] = 'OK'
        return HttpResponse(json.dumps(re))
    except(KeyError, user.DoesNotExist):
        re['ErrorMessage'] = 'Not Authorized'
        return HttpResponse(json.dumps(re))


@csrf_exempt
def set_queue(request):
    open_id = request.POST.get('open_id', None)
    queue_id = request.POST.get('queue_id', None)
    re = {'Code': 'Error'}
    try:
        request_user = user.objects.get(open_id=open_id)
    except(KeyError, user.DoesNotExist):
        re['ErrorMessage'] = 'Not Signed'
        return HttpResponse(json.dumps(re))

    try:
        target_queue = queue.objects.get(id=queue_id)
    except(KeyError, queue.DoesNotExist):
        re['ErrorMessage'] = 'No Such Queue'
        return HttpResponse(json.dumps(re))

    if target_queue.creator != request_user and request_user.role() != 'admin':
        re['ErrorMessage'] = 'Not Authorized'
        return HttpResponse(json.dumps(re))

    op = request.POST.get('operation', None)
    if op == 'delete':
        target_queue.delete()
        re['Code']='OK'
        return HttpResponse(json.dumps(re))
    if op == 'pend':
        target_queue.status = 0
    if op == 'finish':
        target_queue.status = 1
    if op == 'start':
        target_queue.status = 2

    target_queue.save()
    re['Code'] = 'OK'
    return HttpResponse(json.dumps(re))


@csrf_exempt
def tackle_queue(request):
    open_id = request.POST.get('open_id', None)
    queue_id = request.POST.get('queue_id', None)
    re = {'Code': 'Error'}
    try:
        request_user = user.objects.get(open_id=open_id)
    except(KeyError, user.DoesNotExist):
        re['ErrorMessage'] = 'Not Signed'
        return HttpResponse(json.dumps(re))

    try:
        target_queue = queue.objects.get(id=queue_id)
    except(KeyError, queue.DoesNotExist):
        re['ErrorMessage'] = 'No Such Queue'
        return HttpResponse(json.dumps(re))

    try:
        r = relation.objects.get(user=request_user, queue=target_queue)
    except(KeyError, relation.DoesNotExist):
        r = relation(user=request_user, queue=target_queue)

    op = request.POST.get('operation', None)

    if op == 'next':
        if target_queue.was_operating() is False:
            re['ErrorMessage'] = 'Queue Not Available'
            return HttpResponse(json.dumps(re))
        if target_queue.creator != request_user:
            re['ErrorMessage'] = 'Not Authorized'
            return HttpResponse(json.dumps(re))
        try:
            followers = relation.objects.filter(queue=target_queue, status=2).order_by('create_time')[:2]
            if len(followers) == 0:
                re['ErrorMessage'] = 'No Followers'
                return HttpResponse(json.dumps(re))
            if len(followers) > 0:
                followers[0].status = 3
                followers[0].save()
            if len(followers) > 1:
                # todo: send notifications
                pass
            re['Code'] = 'OK'
            return HttpResponse(json.dumps(re))
        except(KeyError, relation.DoesNotExist):
            re['ErrorMessage'] = 'No Followers'
            return HttpResponse(json.dumps(re))
    if op == 'join':
        if target_queue.was_operating() is False:
            print(target_queue.get_dict())
            re['ErrorMessage'] = 'Queue Not Available'
            return HttpResponse(json.dumps(re))
        if request_user.can_join_queue() is False:
            re['ErrorMessage'] = 'Not Qualified User'
            return HttpResponse(json.dumps(re))

        r.create_time = timezone.now()
        r.status = 2
        r.save()
        re['Code'] = 'OK'
        return HttpResponse(json.dumps(re))
    if op == 'quit':
        if r.which() == 'finished':
            re['ErrorMessage'] = 'You cannot quit this queue'
            return HttpResponse(json.dumps(re))
        r.status = 0
        r.save()
        re['Code'] = 'OK'
        return HttpResponse(json.dumps(re))

    re['ErrorMessage'] = 'No Valid Operation'
    return HttpResponse(json.dumps(re))


@csrf_exempt
def get_queue(request):
    open_id = request.POST.get('open_id', None)
    queue_id = request.POST.get('queue_id', None)
    re = {'Code': 'Error'}
    try:
        request_user = user.objects.get(open_id=open_id)
    except(KeyError, user.DoesNotExist):
        re['ErrorMessage'] = 'Not Signed'
        return HttpResponse(json.dumps(re))

    try:
        target_queue = queue.objects.get(id=queue_id)
    except(KeyError, queue.DoesNotExist):
        re['ErrorMessage'] = 'No Such Queue'
        return HttpResponse(json.dumps(re))

    try:
        r = relation.objects.get(user=request_user, queue=target_queue)
    except(KeyError, relation.DoesNotExist):
        r = relation(user=request_user, queue=target_queue)
        r.save()

    re['queue'] = target_queue.get_dict()
    try:
        rs = relation.objects.filter(queue=target_queue, status__gt=0).order_by('status', 'create_time')
        re['queue']['follower'] = []
        re['queue']['finished'] = []
        re['queue']['creator'] = target_queue.creator.get_dict(restricted=True)
        for r in rs:
            if r.which() == 'follower':
                re['queue']['follower'].append(r.user.get_dict(restricted=True))
            if r.which() == 'finished':
                re['queue']['finished'].append(r.user.get_dict(restricted=True))
        re['queue']['my_relation'] = r.get_dict()

        re['Code'] = 'OK'
        return HttpResponse(json.dumps(re, cls=DateEncoder, ensure_ascii=False))
    except(KeyError, relation.DoesNotExist):
        re['ErrorMessage'] = 'No Relations'
        return HttpResponse(json.dumps(re))


@csrf_exempt
def all_queue(request):
    open_id = request.POST.get('open_id', None)
    re = {'Code': 'Error'}
    try:
        request_user = user.objects.get(open_id=open_id)
    except(KeyError, user.DoesNotExist):
        re['ErrorMessage'] = 'Not Signed'
        return HttpResponse(json.dumps(re))
    queues = queue.objects.all()
    re['queues'] = []
    for q in queues:
        tmp = q.get_dict()
        all = relation.objects.filter(queue=q)
        r = all.filter(status=2).order_by('create_time')
        tmp['creator'] = q.creator.avatar_url
        tmp['size'] = len(r)
        tmp['upcoming'] = [u.user.avatar_url for u in r[:3]]
        re['queues'].append(tmp)
    re['Code'] = 'OK'
    return HttpResponse(json.dumps(re, cls=DateEncoder, ensure_ascii=False))

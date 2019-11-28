from django.http import HttpResponse
from django.utils import timezone
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
            new_queue = queue()
            new_queue.save()
            name = request.POST.get('name', None)
            if name is None:
                name = '队列【' + str(new_queue.id) + '】'
            new_queue.name = name
            new_queue.save()
            new_relation = relation(user=creator, queue=new_queue)
            new_relation.save()
            re['Code'] = 'OK'
        return HttpResponse(json.dumps(re))
    except(KeyError, user.DoesNotExist):
        re['ErrorMessage'] = 'Not Authorized'
        return HttpResponse(json.dumps(re))

@csrf_exempt
def set_queue(request):
    open_id = request.POST.get('open_id', None)
    queue_id = request.POST.get('queue_id',None)
    re = {'Code': 'Error'}
    try:
        request_user = user.objects.get(open_id=open_id)
    except(KeyError, user.DoesNotExist):
        re['ErrorMessage'] = 'Not Signed'
        return HttpResponse(json.dumps(re))

    try:
        target_queue = queue.objects.get(id=queue_id)
    except(KeyError,queue.DoesNotExist):
        re['ErrorMessage'] = 'No Such Queue'
        return HttpResponse(json.dumps(re))

    try:
        r = relation.objects.get(user=request_user, queue=target_queue)
        if r.which() != 'creator' and request_user.role() != 'admin':
            re['ErrorMessage'] = 'Not Authorized'
            return HttpResponse(json.dumps(re))
    except(KeyError, relation.objects):
        re['ErrorMessage'] = 'Not Authorized'
        return HttpResponse(json.dumps(re))

    op = request.POST.get('operation',None)
    if op == 'delete':
        target_queue.delete()
    if op == 'pending':
        target_queue.status = 0
    if op == 'finished':
        target_queue.status = 1
    if op == 'operating':
        target_queue.status = 2

    re['Code']='OK'
    return HttpResponse(json.dumps(re))


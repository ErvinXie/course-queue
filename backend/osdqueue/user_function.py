from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
import json
from osdqueue.models import user, queue, relation


@csrf_exempt
def get_openid(request):
    code = request.POST.get('code')
    from .secure_info import AppID, AppSecret
    parmas = {
        'appid': AppID,
        'secret': AppSecret,
        'js_code': code,
        'grant_type': 'authorization_code'
    }
    import requests as req
    url = 'https://api.weixin.qq.com/sns/jscode2session'
    response = (req.get(url, params=parmas)).json()

    re = {'Code': 'Error'}

    if 'errmsg' in response.keys():
        re['ErrorMessage'] = response['errmsg']
        return HttpResponse(json.dumps(re))
    else:
        re['Code'] = 'OK'
        re['open_id '] = response['openid']
        try:
            this_user = user.objects.get(open_id=re['open_id '])
        except(KeyError, user.DoesNotExist):
            this_user = user(open_id=re['open_id '])
            this_user.save()
        return HttpResponse(json.dumps(re))


@csrf_exempt
def set_info(request):
    open_id = request.POST.get('open_id', None)
    re = {'Code': 'Error'}
    try:
        this_user = user.objects.get(open_id=open_id)
        for key in this_user.get_dict():
            if key != 'id' and request.POST.get(key, None) is not None:
                setattr(this_user, key, request.POST.get(key))
        this_user.save()
        re['Code'] = 'OK'
        return HttpResponse(json.dumps(re))
    except(KeyError, user.DoesNotExist):
        re['ErrorMessage'] = 'Not Signed'
        return HttpResponse(json.dumps(re))


@csrf_exempt
def get_info(request):
    open_id = request.POST.get('open_id', None)
    id = request.POST.get('id', None)
    re = {'Code': 'Error'}
    try:
        this_user = user.objects.get(open_id=open_id)
    except(KeyError, user.DoesNotExist):
        re['ErrorMessage'] = 'Not Signed'
        return HttpResponse(json.dumps(re))

    try:
        target_user = user.objects.get(id=id)
        if target_user.open_id == open_id:
            re['info'] = target_user.get_dict()
        else:
            re['info'] = target_user.get_dict(restricted=True)
        re['Code'] = 'OK'
        return HttpResponse(json.dumps(re,ensure_ascii=False))
    except(KeyError, user.DoesNotExist):
        re['ErrorMessage'] = 'No Such User'
        return HttpResponse(json.dumps(re))

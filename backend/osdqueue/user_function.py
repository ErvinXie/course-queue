from django.http import HttpResponse
from django.utils import timezone
from .utils import DateEncoder
from django.views.decorators.csrf import csrf_exempt
from osdqueue.models import user, queue, relation

import json


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
        re['me'] = this_user.get_dict()
        return HttpResponse(json.dumps(re, cls=DateEncoder, ensure_ascii=False))


@csrf_exempt
def set_info(request):
    open_id = request.POST.get('open_id', None)
    user_info = request.POST.get('user_info', None)
    if user_info is not None:
        user_info = json.loads(user_info)
        user_info['avatar_url'] = user_info['avatarUrl']
    re = {'Code': 'Error'}

    try:
        this_user = user.objects.get(open_id=open_id)
        for key in this_user.get_dict():
            if key != 'id' and key != 'status':
                if key in request.POST:
                    print(key, request.POST.get(key))
                    setattr(this_user, key, request.POST.get(key))
                if key in user_info:
                    print(key, user_info[key])
                    setattr(this_user, key, user_info[key])

        # decide the identiy
        # print(this_user.get_dict())
        if this_user.role() == 'tourist':
            cert = request.POST.get('cert', None)
            from .secure_info import cert_code
            if cert == cert_code and this_user.name != "":
                this_user.status = 2  # teacher

            else:
                if this_user.name != "" and this_user.school_id != "" and this_user.class_id != "":
                    this_user.status = 1  # students
                else:
                    re['ErrorMessage'] = 'Empty Information'
                    return HttpResponse(json.dumps(re, cls=DateEncoder, ensure_ascii=False))

        if this_user.name == '':
            if this_user.role() != 'admin':
                this_user.status = 0
        if this_user.school_id == "" or this_user.class_id == "":
            if this_user.role() == 'student':
                this_user.status = 0
        this_user.save()
        re['Code'] = 'OK'
        re['me'] = this_user.get_dict()
        return HttpResponse(json.dumps(re, cls=DateEncoder, ensure_ascii=False))
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
        return HttpResponse(json.dumps(re, ensure_ascii=False))
    except(KeyError, user.DoesNotExist):
        re['ErrorMessage'] = 'No Such User'
        return HttpResponse(json.dumps(re))

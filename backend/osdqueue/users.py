from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
import json


@csrf_exempt
def get_openid(request):
    code = request.POST.get('code')
    print(request.POST)
    user_info = request.POST.get('userInfo', None)
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
        try:
            user = users.objects.get(open_id=response['openid'])
            if user.was_banned():
                re['Code'] = 'Error'
                re['ErrorMessage'] = 'Banned'
                return HttpResponse(json(re))
        except(KeyError, users.DoesNotExist):
            user = users(open_id=response['openid'], status=0)
        finally:
            re['open_id'] = response['openid']
            re['status'] = user.status
            if user_info is not None and user_info != 'null':
                user_info = json.loads(user_info)
                user.nickname = user_info['nickName']
                user.gender = user_info['gender']
                user.city = user_info['city']
                user.province = user_info['province']
                user.country = user_info['country']
                user.avatar_url = user_info['avatarUrl']
            user.save()
        re['user'] = user.get_dict()
        return HttpResponse(json.dumps(re))
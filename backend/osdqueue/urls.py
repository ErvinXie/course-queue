from django.urls import path

from . import users


urlpatterns = [
    path('get-openid/',users.get_openid,name = 'get_openid')

]
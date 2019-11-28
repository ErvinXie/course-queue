from django.urls import path

from . import user_function,queue_function


urlpatterns = [
    path('get-openid/', user_function.get_openid, name ='get openid'),
    path('set-info/',user_function.set_info,name='set info'),
    path('get-info/',user_function.get_info,name='get info'),
    path('create-queue/',queue_function.create_queue,name= 'create queue'),
    path('set-queue/',queue_function.set_queue,name = 'set queue')
]
from django.conf.urls import url
from . import views
urlpatterns=[
    #http://127.0.0.1:8000/v1/users
    url(r'^$',views.users),
    #APPEND_SLASH 自动补全url后面的斜线,1前提是你有个带/的路由
    url(r'^/(?P<username>[\w]{1,11})$', views.users),
    url(r'^/(?P<username>[\w]{1,11})/avatar$',views.user_avatar),
]

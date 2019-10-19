import hashlib
import json
import time
from django.http import JsonResponse
from django.shortcuts import render
from .models import *
from btoken.views import make_token
from tools.login_check import login_check
# Create your views here.
@login_check('PUT')
def users(request, username=None):
    if request.method == 'GET':
        #获取用户数据
        if username:
            #/v1/users/<username>
            #拿指定用户数据
            try:
                user = UserProfile.objects.get(username=username)
            except Exception as e:
                user = None
            if not user:
                result = {'code': 208, 'error': 'no user'}
                return JsonResponse(result)
            #检查是否有查询字符串
            if request.GET.keys():
                #查询指定字段
                data = {}
                for k in request.GET.keys():
                    if hasattr(user, k):
                        v = getattr(user, k)
                        if k == 'avatar':
                            data[k] = str(v)
                        else:
                            data[k] = v
                result = {'code':200, 'username':username, 'data':data}
                return JsonResponse(result)
            else:
                #全量查询【password email 不给】
                result = {'code':200, 'username':username, 'data':{'info':user.info, 'sign':user.sign, 'avatar':str(user.avatar),'nickname':user.nickname}}
                return JsonResponse(result)

            # return JsonResponse({'code': 200, 'error':'wolaila GET %s'%(username)})
        else:
            #/v1/users
            return JsonResponse({'code':200, 'error':'wolaile GET'})

    elif request.method == 'POST':
        #此功能模块异常码  201 开始
        #request.POST  只能拿表单post提交的数据
        #创建用户
        #前端注册页面地址  http://127.0.0.1:5000/register
        # print(request.body)
        # dict = json.loads(request.body)
        # import jwt
        # jwt.encode()
        json_str = request.body
        if not json_str:
            result = {'code': 201, 'error': 'Please give me data'}
            return JsonResponse(result)
        #把客户端拿取的json串转化为字符串
        json_obj = json.loads(json_str)

        username = json_obj.get('username')
        if not username:
            result = {'code':202, 'error':'Please give me username'}
            return  JsonResponse(result)

        email = json_obj.get('email')
        if not email:
            result = {'code':203, 'error': 'Please give me email'}
            return JsonResponse(result)
        password_1 = json_obj.get('password_1')
        password_2 = json_obj.get('password_2')
        if not password_1 or not password_2:
            result = {'code':204, 'error': 'Please give me password'}
            return JsonResponse(result)

        if password_1 != password_2:
            result = {'code':205, 'error': 'Your password not same'}
            return JsonResponse(result)
        #优先查询当前用户名是否已存在
        old_user = UserProfile.objects.filter(username=username)
        if old_user:
            result = {'code':206, 'error':'Your username is already existed'}
            return JsonResponse(result)
        #密码处理 md5哈希/散列
        m = hashlib.md5()
        m.update(password_1.encode())
        #======charfield 尽量避免使用 null=True
        sign = info = ''
        try:
            UserProfile.objects.create(username=username,nickname=username,password=m.hexdigest(),sign=sign,info=info,email=email)
        except Exception as e:
            #数据库down了， 用户名已存在
            result = {'code': 207, 'error': 'Server is busy'}
            return JsonResponse(result)
        #make token
        token = make_token(username)
        #正常返回给前端
        result = {'code':200, 'username':username, 'data':{'token':token.decode()}}
        return JsonResponse(result)

    elif request.method == 'PUT':
        #http://127.0.0.1:5000/<username>/change_info
        #更新数据
        #此头可获取前端传来的token
        #META可拿取http协议原生请求头,META 也是类字典对象，可使用
        #字典相关方法
        #特别注意 http头有可能被django重命名，建议百度
        request.META.get('HTTP_AUTHORIZATION')

        user = request.user
        json_str = request.body
        if not json_str:
            result = {'code':209, 'error':'Please give me json'}
            return JsonResponse(result)

        json_obj = json.loads(json_str)

        if 'sign' not in json_obj:
            result = {'code':210, 'error': 'no sign'}
            return JsonResponse(result)
        if 'info' not in json_obj:
            result = {'code':211, 'error': 'no info'}
            return JsonResponse(result)
        sign = json_obj.get('sign')
        info = json_obj.get('info')

        request.user.sign = sign
        request.user.info = info
        request.user.save()
        result = {'code':200, 'username':request.user.username}
        return JsonResponse(result)

    else:
        raise KeyError

@login_check('POST')
def user_avatar(request,username):
    if request.method!="POST":
        result={'code':212,'error':'I need post'}
        return JsonResponse(result)
    avatar=request.FILES.get('avatar')
    if not avatar:
        result={'code':213,'error':'I need avatar'}
        return JsonResponse(result)
    #
    request.user.avatar=avatar
    request.user.save()
    result={'code':200,'username':request.user.username}
    return JsonResponse(result)















    return JsonResponse({'code':200,'error':'i am avatar!'})








from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from pandas._libs import json

from message.models import Message
from tools.login_check import login_check
from topic.models import Topic

@login_check('POST')
def messages(request,topic_id):
    if request.method!='POST':
        result={'code':401,'error':'please use post'}
        return JsonResponse(result)
    user=request.user
    json_str=request.body
    json_obj=json.loads(json_str)
    content=json_obj.get('content')
    if not content:
        result={'code':402,'error':'please give me content'}
        return JsonResponse(result)
    parent_id=json_obj.get('parent_id',0)
    try:
        topic=Topic.objects.get(id=topic_id)
    except:
        result = {'code': 403, 'error': 'no this topic'}
        return JsonResponse(result)
    if topic.limit=='private':
        if user.username!=topic.author.username:
            result={'code':404,'error':'get out'}
            return JsonResponse(result)
    Message.objects.create(content=content,publisher=user,
                           topic=topic,parent_message=parent_id)

    message=Message.objects.filter()



    return JsonResponse({'code':200,'data':{

    }})


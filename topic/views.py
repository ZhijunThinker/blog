from django.http import JsonResponse
from django.shortcuts import render
from pandas._libs import json
from btoken.views import make_token
from message.models import Message
from tools.login_check import login_check,get_user_by_request
# Create your views here.
from topic.models import Topic
from  user.models import UserProfile

@login_check('POST','DELETE')
def topics(request,author_id):
    if request.method=="GET":
        #http://127.0.0.1:5000/<username>/topics
        #获取用户数据
        authors=UserProfile.objects.filter(username=author_id)
        if not authors:
            result={'code':308,'error':'no author'}
            return JsonResponse(result)
        author=authors[0]
        visitor=get_user_by_request(request)
        visitor_name=None
        if visitor:
            visitor_name=visitor.username
        t_id=request.GET.get('t_id')
        if t_id:
            #是否为自己访问自己
            is_self=False
            #根据t_id 进行查询
            t_id=int(t_id)
            if author_id==visitor_name:
               is_self = True
               try:
                   author_topic=Topic.objects.get(id=t_id)
               except Exception as e:
                   result = {'code': 312, 'error': 'no topic'}
                   return JsonResponse(result)
            else:
                #访客访问
                try:
                    author_topic = Topic.objects.get(id=t_id,limit='public')
                except Exception as e:
                    result = {'code': 313, 'error': 'no topic !'}
                    return JsonResponse(result)
            res=make_topic_res(author,author_topic,is_self)
            return JsonResponse(res)

        else:
            category=request.GET.get('category')
            if category in ['tec','no-tec']:
                # /v1/topics/<author_id>? category=[tec|no-tec]
                if author_id==visitor_name:
                    topics=Topic.objects.filter(author_id=author_id,categrory=category)
                else:
                    topics=Topic.objects.filter(author_id=author_id,categrory=category,limit='public')

            else:
                # /v1/topics/<author_id>
                if author_id==visitor_name:
                    #博主访问自己的博客,获取全部的数据
                    topics=Topic.objects.filter(author_id=author_id)

                else:
                    #访客来了,非博主本人
                    topics=Topic.objects.filter(author_id=author_id,limit ='public')

            result=make_topics_res(author,topics)

            return JsonResponse(result)

    elif request.method=="POST":
        json_str = request.body
        if not json_str:
            result={'code':301,'error':'Please give me json'}
            return JsonResponse(result)
        json_obj=json.loads(json_str)
        title=json_obj.get('title')
        #xss注入,进行转义
        import html
        title=html.escape(title)
        if not title:
            result={'code':302,'error':"Please give me title"}
            return JsonResponse(result)
        content=json_obj.get('content')
        if not content:
            result = {'code': 303, 'error': "Please give me content"}
            return JsonResponse(result)
        #获取纯文本内容,
        content_text=json_obj.get('content_text')
        if not content_text:
            result = {'code': 304, 'error': "Please give me content_text"}
            return JsonResponse(result)
        introduce=content_text[:30]
        limit=json_obj.get('limit')
        if limit not in ['public','private']:
            result = {'code': 305, 'error': "You limit is wrong"}
            return JsonResponse(result)
        categrory = json_obj.get('category')
        if categrory not in ['tec','no-tec']:
            result = {'code': 306, 'error': "You categrory is wrong"}
            return JsonResponse(result)

        Topic.objects.create(title=title,categrory=categrory,limit=limit,content=content,introduce=introduce,
                             author=request.user)
        result={'code':200,'username':request.user.username}
        return JsonResponse(result)

    # elif request.method==""
    elif request.method=="DELETE":
        #博主删除自己的博客
        #vi/topics/<author_id>
        # #token存储的用户
        author=request.user
        token_author_id=author.username
        if author_id!=token_author_id:
            result={'code':309,'error':'You can not do it '}
            return JsonResponse(result)
        topic_id=request.GET.get('topic_id')
        try:
            topic=Topic.objects.get(id=topic_id)
        except:
            result={'code':310,'error':'You can not do it !'}
            return JsonResponse(result)
        if topic.author.username!=author_id:
            result = {'code': 311, 'error': 'You can not do it !!'}
            return JsonResponse(result)
        topic.delete()
        res={'code':200}
        return JsonResponse(res)

def make_topics_res(author,topics):
    res={'code':200,'data':{}}
    data={}
    data['nickname']=author.nickname
    topics_list = []
    for topic in topics:
        d={}
        d['id']=topic.id
        d['title']=topic.title
        d['categrory ']=topic.categrory
        d['introduce']=topic.introduce
        d['author']=author.nickname
        d['created_time']=topic.created_time.strftime('%Y-%m-%d %H:%M:%S')
        topics_list.append(d)
    data['topics']=topics_list
    res['data']=data
    return res
def make_topic_res(author,author_topic,is_self):
    '''
    拼接详情页返回的数据
    :param author: 作者对象
    :param author_topic: 文章对象
    :param is_self:
    :return:
    '''
    if is_self:
        #博主访问自己:
        #下一篇
        #取出id大于当前博客id的第一个且author为当前作者的
        next_topic=Topic.objects.filter(id__gt=author_topic.id,author=author).first()
        #上一篇:
        last_topic=Topic.objects.filter(id__lt=author_topic.id,author=author).last()
    else:
        #访客访问博主的下一篇
        next_topic = Topic.objects.filter(id__gt=author_topic.id, author=author,limit='public').first()
        last_topic = Topic.objects.filter(id__lt=author_topic.id, author=author,limit='public').last()
    if next_topic:
        next_id=next_topic.id
        next_title=next_topic.title
    else:
        next_id = None
        next_title = None
    if last_topic:
        last_id=last_topic.id
        last_title=last_topic.title
    else:
        last_id = None
        last_title = None

    all_messages = Message.objects.filter(topic=author_topic).order_by('-created_time')
    #所有的留言
    msg_list = []
    #留言&回复的映射字典
    reply_dict = {}
    msg_count = 0
    for msg in all_messages:
        msg_count += 1
        if msg.parent_message == 0:
            #当前是留言
            msg_list.append({'id':msg.id, 'content':msg.content, 'publisher': msg.publisher.nickname, 'publisher_avatar': str(msg.publisher.avatar), 'created_time': msg.created_time.strftime('%Y-%m-%d'), 'reply':[]})
        else:
            #当前是回复
            reply_dict.setdefault(msg.parent_message, [])
            reply_dict[msg.parent_message].append({'msg_id':msg.id,'content':msg.content,'publisher':msg.publisher.nickname, 'publisher_avatar':str(msg.publisher.avatar), 'created_time': msg.created_time.strftime('%Y-%m-%d')})

    #合并  msg_list 和 reply_dict
    for _msg in msg_list:
        if _msg['id'] in reply_dict:
            _msg['reply'] = reply_dict[_msg['id']]

    res={'code':200,'data':{}}
    res['data']['nickname']=author.nickname
    res['data']['title']=author_topic.title
    res['data']['category']=author_topic.categrory
    res['data']['created_time']=author_topic.created_time.strftime('%Y-%m-%d %H:%M:%S')
    res['data']['content']=author_topic.content
    res['data']['introduce']=author_topic.introduce
    res['data']['author']=author.nickname
    res['data']['next_id']=next_id
    res['data']['next_title']=next_title
    res['data']['last_id']=last_id
    res['data']['last_title']=last_title
    res['data']['messages']=msg_list
    res['data']['messages_count']=msg_count
    return res







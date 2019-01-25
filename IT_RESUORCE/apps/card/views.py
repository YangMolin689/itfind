from random import sample
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, logout, login
from django.views.generic import View
from apps.logs.MyLog import logger
from django.core.cache import cache
from .models import Card_Type, Card, Comment
from apps.user.models import User
from apps.logs.MyLog import logger
from django.core.paginator import Paginator
import json
from django.urls import reverse
from django_redis import get_redis_connection
from utils.spider import Get_news
from django.core.cache import cache
from itertools import chain


# /index 首页
class IndexView(View):

    def get(self, request):

        # 从缓存中拿取数据
        context = cache.get("index_cache_html")

        if context is None:

            try:
                # 查询类型
                type_all = Card_Type.objects.all()[:3]
                cards = Card.objects.filter().order_by('-create_time')[:10]

                # 统计人数
                peopels = User.objects.all().count()
                # 统计帖子数
                count = Card.objects.all().count()

                rand_ids = sample(range(1, count), 10)
                hots = Card.objects.filter(id__in=rand_ids)

                # 电子书
                books = Card_Type.objects.filter(name="电子书")
                books = Card.objects.filter(type=books).order_by('create_time').all()[:5]

                # 推荐资源
                recom = sample(range(1, count), 5)
                fives = Card.objects.filter(id__in=recom)

                # 从redis取出新闻资源
                con = get_redis_connection("default")

                blk = con.hgetall("block")
                smart = con.hgetall("smart")

                if all([blk, smart]):
                    bck = {}
                    smt = {}
                    # 遍历
                    for hd, ct in blk.items():
                        hd = hd.decode()
                        ct = ct.decode()
                        bck[hd] = ct

                    for hd, ct in smart.items():
                        smt[hd] = ct

                else:
                    bck, smt = Get_news()

                    # 组织上下文
                context = {
                    "type_all": type_all,
                    "cards": cards,
                    "hots": hots,
                    "books": books,
                    'fives': fives,
                    "count": count,
                    "peopels": peopels + 900,
                    "blk": bck,
                    "smart": smt
                }

            except Exception as e:
                # 出现异常

                logger.writeLog(e)

            # 设置缓存
            cache.set("index_cache_html", context)

        return render(request, 'index.html', context)


# /show 资源社区
class CardView(View):
    """资源社区界面"""

    def get(self, request, type_id):

        try:
            page = request.GET.get('page')
            sort = request.GET.get('sort')

        except Exception as e:
            return redirect(reverse('card:index'))

        page = int(page)

        try:
            # 查询单个类型资源
            type = Card_Type.objects.filter(id=type_id)
            # 查询所有类型
            type_all = Card_Type.objects.all()

        except Exception as e:
            # 出现异常
            logger.writeLog(e)
            print (e)
            return redirect(reverse('card:index'))

        if sort == 'new':

            type_card = Card.objects.filter(type=type).all().order_by('-create_time')


        elif sort == 'hot':
            type_card_all = Card.objects.filter(type=type).all()

            ret = {}
            for card in type_card_all:
                cot = Comment.objects.filter(card=card).count()
                ret[card.name] = cot

            # 以评论数排序
            rets = sorted(ret.items(), key=lambda item: item[1], reverse=True)

            # 再次查询添加list
            type_card = []
            for x in rets:
                card = Card.objects.get(name=x[0])
                type_card.append(card)


        else:
            sort = 'new'
            type_card = Card.objects.filter(type=type).all().order_by('-create_time')

        # 对数据进行分页
        paginator = Paginator(type_card, 8)

        # 获取第page页的内容
        try:
            page = int(page)
        except Exception as e:
            page = 1

        if page > paginator.num_pages:
            page = 1

        # 获取第page页的Page实例对象
        cards_page = paginator.page(page)

        # todo: 进行页码的控制，页面上最多显示5个页码
        # 1.总页数小于5页，页面上显示所有页码
        # 2.如果当前页是前3页，显示1-5页
        # 3.如果当前页是后3页，显示后5页
        # 4.其他情况，显示当前页的前2页，当前页，当前页的后2页
        num_pages = paginator.num_pages
        if num_pages < 5:
            pages = range(1, num_pages + 1)
        elif page <= 3:
            pages = range(1, 6)
        elif num_pages - page <= 2:
            pages = range(num_pages - 4, num_pages + 1)
        else:
            pages = range(page - 2, page + 3)

        if sort is None:
            sort = "new"
        # 组织上下文
        context = {
            "type_id": type_id,
            "type_all": type_all,
            'pages': pages,
            'cards_page': cards_page,
            'page': page,
            'sort': sort,
        }

        return render(request, 'resource.html', context)


# /card资源详情界面
class DetailsView(View):
    """显示详情界面"""

    def get(self, request, card_id):
        # 查询帖子
        card = Card.objects.get(id=card_id)

        user = request.user
        # 验证用户登入

        # 如果用户没登入增加隐士属性login
        if not user.is_authenticated():
            card.is_login = "login"

        card.no_login = user.id

        # 如果用户已经登入,检查用户是否已经评论
        if user.id is not None:
            user = User.objects.get(id=user.id)
            card.is_msg = 2

            msg = Comment.objects.filter(user=user, card=card)
            if (len(msg) == 0):
                card.is_msg = 1

        # 查询帖子评论
        comment = Comment.objects.filter(card=card).order_by('-create_time')
        count_comment = len(comment)
        comt = comment[:8]
        card.count_comment = count_comment
        card.comt = comt

        card.is_all = Card.STATUS[card.all_status]
        card.is_merber = Card.STATUS[card.merber_status]

        # 组织参数
        context = {
            'card': card
        }

        return render(request, 'card.html', context)

    def post(self, request, card_id):
        """处理评论请求"""

        # 接受参数
        comment = request.POST.get("comment")
        user_id = request.POST.get("user_id")
        card_id = request.POST.get("card_id")

        # 校验参数
        if not all([comment, user_id, card_id]):
            return JsonResponse({"msg": "0", "masg": "回复异常"})

        # 处理业务逻辑
        try:
            card = Card.objects.get(id=card_id)
            user = User.objects.get(id=user_id)
            Comment.objects.create(name=comment, user=user, card=card)

        except Exception as e:

            return JsonResponse({"msg": "0", "masg": "回复异常"})

        # 返回请求
        return JsonResponse({"msg": "1", "masg": "成功回复"})


# 评论成功
class Show_cardView(View):
    """显示"""

    def get(self, request):

        try:

            # 接受参数
            user = request.user
            card_id = request.GET.get("card_id")

            card = Card.objects.get(id=card_id)
            user = User.objects.get(id=user.id)

        except Exception as e:
            # 跳转到首页

            return redirect(reverse('card:index'))

        # 判断用户是否有评论
        if user.id is not None:
            user = User.objects.get(id=user.id)
            msg = Comment.objects.filter(user=user, card=card)

            if (len(msg) == 0):
                return JsonResponse({"msg": "0", "masg": "服务器繁忙"})

        masg = card.desc
        return JsonResponse({"msg": "1", "masg": masg})

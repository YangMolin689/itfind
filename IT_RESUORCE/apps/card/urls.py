from django.conf.urls import url
from .views import IndexView, CardView, DetailsView, Show_cardView

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),  # 首页
    url(r'^index$', IndexView.as_view(), name='index'),  # 首页
    url(r'^show/(?P<type_id>\d*)$', CardView.as_view(), name='show'),  # 资源社区中心
    url(r'^details/(?P<card_id>\d*)$', DetailsView.as_view(), name='details'),  # 帖子详情
    url(r'^show_card$', Show_cardView.as_view()),  # 返回链接资源

]

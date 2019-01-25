from django.conf.urls import url
from .views import RegisterView, LoginView, LogoutView, UserInfoView, UpdateView, Update_psView

urlpatterns = [
    url(r'^register$',RegisterView.as_view(),name='register'),#注册
    url(r'^login$', LoginView.as_view(), name='login'),#登入
    url(r'^logout$', LogoutView.as_view(),name="logout"),#退出
    url(r'^$', UserInfoView.as_view(), name='user'),  # 用户中心-信息页
    url(r'update$',UpdateView.as_view(), name="update"), #修改
    url(r'update_ps/(?P<token>.*)$',Update_psView.as_view(), name="up"),
    # url(r'update_user_act$', Update_user_head.as_view(), name="up_act")

]

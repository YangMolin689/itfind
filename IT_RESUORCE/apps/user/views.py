import re
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View
from apps.logs.MyLog import logger
from utils.mixin import LoginRequiredMixin
from django.core.mail import send_mail
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from .models import User
from celery_tasks.tasks import send_update_active_email
from django.core.cache import cache


# Create your views here.
# /user/register 用户注册
class RegisterView(View):
    '''注册'''

    def get(self, request):
        '''显示注册页面'''
        return render(request, 'register.html')

    def post(self, request):
        '''进行注册处理'''
        # 接收数据
        name = request.POST.get('user_name')
        password = request.POST.get('pwd')
        cpassword = request.POST.get('cpwd')
        username = request.POST.get('email')
        allow = request.POST.get('allow')

        # 去除空格
        username = username.replace(' ', '')
        password = password.replace(' ', '')
        cpassword = cpassword.replace(' ', '')

        # 验证2次密码填写
        if password != cpassword:
            return render(request, 'register.html', {'errmsg': '密码填写错误'})

        # 进行数据校验
        if not all([username, password, cpassword, name]):
            # 数据不完整
            return render(request, 'register.html', {'errmsg': '数据不完整'})

        # 判断长度
        if not all([2 < len(name) < 10, 6 < len(password) < 16]):
            return render(request, 'register.html', {'errmsg': '密码或账号长度错误'})

        # 校验邮箱
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', username):
            return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})

        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请同意协议'})

        # 校验用户名是否重复
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 用户名不存在
            user = None

        if user:
            # 用户名已存在
            return render(request, 'register.html', {'errmsg': '邮箱已存在'})

        try:
            # 进行业务处理: 进行用户注册
            user = User.objects.create_user(username, username, password)
            user.is_active = 1
            user.name = name
        except Exception as e:
            logger.writeLog(e)
            return render(request, 'register.html', {'errmsg': '注册异常'})

        # 注册成功保存用户信息
        user.save()
        return redirect(reverse('user:login'))


# 用户登入
# /user/login
class LoginView(View):
    """ 登入页"""

    next_url  = None

    def get(self, request):
        '''显示登录页面'''

        next_url= request.GET.get("next")
        LoginView.next_url = next_url


            # 判断是否记住了用户名
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            checked = 'checked'
        else:
            username = ''
            checked = ''

            # 判断用户是否登入
        user = request.user
        if user is not None:
            redirect(reverse("card:index"))

        # 使用模板
        return render(request, 'login.html', {'username': username, 'checked': checked})

    def post(self, request):
        '''登录校验'''
        # 接收数据
        username = request.POST.get('username')
        password = request.POST.get('pwd')



        # 校验数据
        if not all([username, password]):
            return render(request, 'login.html', {'errmsg': '数据不完整'})

        # 获取
        ip = None
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]  # 真实的ip
        else:
            ip = request.META.get('REMOTE_ADDR')  # 这里获得代理ip

        # 获取用户登入错误次数
        time_ip = "ip_num_%s" % ip
        tms = cache.get(time_ip)

        if tms is not None:
            # 验证密码错误次数
            if int(tms) >= 5:
                return render(request, 'login.html', {'errmsg': '次数错误过多请10分钟再试'})

        # 业务处理:登录校验
        user = authenticate(username=username, password=password)

        if user is not None:
            # 用户名密码正确

            # 记录用户的登录状态
            login(request, user)

            # 获取登录后所要跳转到的地址


            if LoginView.next_url is not None and LoginView.next_url != '/register' and LoginView.next_url !='login':
                next = LoginView.next_url
            else:
                next = reverse('card:index')

            # 跳转到next
            response = redirect(next)  # HttpResponseRedirect

            # 判断是否需要记住用户名
            remember = request.POST.get('remember')

            if remember == 'on':
                # 记住用户名
                response.set_cookie('username', username, max_age=7 * 24 * 3600)
            else:
                response.delete_cookie('username')
            # 返回response
            return response

        else:
            errmsg = None
            # 获取用户ip
            user_ip = cache.get("ip_num_%s" % ip)

            # 判断用户是否登入错误过
            if user_ip is None:
                cache.set("ip_num_%s" % ip, 1)

                cache.expire("ip_num_%s" % ip, 600)

                return render(request, 'login.html', {'errmsg': "用户名或密码错误,你已剩下登入4次机会"})

            else:
                cache.incr("ip_num_%s" % ip, 1)
                cache.expire("ip_num_%s" % ip, 600)

                # 重新获取次数
                tm = cache.get("ip_num_%s" % ip)
                tm = 5 - int(tm)

                errmsg = "用户名或密码错误,你已剩下登入" + str(tm) + "次机会"

            # 用户名或密码错误
            return render(request, 'login.html', {'errmsg': errmsg})


# /user/logout
# 用户退出
class LogoutView(View):
    '''退出登录'''

    def get(self, request):
        '''退出登录'''
        # 清除用户的session信息
        logout(request)

        # 跳转到首页
        return redirect(reverse('card:index'))


# /user/user
# 用户信息中心
class UserInfoView(LoginRequiredMixin, View):

    # 获取页面
    def get(self, request):
        # 获取用户的订单信息
        user = request.user
        if user.id == 0:
            user.act ="NO"
        else:
            user.act ="YES "

        return render(request, 'user_center.html')


    def post(self, request):

        user = request.user
        #获取当前用户

        avatar = request.FILES.get('act')
        #头像

        try:
            user.image = avatar
            user.save()
        except Exception as e:
            return  JsonResponse({"msg":"0"})

        return  JsonResponse({"msg":"1"})



# /user/update
#修改页面的显示
class UpdateView(View):
    """显示页面"""

    def get(self, request):

        return render(request, 'update.html')

    def post(self, request):

        # 接收参数
        username = request.POST.get('user_name')

        # 校验邮箱
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', username):
            return render(request, 'update.html', {'errmsg': '邮箱格式不正确'})

        try:
            user = User.objects.get(username=username)
        except Exception as  e:
            logger.writeLog(e)
            return render(request, 'update.html', {'errmsg': '邮箱不存在或错误'})

            # 发送激活邮件，包含修改链接: http://127.0.0.1:8000/user/active/3
            # 激活链接中需要包含用户的身份信息, 并且要把身份信息进行加密


        # 加密用户的身份信息，生成激活token

        serializer = Serializer(settings.SECRET_KEY, 3600)
        info = {'confirm': user.id}
        token = serializer.dumps(info)  # bytes
        token = token.decode()
        send_update_active_email.delay(username, user.name, token)

        return render(request, 'login.html', {'errmsg': '发送成功请等待'})


#修改提交数据
# user/update_up
class Update_psView(View):
    def get(self, request, token):

        return render(request, 'update_ps.html', {'token': token})

    def post(self, request, token):
        # 接收参数
        # 验证参数
        serializer = Serializer(settings.SECRET_KEY, 900)
        try:
            info = serializer.loads(token)
            # 获取带激活的用户的id
            user_id = info['confirm']

            # 根据用户获取id,激活用户id
            user = User.objects.get(id=user_id)
        except Exception as e:
            # 激活链接已过期
            return JsonResponse({"status": "0", "msg": "链接过期"})

        password = request.POST.get('pwd')
        cpassword = request.POST.get('cpwd')

        # 进行数据校验
        if not all([password, cpassword]):
            # 数据不完整
            return JsonResponse({"status": "0", "msg": "数据不完整"})

        password = password.replace(' ', '')
        cpassword = cpassword.replace(' ', '')

        # 验证2次密码填写
        if password != cpassword:
            return JsonResponse({"status": "0", "msg": "密码不相同"})

        # 判断长度
        if not all([6 < len(password) < 16]):
            return JsonResponse({"status": "0", "msg": "长度错误"})

        # 设置密码
        user.set_password(password)
        user.save()

        print("保存完毕")
        return JsonResponse({"status": 1, "msg": "修改成功"})











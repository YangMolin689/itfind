# 使用celery
from django.core.mail import send_mail
from django.conf import settings
from celery import Celery
from django_redis import get_redis_connection
from django.template import loader

from random import sample


import time
# 在任务处理者一端加这几句
import os
import django

#导入Djano配置
from utils.spider import Get_news

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "IT_RESUORCE.settings")
django.setup()


from apps.card.models import  Card_Type,Card,Comment
from  apps.user.models import User



# 创建一个Celery类的实例对象
app = Celery('celery_tasks.tasks', broker='redis://172.18.2.58/3')


# 定义任务函数
@app.task
def send_update_active_email(to_email, username, token):

    print("正在发送")
    '''发送激活邮件'''
    # 组织邮件信息
    subject = 'IT_FIND 欢迎您修改密码'
    message = ''
    sender = settings.EMAIL_FROM
    receiver = [to_email]
    html_message = '<h1>%s, 欢迎您修改密码</h1>请点击下面链接修改你的您的账户密码<br/><a href="http://127.0.0.1:8000/user/update_ps/%s">http://127.0.0.1:8000/user/update_ps/%s</a>' % (username, token, token)

    send_mail(subject, message, sender, receiver, html_message=html_message)












from django.db import models
from django.contrib.auth.models import AbstractUser
from db.base_model import BaseModel



class User(AbstractUser, BaseModel):
    '''用户模型类'''
    image = models.ImageField(upload_to='type', verbose_name='头像路径',null=True)
    name = models.CharField(max_length =20, verbose_name="名字", default='' )
    class Meta:
        db_table = 'it_user'
        verbose_name = '用户表'
        verbose_name_plural = verbose_name


    def __str__(self):
        return self.username






















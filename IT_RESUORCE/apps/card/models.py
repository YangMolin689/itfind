from django.db import models
from db.base_model import BaseModel
from apps.user.models import User
from tinymce.models import HTMLField


# Create your models here.


# 帖子类型
class Card_Type(BaseModel):
    name = models.CharField(max_length=20, verbose_name='资源类型')

    db_table = 'it_card_types'
    verbose_name = '帖子类型'
    verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


# 首页轮播图
class IndexGardsBanner(BaseModel):
    '''首页轮播商品展示模型类'''
    image = models.ImageField(upload_to='type', verbose_name='图片')
    index = models.SmallIntegerField(default=0, verbose_name='展示顺序')  # 0 1 2 3

    class Meta:
        db_table = 'it_index_banner'
        verbose_name = '首页轮播商品'
        verbose_name_plural = verbose_name


# 帖子
class Card(BaseModel):
    '''帖子'''
    STATUS_ALL = (
        (0, '否'),
        (1, '是'),
    )

    STATUS = {
        0: "否",
        1: "是",

    }
    type = models.ForeignKey(Card_Type, verbose_name='帖子类型')
    user = models.ForeignKey(User, verbose_name='帖子发表人')
    name = models.CharField(max_length=200, verbose_name='帖子名称')
    way = models.CharField(max_length=20, verbose_name='下载方式')
    size = models.CharField(max_length=20, verbose_name='资源大小')
    desc = HTMLField(verbose_name='帖子详情')
    all_status = models.SmallIntegerField(choices=STATUS_ALL, default=1, verbose_name='是否全套')
    merber_status = models.SmallIntegerField(choices=STATUS_ALL, default=0, verbose_name='是否需要会员')

    class Meta:
        db_table = 'it_card'
        verbose_name = '帖子'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


# 帖子评论
class Comment(BaseModel):
    name = models.CharField(max_length=200, verbose_name='帖子评论')
    user = models.ForeignKey(User, verbose_name='评论人_id')
    card = models.ForeignKey(Card, verbose_name='帖子_id', null=True)

    db_table = 'it_comments'
    verbose_name = '评论'
    verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


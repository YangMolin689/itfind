import  requests
from  lxml import  etree
import  threading
from django_redis import get_redis_connection


import redis

class Block():
    def __init__(self):

        self.headers ={"User-Agent":"Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;"}
        self.rd = redis.Redis(host='172.18.2.58', port=6379,db =2)


    def parse_url(self,url,bm=None):
        self.url = url
        response = requests.get(url=url, headers=self.headers)

        return response.content.decode(bm)

    def get_conetent_list(self,html_str,hd,ct):# 提取数据


       html = etree.HTML(html_str)
       #解析
       head_l = html.xpath(hd)[0:10]

       content_l = html.xpath(ct)[0:10]

       return  head_l,content_l
       #提取字符



    def run(self,name,url,hd,ct,bm):
        #求求内容
        html_str = self.parse_url(url,bm)

        #拿到结果
        head_list,content_list = self.get_conetent_list(html_str,hd,ct)

        #存入数据库
        for head, cont in zip(head_list,content_list):

            if 'http' in cont:
                self.rd.hset(name, head, cont)
                self.rd.expire(name,18888)
            else:
                cont = self.url + cont
                self.rd.hset(name, head, cont)
                self.rd.expire(name,18888)


    @classmethod
    def run_spider(Block):

        Threads = []
        bok = Block()
        hd = "//div[@style='margin-bottom:24px;margin-top:-8px;']//div[@class='article-item-warp']//div[@class='article-item bbt-clearfix']//div[@class='article-item__body']//h3[@class='article-item__title']//a//text()"
        ct = "//div[@style='margin-bottom:24px;margin-top:-8px;']//div[@class='article-item-warp']//div[@class='article-item bbt-clearfix']//div[@class='article-item__body']//h3[@class='article-item__title']//a//@href"
        url = "https://www.8btc.com"
        na = "block"
        bm = 'utf-8'
        # bok.run(na,url,hd,ct,bm)

        t1 = threading.Thread(target=bok.run(na, url, hd, ct, bm), args=())
        Threads.append(t1)

        smt = Block()
        ha = "//div[@class='ai-main-cont mt15']//div[@class='w1000 clearfix']//div[@class='main-cont-left w640']//div[@class='item-box-right clearfix']//div[@class='top-title mtl15']//a/text()"
        cn = "//div[@class='ai-main-cont mt15']//div[@class='w1000 clearfix']//div[@class='main-cont-left w640']//div[@class='item-box-right clearfix']//div[@class='top-title mtl15']//a/@href"
        ur = "https://ai.ofweek.com/CATList-201700-8100-ai.html"
        nm = "smart"
        bmm = "gb18030"
        # smt.run(nm,ur,ha,cn,bmm)

        t2 = threading.Thread(target=smt.run(nm, ur, ha, cn, bmm), args=())
        Threads.append(t2)

        for t in Threads:
            t.setDaemon(True)
            t.start()




def Get_news():
    try:
        Block.run_spider()
        bck = {}
        smt = {}
        con = get_redis_connection("default")

        smart = con.hgetall("smart")
        blk = con.hgetall("block")


        if all([blk, smart]):
            # 遍历
            for hd, ct in blk.items():
                hd = hd.decode()
                ct = ct.decode()
                bck[hd] = ct

            for hd, ct in smart.items():
                smt[hd] = ct
            print("调用get")
        return  bck,smt
    except Exception as e:
        blk = ""
        smt = ""
        return blk,smt


















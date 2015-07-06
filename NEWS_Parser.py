#!usr\bin\env python
#encoding:UTF-8

import urllib,re,os,sys,socket
from BeautifulSoup import BeautifulSoup
from datetime import date
import MySQLdb

"""
默认站点列表，各站点的标签及其说明如下：
凤凰资讯(IFENG)
IFENG:"http://news.ifeng.com/rt-channel/rtlist_"+Year+Month+Day+"/"+str(pageNum)+".shtml"
IFENG:财经滚动"http://finance.ifeng.com/cmppdyn/103/123/1/dynlist.html"
"""


class newsDAO():
    
    def __init__(self):
        pass
    def newsDAO(self,stmt):      
        conn = MySQLdb.connect(host="localhost",user="root",passwd="root",port=3306,charset="utf8")
        cursor=conn.cursor()
        try:
            cursor.execute('create database if not exists news')
            conn.select_db('news')

            cursor.execute('CREATE TABLE IF NOT EXISTS new(publishdate datetime,pubname varchar(100),keywords varchar(50),title varchar(50),url varchar(100),content TEXT) CHARACTER SET utf8')
        
            conn.query(stmt)
            conn.commit()
            cursor.close()
            conn.close()
        except MySQLdb.Error,e:
            print "Error %d: %s" %(e.args[0],e.args[1])

class URLparser():
    def __init__(self):
        self.tag = 0
        socket.setdefaulttimeout(20)
        #self.num = 0
        

    #获取每一个页面的URL
    def get_url(self,i):
        url = 'http://finance.ifeng.com/cmppdyn/103/123/'+str(i)+'/dynlist.html'
        st = urllib.urlopen(url)
        stock = st.read()
        href = re.findall(r'<li><span class="txt01"><a  href="(http://.*?.shtml)".*?([\d]{4}-[\d]{2}-[\d]{2} [\d]{2}:[\d]{2}).*?',stock,re.I)
        return href

    #获取每个链接的内容
    def getcontent(self,path):
        DB=newsDAO()
        i = 13830
        while i <= 15000:
            m = self.get_url(i)
            i+=1
            for url in m:
                fileName = "IFENG"+"-"+str(self.tag)
                try:
                    self.tag+=1
                    html = urllib.urlopen(url[0])
                    text = html.read()
                    soup = BeautifulSoup(text,fromEncoding="gb18030")
                    news = self.IFENGNewsParser(soup)
                    news['pubdate'] = str((url[1]+':00').encode('utf-8'))
                    news['keywords'].decode('utf-8')
                    dirs = url[0].split('/')[4]
                    path1 = path+str(dirs)+'\\'
                    isExists = os.path.exists(path1)
                    if not isExists:
                        os.makedirs(path1)
                        self.tag = 0
                    else:
                        pass
                    
                    f = open(path1+fileName+'.txt','w+')
                    f.write(news['title']+'\n'+news['pubdate']+'\n'+url[0]+'\n'+news['pubname']+'\n'+news['keywords']+'\n'+news['content'])

                    stmt = 'insert into new(publishdate,pubname,keywords,title,url,content) values(\'%s\',\'%s\',\'%s\',\'%s\',\'%s\',\'%s\')' % (news['pubdate'],news['pubname'],news['keywords'],news['title'],url[0],news['content'])
                    DB.newsDAO(stmt)
                    print "Get "+ str(self.tag) + " " + 'IFENG' + " news successfully."
                except:
                    print "Something worng when getting "+ 'IFENG' +"news:"+url[0]
                    pass
        print "Get "+ str(self.tag) + " news successfully."
        return True

    #获取新闻内容
    def IFENGNewsParser(self,soup):
        news=dict()
        newscontents = ''
        newstitle = ''
        pubdate = ''
        keyw = ''
        keywords = ''
        news['pubname'] = 'IFENG'

        contenttitle = soup.find('h1',id='artical_topic')
        keyw = soup.find('p',attrs={"class":"p01 ss_none"})
        if contenttitle:
            newstitle = str(contenttitle.getText().encode('utf-8'))
        else:
            newstitle = ''

        if keyw:
            try:
                a=keyw.find('a')
                if not a.find('script'):
                    keywords=keywords+str(a.getText().encode('utf-8'))
                while a.findNextSibling('a'):
                    a = a.findNextSibling('a')
                    if not a.findNextSibling('script'):
                        keywords=keywords+','+str(a.getText().encode('utf-8'))
            except:
                keywords = ''
 
        contentbody = soup.find('div',id='main_content')
        if contentbody:
            try:
                p = contentbody.find('p')
                if not p.find('script'):
                    newscontents += str(p.getText().encode('utf-8'))
                while p.findNextSibling('p'):
                    p = p.findNextSibling('p')
                    if not p.find('script'):
                        newscontents += str(p.getText().encode('utf-8'))
            except:
                print "there is a worng....content NULL"
                pass
        news['keywords'] = keywords 
        news['content'] = newscontents
        news['title'] = newstitle
        news['pubdate'] = pubdate    
        return news

print u"""
#-----------------------------------------------------------------------------
    软件名称：凤凰网财经新闻采集器
    作   者：Venson
    时   间：2015-03
    版   本：1.0
#------------------------------------------------------------------------------
"""
if __name__=="__main__":
    UrlPar = URLparser()
    path = os.getcwd()+'\\IFENG'+'\\'+str(date.today()).replace('-','')+'\\'
    """isExists = os.path.exists(path)
    #如果路径不存在创建
    if not isExists:
        os.makedirs(r"%s\%s"%(os.getcwd()+'\\IFENG',str(date.today()).replace('-','')))
    else:
        pass
    """
    UrlPar.getcontent(path)
    raw_input()

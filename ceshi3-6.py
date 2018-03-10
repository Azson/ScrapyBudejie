from urllib import request
from bs4 import BeautifulSoup as BS
import re
import sqlite3

def updateTable(data):
    #print("SELECT * FROM User WHERE UserId = \'" + str(data['userId'][0]) + "\'")
    cur.execute("SELECT * FROM User WHERE UserId = \'" + str(data['userId']) + "\'")
    result = cur.fetchall()
    try:
        if (len(result) == 0):
            #print("INSERT INTO User VALUES (\"{}\", \"{}\", \"{}\")".format(data['writer'], data['userId'],data['portrait']))
            cur.execute("INSERT INTO User VALUES (\"{}\", \"{}\", \"{}\")".format(data['writer'], data['userId'],data['portrait']))
            cx.commit()
    except Exception as e:
        print(e)
        print("插入用户数据失败!")
    try:
        #字符串大小匹配算法不一样
        cur.execute("SELECT Max(cast(markId as BIGINT)) FROM mark")
        result = cur.fetchone()
        if(result[0] is None):
            result = 1
        else:
            result = int(result[0]) + 1
        #print(result, type(result))
        #print("INSERT INTO mark VALUES (\"{}\", \"{}\", {}, {}, \"{}\", {}, {}, \"{}\", \"{}\")".format(result, data['mark'], data['agreeNum'], data['disagreeNum'], data['pub_time'], data['markNum'],data['shareNum'], data['userId'], data['picUrl']))

        cur.execute(
            "INSERT INTO mark VALUES (\"{}\", \"{}\", {}, {}, \"{}\", {}, {}, \"{}\", \"{}\")".format(result, data['mark'], data['agreeNum'], data['disagreeNum'], data['pub_time'], data['markNum'],data['shareNum'], data['userId'], data['picUrl']))
        cx.commit()
    except Exception as e:
        print(e)
        print("信息插入失败！")


def getPageInfo(url):
    cnt = 0
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0"}
    html = request.Request(url, headers=headers)
    html = request.urlopen(html)
    bsObj = BS(html, "lxml")

    itemList = bsObj.findAll("li")
    # print(itemList)
    data = {}
    print("------------------------")
    for item in itemList:
        for tmp1 in item.findAll("div", {"class": "j-list-user"}):
            # print("tmp1 {}".format(tmp1))
            try:
                writer = tmp1.find("a", {"class": "u-user-name"})
                userId = writer.attrs['href']
                # print("type is {} content is {}".format(type(userId), re.findall(r"-(\d+).html", userId)))
                data['userId'] = re.findall(r"-(\d+).html", userId)[0]
                data['writer'] = writer.get_text()
                data['pub_time'] = tmp1.find("span", {"class": "u-time f-ib f-fr"}).get_text()

                data['mark'] = item.find("div", {"class": "j-r-list-c-desc"}).find("a").get_text()

                data['agreeNum'] = item.find("li", {"class": "j-r-list-tool-l-up"}).find("span").get_text()
                data['disagreeNum'] = item.find("li", {"class": "j-r-list-tool-l-down"}).find("span").get_text()

                data['markNum'] = item.find("span", {"class": "comment-counts"}).get_text()

                data['shareNum'] = item.find("div", {"class": "j-r-list-tool-ct-share-c"}).find("span").get_text()
                data['shareNum'] = re.findall("(\d)+", data['shareNum'])[0]
                # picUrl = item.find("img", {"src":re.compile(r"[]+\.(jpg|png|gift)")})
                # print("___- {}".format("\[^]+\.(jpg\|png\|gift)"))
                picUrl = item.find("div", {"class": "j-r-list-c-img"})
                data['portrait'] = item.find("div", {"class": "j-list-user"}).img.attrs['data-original']

                print("作者：{}, ID:{} ,发表时间: {}".format(data['writer'], data['userId'], data['pub_time']))
                print("他的头像是: {}".format(data['portrait']))
                print("说了: {}".format(data['mark']))
                print("支持的人数有{}人，反对的人数有{}人".format(data['agreeNum'], data["disagreeNum"]))
                print("有{}人参与了评论,{}人将它分享了出去".format(data["markNum"], data["shareNum"]))
                if (picUrl is not None):
                    # picUrl.find(re.compile("<img [A-Za-z0-9\.\\\\/]+ >"))
                    data["picUrl"] = picUrl.img.attrs["data-original"]

                    if (picUrl is not None):
                        print("他还发表了图片: {}".format(data["picUrl"]))
                print("")
                cnt += 1

                updateTable(data)
            except Exception as e:
                print(e)
    print("在URL= {}，爬取了 {} 条信息\n".format(url, cnt))

#http://www.budejie.com/
#http://www.pythonscraping.com/pages/page3.html


cx = sqlite3.connect("budejie1.db")
if __name__ == '__main__':

    cur = cx.cursor()
    for i in range(1, 51):
        getPageInfo("http://www.budejie.com/pic/" + str(i))

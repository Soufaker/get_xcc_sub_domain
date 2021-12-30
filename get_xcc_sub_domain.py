#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# time:2021/11/11
# author:Soufaker

import requests
import json
import sys
import time

# 获取APP_ID列表
def Get_App_Id_List(query,number,cookie):
    headers={"User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63030073)"}
    url = "https://mp.weixin.qq.com/wxa-cgi/innersearch/subsearch"
    params = "query=" + query + "&cookie=" + cookie + '&subsys_type=1&offset_buf= {"page_param":[{"subsys_type":1,"server_offset":0,"server_limit":' + str(number) + ',"index_step":' + str(number) + ',"index_offset":0}],"client_offset":0,"client_limit":' + str(number) + '}'
    response = requests.post(url=url, params=params, headers=headers, timeout=10).text
    Apps_Json = json.loads(response)
    print(Apps_Json)
    try:
        App_Items = Apps_Json['respBody']['items']
        for App_Item in App_Items:
            App_Item_Json = json.loads(json.dumps(App_Item))  # 重新加载嵌套内容中的json数据
            App_Id = App_Item_Json['appid']
            App_Name = App_Item_Json['nickName']

            if query in App_Name:
                App_Id_List.append(App_Id)
                print(App_Name)
    except:
        print('连接异常')

# 获取小程序域名
def Get_Domain(X_APP_ID):
    headers={ "User-Agent": "Mozilla/5.0 (Linux; Android 6.0.1; MuMu Build/V417IR; wv)" } #微信两个校验值
    url = "https://mp.weixin.qq.com/wxawap/waverifyinfo?"
    params = "action=get&wx_header=1&appid=" + X_APP_ID
    response = requests.get(url=url, params=params, headers=headers).text
    resp = response.replace(' ', '').replace('\n', '').replace('\t', '').replace("\"", "")
    try:
        if "request_domain:{item:[" in resp:
            Response_domain_list = Get_MiddleStr(resp,"request_domain:{item:[",",]}};</sc")
            real_list = black_domain_filter(Response_domain_list)

            # 将要批量跑的域名写入列表1
            for r in real_list:
                All_domain_list.append(r)

            real_list.insert(0,X_APP_ID)
            real_list.insert(0,'------')

            print(real_list)

            # 将要查询的域名写入列表2
            All_domain_list2.append(real_list)


    except:
        print('连接出现异常,请稍后重试或更换IP重试！')

    time.sleep(0.1)

# 将一些不属于小程序的域名加入黑名单处理过滤
def black_domain_filter(res_domain_list):
    black_domain_list = ['qq.com','gov.cn']
    real_domian_list = []
    for res in res_domain_list:
        flag = 0
        for bl in black_domain_list:
            if bl in res:
                flag = 1

        if flag == 0:
            real_domian_list.append(res)

    return real_domian_list

# 选取想要的域名元素
def Get_MiddleStr(content,startStr,endStr): #获取中间字符串的⼀个通⽤函数
	startIndex = content.index(startStr)
	if startIndex>=0:
		startIndex += len(startStr)
		endIndex = content.index(endStr)
	return content[startIndex:endIndex].split(',')


# 将跑出的域名写入文本
def write_domain_list(query,all_domain_list,all_domain_list2):
    t = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
    with open(query + '批量用'+ t + '.txt', 'w+', encoding='utf-8') as f:
        for l in set(all_domain_list):
            f.writelines(l+'\n')

    with open(query + '查询用'+ t + '.txt', 'w+', encoding='utf-8') as f:
        f.writelines('如果想查询某个域名属于哪个小程序,请访问地址:https://mp.weixin.qq.com/wxawap/waverifyinfo?action=get&appid=加上域名列表前的APPID即可')
        for l in all_domain_list2:
            str1 = ''
            for i in l:
                str1 =str1+i+','
            f.writelines(str1+'\n')

if __name__ == '__main__':
    sys.getdefaultencoding()  # 解决编码问题
    query = input("请输⼊要搜的微信⼩程序名称: ")
    number = input("请指定要返回的⼩程序的数量: ")
    cookie = input("请输⼊你获取到的Cookie信息: ")

    App_Id_List = []
    All_domain_list = []  # 存放一个用来批量测试的域名列表
    All_domain_list2 = []  # 提供一个查询列表
    Get_App_Id_List(query,number,cookie)

    # 当APP_ID_LIST为空时结束循环
    while App_Id_List:
        app_id = App_Id_List.pop(0)
        Get_Domain(app_id)

    # 写入文本
    write_domain_list(query, All_domain_list,All_domain_list2)

    print('程序结束')



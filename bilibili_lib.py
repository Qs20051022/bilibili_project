# bilibili html解析函数库
import re
import requests
from lxml import etree
import json
from process_lib import *
from user_config import *

# bilibili请求头
bilibili_head = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0",
    "Referer": "https://www.bilibili.com/",
    "Cookie": "CURRENT_FNVAL=4048; buvid3=BE2D386A-BBCB-E06E-8C2B-F5223B4C8BC517591infoc; b_nut=1721567317; _uuid=67165DF10-7B77-BDE8-3C63-732C2FCAF4D520375infoc; enable_web_push=DISABLE; buvid4=0245F01B-6C4B-CD5A-2EC5-BC060EC0777D18433-024072113-zRTpkL0r94scQqxGfSYKhQ%3D%3D; home_feed_column=5; header_theme_version=CLOSE; rpdid=|(Y|RJRR)Y~0J'u~kulY~Rkk; DedeUserID=1611307689; DedeUserID__ckMd5=b0865dba0b3ced5b; buvid_fp_plain=undefined; is-2022-channel=1; b_lsid=D8542F24_191412D93C0; bsource=search_bing; bmg_af_switch=1; bmg_src_def_domain=i1.hdslb.com; browser_resolution=1659-943; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MjM2MzQ1OTMsImlhdCI6MTcyMzM3NTMzMywicGx0IjotMX0.Ox8rnEpQH5i1H_wQfH2z5CzZC0y8PlqQCy1KVa8XEfQ; bili_ticket_expires=1723634533; SESSDATA=f567fef6%2C1738927393%2C5d207%2A82CjAh2pSUKwDLr1XiI6ncU5B6NXEfWKS7ES6mDC8yGxM6aT3-BTdvK0KAlYpMhCXtEXgSVkl2aTlQWUNacTZOZ0ZNXzJwZ21QT2ozMXFXcWtFc1FpNnBIWlNWbml2Y3BxNV80bUNMZTBVN1dyb3h0STU1ZklDM0MwckJvanRmTmNkeTBFcW5qYl9RIIEC; bili_jct=8d788bcb503d69ba2ded7dfbb53f6e58; sid=71po5kkf; fingerprint=0c7279b7c69b9542a76b8d9df9b7872a; buvid_fp=BE2D386A-BBCB-E06E-8C2B-F5223B4C8BC517591infoc; bp_t_offset_1611307689=964382000909647872"
}


# bangumi-> bangumi set ,single bangumi,bangumi append
# set->ordinary set ,complex set
# BV_AV号索引可能得到 普通视频 番剧电影单集/贴片 分集视频 合集视频 合集嵌套合分集视频
# 从BVAV号获取info
# 传入参数：BV/AVid
# 返回值：info：
# info格式 [ID号,标题，分集id列表[]，分集标题列表[]，视频类型标签]
# 视频类型标签 (0: 一般视频，1: 番剧电影，2:分集视频，3:合集视频，4:合集嵌套合分集视频（BV1wZyHYSEc5，BV17j28YqEv6），5:番剧电影贴片 或 通过BV号索引的单集番剧视频,"unknown":未知) 番剧的附带类型怎么办？
# 视频类型标签 (一般视频(ordinary video)，1: 番剧电影(bangumi set)，2:分集视频(episode video)，3:合集视频(ordinary set)，4:合集嵌套合分集视频（BV1wZyHYSEc5，BV17j28YqEv6）(complex set)，5:通过BV号索引的单集番剧视频(single bangumi)，番剧电影相关视频(bangumi append),"unknown":未知) 番剧的附带类型怎么办？

# 合集视频info格式 [合集标题，atmo_list[]，视频类型标签=3]
# 一般视频,分集视频，番剧电影贴片与atmo的info格式 [ID号,标题，分集id列表[]，分集标题列表[]，视频类型标签]
def from_BVAVid_get_info(BVAV_id):
    # 一、请求返回html
    target_url = "https://www.bilibili.com/video/" + BVAV_id
    response = requests.get(target_url, headers=bilibili_head)
    res_text = response.text
    tree = etree.HTML(res_text)
    # 二、判断视频类型
    identity_flag = type_distinguish(res_text)
    # 三、获取详细信息
    if identity_flag == "ordinary video":  # 一般视频
        info = get_ordinary_video_info(res_text)
        # info格式 [ID号,标题,视频类型标签]
    elif identity_flag == "episode video":  # 分集视频
        info = get_episode_video_info(res_text)
        # info格式 [ID号,标题，分集id列表[]，分集标题列表[]，视频类型标签]
    elif identity_flag == "bangumi":  # 单集番剧电影或单集番剧电影贴片
        info = get_bangumi_info(res_text, "BVid")
        # [ID号,标题，分集id列表[]，分集标题列表[]，视频类型标签]
    elif identity_flag == "set":  # 合集视频(一般合集，复杂合集)
        info = get_set_info(res_text)
        # info格式 [合集id,标题，atmo_list，视频类型标签=ordinary set]
        # info格式 [合集id，标题,分集列表section_list[section]，视频类型标签=complex set]
        # section[]格式 [section_id,标题，atmo_list[atmo]，视频类型标签=ordinary set]
    else:
        set_id = "unknown"
        set_title = "unknown"
        episode_id_list = "unknown"
        episode_title_list = "unknown"
        identity_flag = "unknown"
        # 合成info
        info = [set_id, set_title, episode_id_list, episode_title_list, identity_flag]
        # info格式 [ID号,标题，分集id列表[]，分集标题列表[]，视频类型标签]
    # display_info_list([info])  # 展示用
    return info


#  从ssep号获取info
# 传入参数：ss/epid
# 返回值：info：
# info格式 [ID号,标题，这是第..集,集数id列表[]，分集标题列表[]，视频类型标签]
# 视频类型标签 (1: 番剧电影)
# 番剧电影：集数id列表= [第一集ID，第二集ID，第三集ID，第四集ID，第五集ID，第六集ID](epid)
# ID号统一为ss
def from_ssepid_get_info(ssep_id, type):
    # 一、请求返回html
    # identity_flag = "bangumi"  # 番剧电影
    target_url = "https://www.bilibili.com/bangumi/play/" + ssep_id
    response = requests.get(target_url, headers=bilibili_head)
    res_text = response.text
    tree = etree.HTML(res_text)
    if type == "epid":  # 单集番剧电影或单集番剧电影贴片
        info = get_bangumi_info(res_text, "epid")
    elif type == "ssid":  # 番剧电影合集
        info = get_bangumi_info(res_text, "ssid")
    else:
        print("ssepid_type_error")
        return
    # info格式 [ID号,标题，分集id列表[]，分集标题列表[]，视频类型标签]
    return info


# 从搜索页面获取id
# 传入参数：关键词keyword 分区target_area 页数page_id
# 返回值：id_list [[id,id类型]...]
# id类型 ssid,epid ,BVid
# 其中分区可以为 all：综合, video：视频, bangumi：番剧, pgc：影视, live：直播, article：专栏, upuser：用户
# 页数为需要返回的页面编号

def from_search_page_get_id(keyword, target_area="all", page_id=1):
    target_url = "https://search.bilibili.com/" + target_area + "?keyword=" + keyword + "&page=" + str(page_id)
    response = requests.get(target_url, headers=head)
    tree = etree.HTML(response.text)
    id_list = []
    bangumi_url_list = tree.xpath(
        '//a[@title and @class="text_ellipsis" and @target="_blank" and contains(@href,"www.bilibili.com/bangumi/play/")]/@href')
    for url in bangumi_url_list:
        id = re.findall('(ss[0-9a-zA-Z]+)', url)
        if len(id) == 0:
            id = re.findall('(ep[0-9a-zA-Z]+)', url)
            id = id[0]
            id_list.append([id, "epid"])
        else:
            id = id[0]
            id_list.append([id, "ssid"])
    normal_url_list = tree.xpath(
        '//div[@class="bili-video-card__wrap __scale-wrap"]/a[@target="_blank" and contains(@href,"www.bilibili.com/video/")]/@href')
    for url in normal_url_list:
        id = re.findall('(BV[0-9a-zA-Z]+)', url)[0]
        id_list.append([id, "BVid"])
    # id_list = list(set(id_list))
    bangumi_url_list = list(set(bangumi_url_list))
    normal_url_list = list(set(normal_url_list))
    id_list.sort(reverse=True)
    if len(id_list) != len(bangumi_url_list) + len(normal_url_list):
        print("检索页面id解析错误")
    # print(id_list)
    return id_list


# 函数功能：将info_list按照 番剧电影 番剧电影贴片 合集视频 分集视频 一般视频 嵌套合集的方式排序
# (0: 一般视频，1: 番剧电影，2:分集视频，3:合集视频，4:合集嵌套合分集视频（BV1wZyHYSEc5，BV17j28YqEv6），5:番剧电影贴片)
def sort_info_list(info_list):
    new_info_list = []
    for i in range(len(info_list)):
        if info_list[i][-1] == 1:  # 番剧电影
            new_info_list.append(info_list[i])
    for i in range(len(info_list)):
        if info_list[i][-1] == 5:  # 番剧电影贴片
            new_info_list.append(info_list[i])
    for i in range(len(info_list)):
        if info_list[i][-1] == 3:  # 合集视频
            new_info_list.append(info_list[i])
    for i in range(len(info_list)):
        if info_list[i][-1] == 2:  # 分集视频
            new_info_list.append(info_list[i])
    for i in range(len(info_list)):
        if info_list[i][-1] == 0:  # 一般视频
            new_info_list.append(info_list[i])
    for i in range(len(info_list)):
        if info_list[i][-1] == 4:  # 嵌套合集
            new_info_list.append(info_list[i])
    return new_info_list


def type_distinguish(res_text):
    tree = etree.HTML(res_text)
    identity_flag = "unknown"
    type_identify = tree.xpath(
        '//a[@target="_blank" and @href and @title and @class="title jumpable" and @data-v-f4470e68]')  # 合集视频才有
    if len(type_identify) != 0:  # 合集视频(一般合集，复杂合集)
        identity_flag = "set"
    else:
        type_identify = tree.xpath('//div[@title="视频选集" and @class="title" and @data-v-f4470e68]')  # 分集视频才有
        if len(type_identify) != 0:  # 分集视频
            identity_flag = "episode video"
        else:
            type_identify = tree.xpath(
                '//link[@rel="sitemap" and @type="application/xml" and @title="Sitemap" and @href]')  # 番剧电影或者贴片才有
            if len(type_identify) != 0:  # 番剧电影或者贴片
                identity_flag = "bangumi"
            else:  # 一般视频
                identity_flag = "ordinary video"
    return identity_flag


def get_ordinary_video_info(res_text):
    tree = etree.HTML(res_text)
    # 1)获取id BV号
    id = (tree.xpath('/html/head/meta[@itemprop="url" and @data-vue-meta="true" and @content]/@content')[0]).split("/")[
        -2]
    # 2)获取title
    try:
        title = tree.xpath('//h1[@class="video-title special-text-indent"]/@title')[0]
    except IndexError:
        print("normal_video_title_decode_error")
        title = "decode_error"
    # 3)identity_flag
    identity_flag = "ordinary video"
    # 4)合成info
    info = [id, title, identity_flag]
    # info格式 [ID号,标题,视频类型标签]
    return info


def get_bangumi_info(res_text, type):
    identity_flag = "bangumi"
    if type == "BVid" or type == "epid":
        tree = etree.HTML(res_text)
        # 1)获取id (ep号)
        id = (tree.xpath('/html/head/meta[@property="og:url" and @content]/@content')[0]).split("/")[-1]
        # 2)获取分集列表 再次区分类别
        sitemap_url = tree.xpath('/html/head/link[@rel="sitemap" and @title="Sitemap" and @href]/@href')[0]
        response = requests.get(sitemap_url, headers=bilibili_head)
        xml_tree = etree.XML(response.text.encode('utf-8'))
        episode_id_list = xml_tree.xpath('/season/episodeList/episode/playUrl/text()')
        for i in range(len(episode_id_list)):
            episode_id_list[i] = episode_id_list[i].split("/")[-1]
        for item in episode_id_list:
            if id == item:  # 单集番剧
                identity_flag = "single bangumi"
                break
            else:
                identity_flag = "bangumi append"
        # 3)获取title
        title = tree.xpath('/html/head/title/text()')[0]
        title = title.rstrip(" ,，番剧_-纪录片高清独家在线观看bilibili-哔哩")  # 删除标题中的附加部分
        info = [id, title, identity_flag]
        return info
    if type == "ssid":
        html_tree = etree.HTML(res_text)
        identity_flag = "bangumi set"
        sitemap_url = html_tree.xpath('/html/head/link[@rel="sitemap" and @title="Sitemap" and @href]/@href')[0]
        response = requests.get(sitemap_url, headers=bilibili_head)
        xml_tree = etree.XML(response.text.encode('utf-8'))
        set_id = sitemap_url.split("/")[-1][0:-4]
        title = html_tree.xpath('/html/head/meta[@property="og:title" and @content]/@content')[0]
        episode_id_list = xml_tree.xpath('/season/episodeList/episode/playUrl/text()')
        for i in range(len(episode_id_list)):
            episode_id_list[i] = episode_id_list[i].split("/")[-1]
        episode_title_list = xml_tree.xpath('/season/episodeList/episode/longTitle/text()')
        info = [set_id, title, episode_id_list, episode_title_list, identity_flag]
        return info


def get_episode_video_info(res_text):
    tree = etree.HTML(res_text)
    # 1)合集id即为当前id
    set_id = \
        (tree.xpath('/html/head/meta[@itemprop="url" and @data-vue-meta="true" and @content]/@content')[0]).split("/")[
            -2]
    # 2)获取合集title
    # 旧用javascript解析法
    # set_info = tree.xpath("/html/head/script[5]/text()")[0]
    # set_info = re.findall('window.__INITIAL_STATE__=(.*?);', set_info)[0]  # 用;匹配javascript末尾
    # set_info_dict = json.loads(set_info)
    # set_title = set_info_dict["videoData"]["title"]
    # 更新方法
    set_title = tree.xpath('//h1[@class="video-title special-text-indent"]/@title')[0]
    # 3)获取当前序号
    episode_info = tree.xpath('//div[@class="amt"]/text()')[0]
    episode_info = episode_info.strip("（）")
    episode_info = episode_info.split("/")
    now_episode = eval(episode_info[0])
    episode_num = eval(episode_info[1])
    # 4)获取每集id(从总集数)
    episode_id_list = list(range(1, episode_num + 1))
    # 5)获取每集标题
    episode_title_list = tree.xpath('//div[@class="title-txt"]/text()')
    episode_title_list = remove_index(episode_title_list)

    identity_flag = "episode video"
    # 6)合成info
    info = [set_id, set_title, episode_id_list, episode_title_list, identity_flag]
    # info格式 [ID号,标题，分集id列表[]，分集标题列表[]，视频类型标签]
    return info


def get_set_info(res_text):
    # identity_flag = "set"
    tree = etree.HTML(res_text)
    # info格式 [合集id，标题,分集列表section_list[section]，视频类型标签=complex set] set
    # section[]格式 [section_id,标题，atmo_list[atmo]，视频类型标签=ordinary set] sub_set
    # atmo[]格式 [ID号,标题，分集id列表[]，分集标题列表[]，视频类型标签=ordinary video或episode video] atom原子
    set_id = tree.xpath('//a[@class="title jumpable" and @target="_blank"]/@href')[0]  # 合集视频才有这个
    set_id = "https://" + set_id.split('&')[-2][2:]
    set_info = tree.xpath("/html/head/script[5]/text()")[0]
    set_info = re.findall('window.__INITIAL_STATE__=(.*?}});', set_info)[0]  # 用;匹配javascript末尾
    set_info_dict = json.loads(set_info)
    set_title = set_info_dict["videoData"]["ugc_season"]["title"]  # 总title
    set_identity_flag = "complex set"  # 嵌套
    # sections>episodes>pages
    section_list = []
    for i in range(len(set_info_dict["videoData"]["ugc_season"]["sections"])):
        section_title = set_info_dict["videoData"]["ugc_season"]["sections"][i]["title"]  # 分区title
        section_id = set_id
        section_identity_flag = "ordinary set"
        atmo_list = []
        for j in range(len(set_info_dict["videoData"]["ugc_season"]["sections"][i]["episodes"])):  # 最小视频本身
            if len(set_info_dict["videoData"]["ugc_season"]["sections"][i]["episodes"][j][
                       "pages"]) > 1:  # 一个BV号却有多个视频 嵌套分集视频
                atmo_identity_flag = "episode video"
            else:
                atmo_identity_flag = "ordinary video"
            atmo_id = set_info_dict["videoData"]["ugc_season"]["sections"][i]["episodes"][j]["bvid"]
            atmo_title = set_info_dict["videoData"]["ugc_season"]["sections"][i]["episodes"][j]["title"]
            atmo_num_of_episodes = len(
                set_info_dict["videoData"]["ugc_season"]["sections"][i]["episodes"][j]["pages"])
            atmo_episode_id_list = list(range(1, atmo_num_of_episodes + 1))
            atmo_episode_title_list = []
            for k in range(len(set_info_dict["videoData"]["ugc_season"]["sections"][i]["episodes"][j]["pages"])):
                episode_title = set_info_dict["videoData"]["ugc_season"]["sections"][i]["episodes"][j]["pages"][k][
                    "part"]
                atmo_episode_title_list.append(episode_title)

            if atmo_identity_flag == "episode video":
                atmo = [atmo_id, atmo_title, atmo_episode_id_list, atmo_episode_title_list, atmo_identity_flag]
                # atmo[]格式 [ID号,标题，分集id列表[]，分集标题列表[]，视频类型标签=episode video] atom原子
            elif atmo_identity_flag == "ordinary video":
                atmo = [atmo_id, atmo_title, atmo_identity_flag]
                # atmo[]格式 [ID号,标题,视频类型标签=ordinary video] atom原子
            else:
                return
            atmo_list.append(atmo)
        section = [section_id, section_title, atmo_list, section_identity_flag]
        # section[]格式 [section_id,标题，atmo_list[atmo]，视频类型标签=ordinary set]
        section_list.append(section)
    if len(section_list) == 1:
        set_identity_flag = "ordinary set"
        # 合成info
        info = [set_id, set_title, section_list[0][2], set_identity_flag]
        # info格式 [合集id,标题，atmo_list，视频类型标签=ordinary set]
    else:
        set_identity_flag = "complex set"
        # 合成info
        info = [set_id, set_title, section_list, set_identity_flag]
        # # 展开复杂合集info
        # info = complex_set_unfold(info)
        # info格式 [合集id，标题,分集列表section_list[section]，视频类型标签=complex set]
        # section[]格式 [section_id,标题，atmo_list[atmo]，视频类型标签=ordinary set]
    return info


def complex_set_unfold(complex_set_info):
    # 将complex_video_set展开成普通合集
    # 合集视频info格式 [合集标题，atmo_list[]，视频类型标签=3]
    # 一般视频与分集视频info格式 [ID号,标题，分集id列表[]，分集标题列表[]，视频类型标签]
    title = complex_set_info[1]
    atmo_list = []
    for i in range(len(complex_set_info[2])):
        atmo_list += complex_set_info[2][i][1]
    identity_flag = "ordinary set"
    info = [title, atmo_list, identity_flag]
    return info


# 展示info_list
# info_list格式 [标题,分集列表section_list[section]，视频类型标签=4] set
# section[]格式 [标题，atmo_list[atmo]，视频类型标签=3] sub_set
# atmo[]格式 [ID号,标题，分集id列表[]，分集标题列表[]，视频类型标签=0或2] atom原子
# 番剧电影info_list格式 [ID号,标题，分集id列表[]，分集标题列表[]，视频类型标签]
# (0: 一般视频，1: 番剧电影，2:分集视频，3:合集视频，4:合集嵌套合集)
def display_info_list(info_list):
    info_list = sort_info_list(info_list)
    index = 1
    for info in info_list:
        if info[-1] == 1:  # 番剧电影
            tag = "(番剧电影)"
            episode = "(共" + str(len(info[2])) + "集)"
            print("\t" + str(index) + "." + tag + episode + info[1])
            index += 1
        if info[-1] == "bangume append":  # 番剧电影贴片
            tag = "(番剧电影贴片)"
            episode = ""
            print("\t" + str(index) + "." + tag + episode + info[1])
            index += 1
        if info[-1] == "ordinary set":  # 合集视频
            tag = "(合集视频)"
            episode = "(共" + str(len(info[1])) + "集)"
            print("\t" + str(index) + "." + tag + episode + info[0])
            index += 1
        if info[-1] == "episode video":  # 分集视频
            tag = "(分集视频)"
            episode = "(共" + str(len(info[2])) + "集)"
            print("\t" + str(index) + "." + tag + episode + info[1])
            index += 1
        if info[-1] == "ordinary video":  # 一般视频
            tag = "(一般视频)"
            episode = ""
            print("\t" + str(index) + "." + tag + episode + info[1])
            index += 1
        if info[-1] == "complex set":  # 嵌套合集
            print("合集标题：" + info[1])
            for i in range(len(info[2])):
                print("\t分合集标题:" + info[2][i][0])
                for j in range(len(info[2][i][1])):
                    index = j + 1
                    if info[2][i][1][j][4] == 2:
                        tag = "(分集视频)"
                        episode = "共" + str(len(info[2][i][1][j][2])) + "集"
                    else:
                        tag = "(一般视频)"
                        episode = ""
                    print("\t\t" + str(index) + "." + tag + info[2][i][1][j][1] + episode)
import requests
from core import *

# import re
#

head = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0",
    "Referer": "https://www.bilibili.com/",
    "Cookie": "CURRENT_FNVAL=4048; buvid3=BE2D386A-BBCB-E06E-8C2B-F5223B4C8BC517591infoc; b_nut=1721567317; _uuid=67165DF10-7B77-BDE8-3C63-732C2FCAF4D520375infoc; enable_web_push=DISABLE; buvid4=0245F01B-6C4B-CD5A-2EC5-BC060EC0777D18433-024072113-zRTpkL0r94scQqxGfSYKhQ%3D%3D; home_feed_column=5; header_theme_version=CLOSE; rpdid=|(Y|RJRR)Y~0J'u~kulY~Rkk; DedeUserID=1611307689; DedeUserID__ckMd5=b0865dba0b3ced5b; buvid_fp_plain=undefined; is-2022-channel=1; b_lsid=D8542F24_191412D93C0; bsource=search_bing; bmg_af_switch=1; bmg_src_def_domain=i1.hdslb.com; browser_resolution=1659-943; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MjM2MzQ1OTMsImlhdCI6MTcyMzM3NTMzMywicGx0IjotMX0.Ox8rnEpQH5i1H_wQfH2z5CzZC0y8PlqQCy1KVa8XEfQ; bili_ticket_expires=1723634533; SESSDATA=f567fef6%2C1738927393%2C5d207%2A82CjAh2pSUKwDLr1XiI6ncU5B6NXEfWKS7ES6mDC8yGxM6aT3-BTdvK0KAlYpMhCXtEXgSVkl2aTlQWUNacTZOZ0ZNXzJwZ21QT2ozMXFXcWtFc1FpNnBIWlNWbml2Y3BxNV80bUNMZTBVN1dyb3h0STU1ZklDM0MwckJvanRmTmNkeTBFcW5qYl9RIIEC; bili_jct=8d788bcb503d69ba2ded7dfbb53f6e58; sid=71po5kkf; fingerprint=0c7279b7c69b9542a76b8d9df9b7872a; buvid_fp=BE2D386A-BBCB-E06E-8C2B-F5223B4C8BC517591infoc; bp_t_offset_1611307689=964382000909647872"
}

keyword = "东方"
# target_url = "https://search.bilibili.com/all?keyword="+keyword+"&page="+page_num
# target_url = "https://search.bilibili.com/all?keyword=" + keyword
# target_url = "https://www.bilibili.com/video/BV1jS4y1L7oW"
# target_url="https://www.bilibili.com/video/BV1c34y137Z9/"
# # target_url = "https://www.bilibili.com/video/BV13u4y1w7Cm"
# response = requests.get(target_url, headers=head)
# res_text = response.text
# print("获取html文件")
# 合集视频，分集视频处理
# 东方合集 不分集 分集
# video_id_list = ["BV1c34y137Z9", "BV13u4y1w7Cm", "BV1ss41117Z8"]
# for i in range(len(video_id_list)):
#     target_url = "https://www.bilibili.com/video/" + video_id_list[i]
#     video_response = requests.get(target_url, headers=head)
#     with open(video_id_list[i] + ".html", "w", encoding="utf-8") as f:
#         f.write(video_response.text)
video_id_list = ["BV1c34y137Z9", "BV13u4y1w7Cm", "BV1ss41117Z8"]
video_episode_num_list = []
for i in range(len(video_id_list)):
    video_identity_flag = 0  # 0：一般不分集不合集视频 1:分集视频 2:合集视频
    index = 1
    episode_num = 1
    target_url = "https://www.bilibili.com/video/" + video_id_list[i]
    video_response = requests.get(target_url, headers=head)

    video_episode_info_list = re.findall(
        "<div title=\"视频选集\" class=\"title\" data-v-f4470e68>视频选集</div> <div class=\"amt\" data-v-f4470e68>（\d*?/\d*?）</div>",
        video_response.text)
    if len(video_episode_info_list) == 0:
        video_episode_info_list = re.findall("<div class=\"amt\" data-v-f4470e68>（\d*?/\d*?）</div>",
                                             video_response.text)
        if len(video_episode_info_list) == 0:
            video_identity_flag = 0  # 一般不分集不合集视频
        else:
            video_identity_flag = 2  # 合集视频
    else:
        video_identity_flag = 1  # 分集视频

    if video_identity_flag == 1 or video_identity_flag == 2:
        if len(video_episode_info_list) == 1:
            temp_episode_index = re.findall("（\d*?/", video_episode_info_list[0])
            index = temp_episode_index[0][1:-1]
            temp_episode_num = re.findall("/\d*?）", video_episode_info_list[0])
            episode_num = temp_episode_num[0][1:-1]
            if video_identity_flag == 1:
                print(video_id_list[i] + "为分集视频，该系列共" + str(episode_num) + "集")
            if video_identity_flag == 2:
                print(video_id_list[i] + "为合集视频，这一集为该合集中的第" + str(index) + "集，该系列共" + str(episode_num) + "集")
        else:
            print("集数解析错误")
    else:
        print(video_id_list[i] + "为不分集视频")
print(video_episode_num_list)

# animation_and_film_temp_list = re.findall(
#     '<a title=\".*?\" class=\"text_ellipsis\" href=\"https://www.bilibili.com/bangumi/play/.*?\" target=\"_blank\"',
#     response.text)
# episode_num_list = re.findall('</span></span><span data-v-384b5d39>全(\d*)话</span></div>', response.text)
# # print(episode_num_list)
# # print(animation_and_film_temp_list)
# for item in animation_and_film_temp_list:
#     animation_and_film_title_list += re.findall("title=\".*?\"", item)
#     animation_and_film_ss_id_list += re.findall("href=\"https://www.bilibili.com/bangumi/play/.*?\"", item)
# for i in range(len(animation_and_film_title_list)):
#     animation_and_film_title_list[i] = animation_and_film_title_list[i][7:-1]
#     animation_and_film_title_list[i] = animation_and_film_title_list[i].replace("&amp;quot;",
#                                                                                 "\"")  # 将&amp;quot;换为"\""
# for i in range(len(animation_and_film_ss_id_list)):
#     animation_and_film_ss_id_list[i] = animation_and_film_ss_id_list[i][44:-1]
# for i in range(len(episode_num_list)):
#     episode_num_list[i] = int(episode_num_list[i])
# print(animation_and_film_title_list)
# print(animation_and_film_ss_id_list)


# core_function("https://www.bilibili.com/bangumi/play/ep827835?spm_id_from=333.337.0.0&from_spmid=666.25.episode.0",-3)
#
# animation_and_film_temp_list = re.find  all(
#     '<a title=\".*?\" class=\"text_ellipsis\" href=\"https://www.bilibili.com/bangumi/play/.*?\" target=\"_blank\"',
#     response.text)
# print(animation_and_film_temp_list)
#
# episode_num_list = []
# animation_and_film_id_list = []
# animation_and_film_title_list = []
#
# for item in animation_and_film_temp_list:
#     animation_and_film_title_list += re.findall("title=\".*?\"", item)
#     animation_and_film_id_list += re.findall("href=\"https://www.bilibili.com/bangumi/play/.*?\"", item)
# for i in range(len(animation_and_film_title_list)):
#     animation_and_film_title_list[i] = animation_and_film_title_list[i][7:-1]
#     animation_and_film_title_list[i] = animation_and_film_title_list[i].replace("&amp;quot;", "\"")
# for i in range(len(animation_and_film_id_list)):
#     animation_and_film_id_list[i] = animation_and_film_id_list[i][44:-1]
# episode_num_list = re.findall('</span></span><span data-v-384b5d39>全(\d*)话</span></div>', response.text)
#
# print(episode_num_list)
# print(animation_and_film_title_list)
# print(animation_and_film_id_list)
# animation_and_film_dict = {}
# # 格式 ss/ep号"[标题，集数]
# for i in range(len(episode_num_list)):
#     animation_and_film_dict[animation_and_film_id_list[i]] = [animation_and_film_title_list[i], episode_num_list[i]]
# print(animation_and_film_dict)


# title_list_temp = re.findall(
#     'href=\"//www.bilibili.com/video/.*?/.*?class=\"bili-video-card__info--tit\" title=\"(.*?)\"', response.text)
# print(url_list_temp)
# print(title_list_temp)
# for i in range(len(url_list_temp)):
#     url_list_temp[i] = re.findall("www.bilibili.com/video/.*?/", url_list_temp[i])[0]
# print(url_list_temp)
# # url_list_temp = re.findall('href=\"//www.*?\"', response.text)
# # title_list_temp = re.findall("class=\"bili-video-card__info--tit\" title=\"(.*?)\"", response.text)
# # print(url_list_temp)
# # print(title_list_temp)
#
# for title_id in range(len(title_list_temp)):
#     title_list_temp[title_id] = title_list_temp[title_id].replace("&amp;quot;", "\"")
# print(title_list_temp)
# <img src="//i2.hdslb.com/bfs/archive/1cec928877afe8dcb12bdb2f70ab37743726640c.jpg@672w_378h_1c_!web-search-common-cover"封面

# if __name__ == '__main__':
#     title_list=["东方星莲船 Lunatic 灵梦A NMNBNV","【东方组曲】东方星莲船组曲"]
#     for title in title_list:
#         title=title.replace("Lunatic","\"")
#         print(title)
#     print(title_list)

# title_list = ["东方星莲船 Lunatic 灵梦A NMNBNV", "【东方组曲】东方星莲船组曲"]
# for i in range(len(title_list)):
#     title_list[i] = "pocessed" + title_list[i]
# print(title_list)
# default_number_of_videos=10
# selected_id_list = list(range(1,default_number_of_videos+1))
# print(selected_id_list)


# # print(list(range(1,10)))
# url="https://www.bilibili.com/bangumi/play/ep827835?"
# print(re.findall("/(EP|Ep|eP|ep)(([A-Z]|[a-z]|[0-9])+)", url))
# id = "ep" + re.findall("/(EP|Ep|eP|ep)(([A-Z]|[a-z]|[0-9])+)", url)[0][1]
# print(id)
# iter_list=list(range(10))
# print(iter_list)
# iter_list.pop(1)
#
# print(iter_list)

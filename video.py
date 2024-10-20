from json import JSONDecodeError
from time import sleep

import requests
from lxml import etree
import json
from bs4 import BeautifulSoup
from moviepy.editor import *
from interface import *
from user_config import *

def keywords_to_url(keyword, app_type, select_enable):
    global to_select_num
    in_func_url_list = []  # 添加in_func_前缀以区分
    in_func_title_list = []
    if app_type == "bilibili":
        # 获取搜索页面html，预处理得到原始list
        search_url = "https://search.bilibili.com/all?keyword=" + keyword  # 转化为搜索页面网址
        response = requests.get(search_url, headers=head)
        url_list_temp = re.findall('href=\"//www.*?\"', response.text)
        title_list_temp = re.findall('alt=\"(.*?)\"', response.text)
        # print(response.text)
        # print(title_list_temp)
        # print(url_list_temp)

        # list处理
        # url_list_temp处理
        url_list_temp.pop(-1)  # 最后一个是'https://www.bilibili.com/v/customer-service'
        for j in range(0, len(url_list_temp)):  # 去除重复项
            if j % 2 == 0:
                url_list_temp[j] = "https://" + url_list_temp[j][8:-1]
            else:
                url_list_temp[j] = ""
        for url_item in url_list_temp:
            if url_item == "":
                url_list_temp.remove(url_item)
        # title_list_temp处理
        for title in title_list_temp:
            if title == "":
                title_list_temp.remove(title)  # 删除空项
        title_list_temp.pop(0)  # 第一项好像无法通过上面的检查空项的方法删除

        # print(title_list_temp)
        # print(url_list_temp)

        if select_enable == 0:  # 不交互，默认截取list中需要的前几项
            in_func_url_list = url_list_temp[0:default_number_of_videos]
            in_func_title_list = title_list_temp[0:default_number_of_videos]
            print("关键词检索，非交互模式，以下是默认选择的项目:")
            for i in range(1, len(in_func_title_list) + 1):
                title = in_func_title_list[i - 1]
                print(str(i) + "." + title)
        else:  # 交互模式
            selected_id_list = []
            if to_select_num != -1:
                url_list_temp = url_list_temp[0:to_select_num]
                title_list_temp = title_list_temp[0:to_select_num]
            print("关键词检索，交互模式，以下是可供选择的项目:")

            for i in range(1, len(title_list_temp) + 1):
                title = title_list_temp[i - 1]
                print(str(i) + "." + title)
            select_result = eval(input("请输入您选择的视频序号,输入0退出选择:"))
            while select_result != 0:
                selected_id_list.append(select_result)
                select_result = eval(input("请输入您选择的视频序号,输入0退出选择:"))
            print("退出交互模式\n\n")
            sleep(1)
            for selected_id in selected_id_list:
                in_func_url_list.append(url_list_temp[selected_id - 1])
                in_func_title_list.append(title_list_temp[selected_id - 1])

            print("您选择的项目标题为:")
            for title in in_func_title_list:
                print(title)
            sleep(2)
    return in_func_url_list


def from_set_url_get_epi_url_list(set_url, num_of_episode):
    # 获取BV号
    in_func_list = []
    # 分集总url样例"https://www.bilibili.com/video/BV1ss41117Z8/?spm_id_from=333.337.search-card.all.click&vd_source=61265f50c4aea555795addd1d882df45"
    # 分url样例"https://www.bilibili.com/video/BV1ss41117Z8/?p=3"
    BVID = "BV" + str(re.findall("/BV(.*?)/", set_url)[0])
    for i in range(1, num_of_episode + 1):
        episode_url = "https://www.bilibili.com/video/" + BVID + "/?p=" + str(i)
        in_func_list.append(episode_url)
    print(in_func_list)
    return in_func_list


# mode == -1:全流程(整个完整视频) -2:获取音频 -3:获取html -4:获取画面
def get_video_and_html(target_url, mode):
    # 一、请求返回html的txt
    response = requests.get(target_url, headers=head)
    res_text = response.text
    soup = BeautifulSoup(res_text, 'lxml')

    if mode == -3:
        print("获取html文件")
        with open(target_url + ".html", "w", encoding="utf-8") as f:
            f.write(res_text)

    # 二、解析html文件
    # 1.获取标题(修正标题以避免误识别成文件路径，防止标题过长导致文件输出出错)
    title = soup.title.string
    title = str(title)
    title_list = list(title)
    for i in range(len(title_list)):  # 将“/”转换为“｜”防止打开文件时报错
        if title_list[i - 1] == "/":
            title_list[i - 1] = "|"
    title = "".join(title_list)
    print("视频名称：" + title)
    if len(title) > 100:
        title = title[:100]

    # 2.需要获取画面或音频文件时，解析html中的资源URL
    if mode == -1 or mode == -2 or mode == -4:  # 全视频，音频，画面
        # 数据解析
        tree = etree.HTML(res_text)
        try:
            base_info = "".join(tree.xpath("/html/head/script[4]/text()"))[20:]
            # print(base_info)
            info_dict = json.loads(base_info)
            print("html解码方式一(try)")
            video_url = info_dict["data"]["dash"]['video'][0]["baseUrl"]
            audio_url = info_dict["data"]["dash"]['audio'][0]["baseUrl"]
        except JSONDecodeError:
            # 目前大会员视频无法获得，但是画质可以获得
            base_info = "".join(tree.xpath("/html/head/script[4]/text()"))
            base_info = str(base_info)
            base_info = re.findall("const\splayurlSSRData\s=\s.*?}}}}", base_info)[0]
            base_info = base_info[23:]
            # print(base_info)
            info_dict = json.loads(base_info)
            # print(info_dict)
            print("html解码方式二(except)")
            video_url = info_dict["result"]["video_info"]["dash"]["video"][0]["baseUrl"]
            audio_url = info_dict["result"]["video_info"]["dash"]['audio'][0]["baseUrl"]

        if mode == -1 or mode == -4:  # 全视频或画面
            video_content = requests.get(video_url, headers=head).content
            # print(video_url)
            with open("video_file/" + title + "_video.mp4", "wb") as f:
                f.write(video_content)
                f.close()
                if mode == -1:
                    print("获取整个视频，画面已获取成功")
                else:
                    print("仅获取画面，画面获取成功")

        if mode == -1 or mode == -2:  # 全视频或音频
            audio_content = requests.get(audio_url, headers=head).content
            # print(audio_url)
            with open("audio_file/" + title + "_audio.wav", "wb+") as fp:
                fp.write(audio_content)
                fp.close()
                if mode == -1:
                    print("获取整个视频，音频已获取成功")
                else:
                    print("仅获取音频，音频获取成功")

        if mode == -1:
            print("音频与画面获取结束，音画合并中\n")
            video_path = "video_file/" + title + "_video.mp4"
            audio_path = "audio_file/" + title + "_audio.wav"
            video = VideoFileClip(video_path, audio=False)
            audio = AudioFileClip(audio_path)
            video = video.set_audio(audio)
            video.write_videofile("video_result/" + title + ".mp4")

# end_of_get_video

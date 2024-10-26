from json import JSONDecodeError
from lxml import etree
import json
from bs4 import BeautifulSoup
from moviepy.editor import *

from interface import *
from user_config import *


# mode == -1:全流程(整个完整视频) -2:获取音频 -3:获取html -4:获取画面
# video:内核标准格式
# [[视频id(BV AV与SS EP),选择集数列表[], 总集数，视频标题，视频类型标签(0: 一般视频，1: 番剧电影),模式],...]

# 函数输入:video格式变量(列表类型):[视频id(BV AV与SS EP),选择集数列表[], 总集数，视频标题，视频类型标签(0: 一般视频，1: 番剧电影,2:分集视频，3:合集视频),模式]
# 函数输出:无
def set_unfold_and_commit_to_core(video):
    id = video[0]
    info = video[1:]
    error_code = ""
    # print(video)
    if info[-2] == 0 or info[-2] == 2:  # 一般视频与分集视频
        target_url = "https://www.bilibili.com/video/" + id
        mode = info[-1]
        for episode in info[0]:
            episode_url = "https://www.bilibili.com/video/" + id + "?p=" + str(episode)
            core_function(episode_url, mode)
    elif info[-2] == 1:  # 番剧电影
        mode = info[-1]
        for episode_id in info[0]:
            episode_url = "https://www.bilibili.com/bangumi/play/" + episode_id
            core_function(episode_url, mode)
    else:  # 合集视频 collection
        mode = info[-1]
        for collection_item_id in info[0]:
            episode_url = "https://www.bilibili.com/video/" + collection_item_id
            core_function(episode_url, mode)


def core_function(url, mode):
    fail_flag = 0
    # 一、请求返回html的txt
    response = requests.get(url, headers=head)
    res_text = response.text
    soup = BeautifulSoup(res_text, 'lxml')
    with open("test.html", "w") as f:
        f.write(response.text)
        f.close()

    # 二、解析html文件
    # 1.获取标题(修正标题以避免误识别成文件路径，防止标题过长导致文件输出出错)
    title = soup.title.string
    title = str(title)
    # 从html中获取的视频名称示例：【东方编曲集】感情的摩天楼　～ Cosmic Mind_哔哩哔哩_bilibili
    title_list = list(title)
    for i in range(len(title_list)):  # 将“/”转换为“｜”防止打开文件时报错
        if title_list[i] == "/":
            title_list[i] = "|"
    title_list = title_list[0:-14]  # 删去最后的"_哔哩哔哩_bilibili"
    title = "".join(title_list)
    print("视频名称：" + title)
    if len(title) > 100:
        title = title[:100]

    # 2.需要获取html,画面或音频文件时,解析html中的资源URL
    if mode == -3:
        print("获取html文件")
        with open("html_file/" + title + ".html", "w", encoding="utf-8") as f:
            f.write(res_text)

    if mode == -1 or mode == -2 or mode == -4:  # 全视频，音频，画面
        # 数据解析
        video_url = ""
        audio_url = ""
        error_code = "null"
        tree = etree.HTML(res_text)
        try:
            base_info = "".join(tree.xpath("/html/head/script[4]/text()"))[20:]
            # print(base_info)
            info_dict = json.loads(base_info)
            # print("html解码方式一(try)")
            print("该视频为普通视频")
            video_url = info_dict["data"]["dash"]['video'][0]["baseUrl"]
            audio_url = info_dict["data"]["dash"]['audio'][0]["baseUrl"]
        except (JSONDecodeError, IndexError, KeyError):
            try:
                # 目前大会员视频无法获得，但是画质可以获得(?)
                base_info = "".join(tree.xpath("/html/head/script[4]/text()"))
                base_info = str(base_info)
                base_info = re.findall("const\splayurlSSRData\s=\s.*?}}}}", base_info)[0]
                base_info = base_info[23:]
                # print(base_info)
                info_dict = json.loads(base_info)
                # print(info_dict)
                # print("html解码方式二(except)")
                print("该视频为(免费/限免)番剧电影")
                video_index = 0
                audio_index = 0
                video_size = 0
                audio_size = 0
                for i in range(len(info_dict["result"]["video_info"]["dash"]["video"])):
                    if info_dict["result"]["video_info"]["dash"]["video"][i]["size"] > video_size:
                        video_size = info_dict["result"]["video_info"]["dash"]["video"][i]["size"]
                        video_index = i
                for i in range(len(info_dict["result"]["video_info"]["dash"]["audio"])):
                    if info_dict["result"]["video_info"]["dash"]['audio'][i]["size"] > audio_size:
                        audio_size = info_dict["result"]["video_info"]["dash"]['audio'][i]["size"]
                        audio_index = i
                video_url = info_dict["result"]["video_info"]["dash"]["video"][video_index]["baseUrl"]
                audio_url = info_dict["result"]["video_info"]["dash"]['audio'][audio_index]["baseUrl"]
            except (JSONDecodeError, IndexError, KeyError):
                try:
                    base_info = "".join(tree.xpath("/html/head/script[4]/text()"))
                    base_info = str(base_info)
                    base_info = re.findall("const\splayurlSSRData\s=\s.*?}}}}}", base_info)[0]
                    base_info = base_info[23:]
                    info_dict = json.loads(base_info)
                    print("该视频为大会员番剧电影，暂无法获取完整版本，获取预览版本")
                    video_url = info_dict["result"]["video_info"]["durls"][0]["durl"][0]["url"]
                    error_code = "not_vip"
                except (JSONDecodeError, IndexError, KeyError):
                    print("该视频返回的html暂时无法解析，已保存\"" + title + ".html\"文件")
                    with open("html_file/" + "html_decode_error_" + title + ".html", "w", encoding="utf-8") as f:
                        f.write(res_text)
                    video_url = ""
                    audio_url = ""
                    error_code = "html_decode_error"
                    print("造成此结果的原因可能是 1.视频为充电粉丝专享 2.网络问题 3.访问的视频不存在")
        if error_code == "null":
            video_path = "video_file/" + title + video_file_type  # 画面文件路径
            audio_path = "audio_file/" + title + audio_file_type  # 音频文件路径
            video_result_path = "video_result/" + title + video_file_type  # 完整视频文件路径
            if mode == -1 or mode == -4:  # 全视频或画面
                try:
                    video_content = requests.get(video_url, headers=head).content
                    with open(video_path, "wb") as f:
                        f.write(video_content)
                        f.close()
                    if mode == -1:
                        print("获取整个视频，画面已获取成功")
                    else:
                        print("仅获取画面，画面获取成功")
                except requests.exceptions.ChunkedEncodingError:
                    print("网络连接不稳定，获取失败")
                    return
            if mode == -1 or mode == -2:  # 全视频或音频
                try:
                    audio_content = requests.get(audio_url, headers=head).content
                    with open(audio_path, "wb+") as fp:
                        fp.write(audio_content)
                        fp.close()
                    if mode == -1:
                        print("获取整个视频，音频已获取成功")
                    else:
                        print("仅获取音频，音频获取成功")
                except requests.exceptions.ChunkedEncodingError:
                    print("网络连接不稳定，获取失败")
                    return

            if mode == -1:
                print("音频与画面获取结束，音画合并中\n")
                video = VideoFileClip(video_path, audio=False)
                audio = AudioFileClip(audio_path)
                video = video.set_audio(audio)
                video.write_videofile(video_result_path, audio_codec="aac")
        if error_code == "not_vip":
            video_content = requests.get(video_url, headers=head).content
            with open("video_result/" + title + video_file_type, "wb+") as f:
                f.write(video_content)
                f.close()
    if mode == -5:
        pass  # 自定义程序
    print("\n")
# end_of_get_video

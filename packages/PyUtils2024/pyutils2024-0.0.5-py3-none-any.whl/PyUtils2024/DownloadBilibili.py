import json
import os
import re

import requests
from lxml import etree

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    'referer': 'https://www.bilibili.com/'
}



def downloadVideoAudio(dir_name,file_name,url):
    # 获取页面源码
    page_source = requests.get(url, headers=headers).text
    html = etree.HTML(page_source)
    # 解析出标题
    # title = html.xpath('//*[@id="viewbox_report"]/h1/text()')[0]
    # 使用正则表达式匹配出视频数据JSON，并解析出视频地址和声音地址
    json_text = re.findall('window.__playinfo__=(.*?)</script>', page_source)[0]
    data = json.loads(json_text)
    print(data)
    video_url = data['data']['dash']['video'][0]['baseUrl']
    audio_url = data['data']['dash']['audio'][0]['baseUrl']
    print(video_url)
    print(audio_url)
    #     下载视频和声音
    if not os.path.exists(f'./videos/{dir_name}/'):
        os.makedirs(f'./videos/{dir_name}/')
    print(f"正在下载视频{file_name}")
    content = requests.get(video_url, headers=headers).content
    video_file=f"./videos/{file_name}.mp4"
    with open(video_file, "wb") as f:
        f.write(content)
    print(f"正在下载音频{file_name}")
    content = requests.get(audio_url, headers=headers).content
    audio_file=f"./videos/{file_name}.mp3"
    with open(audio_file, "wb") as f:
        f.write(content)
    out_video_file=f"./videos/{dir_name}/{file_name}.mp4"
    mergeVideoAndAudio(video_file,audio_file,out_video_file)
    #删除下载的音频和视频文件
    os.remove(video_file)
    os.remove(audio_file)
def mergeVideoAndAudio(video,audio,out_video):
    print(f"ffmpeg -i {video} -i {audio} {out_video}")
    os.system(f'ffmpeg -i "{video}" -i "{audio}" "{out_video}"')

def downloadBiliBili(dir_name,url):

    page_source = requests.get(url, headers=headers).text
    json_text = re.findall('window.__INITIAL_STATE__=(.*?);\(function\(\)', page_source)[0]
    pages=json.loads(json_text)["videoData"]["pages"]
    print(json_text)
    for i in range(1,len(pages)):
        file_name = pages[i-1]['part']
        downloadVideoAudio(dir_name,file_name,f"{url}?p={i}")

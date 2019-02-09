#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
import zipfile
import subprocess
from urllib import request, parse
from time import strftime, localtime

target_version = "3.2.3"
language = "zh"
cwd = sys.path[0]
src = f"{cwd + os.sep}src{os.sep}"
dist = f"{cwd + os.sep}dist{os.sep}"
ini = f"{dist}package.ini"
translated = re.compile(r"(?:Generated\s)(\d+)(?: translation)")
untranslated = re.compile(r"(?:Ignored\s)(\d+)(?: untranslated)")


def make_release():
    if os.name == 'nt':
        lrelease = 'C:/Qt/Qt5.6.3/5.6.3/msvc2015_64/bin/lrelease.exe'  # On my laptop.
    else:
        # os.name == 'posix'
        lrelease = 'lrelease'
    # source_file = [f[:-3] for f in os.listdir(src) if os.path.isfile(os.path.join(src, f)) and f[-5:-3] == language]
    source_file = [f[:-3] for f in os.listdir(src) if f[-5:-3] == language]
    if len(source_file) == 0:
        print("Input file not found. Exit.")
    release_file = []
    translated_count = 0
    total_count = 0
    if not os.path.exists(dist):
        print("Warning: \"dist\" folder not found. Creating folder...\n")
        os.makedirs(dist)

    for i in source_file:
        print(i)
        result = subprocess.run([lrelease, f'{src+i}.ts', '-qm', f'{dist+i}.qm'],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            result_info = result.stdout.decode("utf-8")
        except UnicodeDecodeError:
            result_info = result.stdout.decode("gbk")  # 中文系统可能会遇到编码问题
        print(result_info)
        if result.returncode == 0:
            release_file.append(f"{i}.qm")
            if i != "qt_zh":
                translated_count += int(translated.findall(result_info)[0])
                total_count += int(translated.findall(result_info)[0])
                untranslated_count = untranslated.findall(result_info)
                total_count += int(untranslated_count[0]) if len(untranslated_count) != 0 else 0
        else:
            try:
                print(result.stderr.decode("utf-8"))
            except UnicodeDecodeError:
                print(result.stderr.decode("gbk"))  # 中文系统可能会遇到编码问题

        # except subprocess.CalledProcessError as err:
        #    print("lrelease error:")
        #    print(err)'''
    send_progress(translated_count, total_count)
    return release_file


def send_progress(done, total):
    percentage = round(done*100/total, 2)
    output = f"当前进度:\n{done}/{total}\n{percentage}%\n"
    print(output)
    try:
        assert 0 == telegram_push(output)
        print("推送成功\n")
    except AssertionError:
        print("推送被取消\n")
    except Exception as err:
        print(f"发生错误，推送失败\n错误信息：{err}\n")


def telegram_push(string):
    querystring = parse.urlencode({"text": string.encode('utf-8')})
    tg_api = os.getenv('TG_API')
    group_id = os.getenv('TG_GROUP_ID')
    if tg_api == "" or group_id == "":
        print("未检测到Telegram Api Key或Group ID")
        print("需要在环境变量中设置api key和Group ID")
        return 1
    url = f"https://api.telegram.org/bot{tg_api}/sendMessage?chat_id={group_id}&"
    request.urlopen(url + querystring)
    return 0


def make_package(release_list):
    timestamp = strftime("%Y%m%d%H%M%S", localtime())
    print("Write package info to package.ini ...")
    with open(ini, "w", encoding="utf-8") as f:
        package_info = [f"Name = TeamSpeak 3 简体中文汉化包 软件版本:{target_version}",
                        "Type = Translation",
                        "Author = 寂听 & EdisonJwa",
                        f"Version = {timestamp}",
                        "Platforms = ",
                        'Description = 源代码: https://github.com/jitingcn/TS3-Translation_zh-CN']
        f.write("\n".join(package_info))

    file_name = 'Chinese_Translation_zh-CN.ts3_translation'
    print("Zip package ...")
    with zipfile.ZipFile(file_name, 'w', zipfile.ZIP_DEFLATED) as release:
        release.write(ini, "package.ini")
        for i in release_list:
            release.write(dist+i, f"translations/{i}")
        print("构建成功")


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print("Making .qm translations file ...")
        release_file_list = make_release()
        print("Making .ts3_translation release package ...")
        make_package(release_file_list)
    else:
        if sys.argv[1] == "1":
            telegram_push("部署成功")

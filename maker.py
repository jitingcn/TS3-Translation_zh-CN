#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
import zipfile
import subprocess
from urllib import request, parse, error
from time import strftime, localtime

target_version = "3.5.3"
language = "zh"
cwd = sys.path[0]
src = f"{cwd + os.sep}src{os.sep}"
dist = f"{cwd + os.sep}dist{os.sep}"
ini = f"{dist}package.ini"


def make_release():
    if os.name == 'nt':
        lrelease = os.popen("where lrelease").read().strip()  # set in path.
    else:
        # os.name == 'posix'
        lrelease = os.popen("which lrelease").read().strip()
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

    translated = re.compile(r"(?:Generated\s)(\d+)(?: translation)")
    untranslated = re.compile(r"(?:Ignored\s)(\d+)(?: untranslated)")

    error = False

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
            error = True
            try:
                print(f"发生错误:\n{result.stderr.decode('utf-8')}")
                telegram_push(f"发生错误:\n{i}\n{result.stderr.decode('utf-8')}")
            except UnicodeDecodeError:
                print(f"发生错误:\n{result.stderr.decode('gbk')}")  # 中文系统可能会遇到编码问题
                telegram_push(f"发生错误:\n{i}\n{result.stderr.decode('gbk')}")

        # except subprocess.CalledProcessError as err:
        #    print("lrelease error:")
        #    print(err)'''
    if error:
        raise RuntimeError
    send_progress(translated_count, total_count)
    return release_file


def send_progress(done, total):
    percentage = round(done*100/total, 2)
    output = f"当前进度:\n{done}/{total}\n{percentage}%\n"
    print(output)
    try:
        assert 0 == telegram_push(output, 1)
        print("推送成功\n")
    except AssertionError:
        print("推送被取消\n")
    # except Exception as err:
    #    print(f"发生错误，推送失败\n错误信息：{err}\n")


def telegram_push(string, debug=0):
    if not string:
        if debug:
            print('No message to send.')
        return 1
    querystring = parse.urlencode({"text": string.encode('utf-8')})
    tg_api = os.getenv('TG_API')
    group_id = os.getenv('TG_GROUP_ID')
    if not tg_api or not group_id:
        if debug:
            print("Telegram api key or chat(group) id not found.")
            print("You need to set TG_API and TG_GROUP_ID in the environment variable.")
        return 1
    url = f"https://api.telegram.org/bot{tg_api}/sendMessage?chat_id={group_id}&"
    try:
        request.urlopen(url + querystring)
        return 0
    except error.URLError:
        if debug:
            print("Unable to connect to telegram server, skip message sending operation.")
        return 1


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
        print("语言包生成成功")


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print("Making .qm translations file ...")
        release_file_list = make_release()
        print("Making .ts3_translation release package ...")
        make_package(release_file_list)
    else:
        if sys.argv[1] == "1":
            telegram_push("构建成功")

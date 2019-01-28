#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import zipfile
import subprocess
from time import strftime, localtime

target_version = "3.2.3"
language = "zh"
cwd = sys.path[0]
src = f"{cwd + os.sep}src{os.sep}"
dist = f"{cwd + os.sep}dist{os.sep}"
ini = f"{dist}package.ini"


def make_release():
    if os.name == 'nt':
        lrelease = 'C:/Qt/Qt5.6.3/5.6.3/msvc2015_64/bin/lrelease.exe'  # On my laptop.
    else:  # os.name == 'posix'
        # result = subprocess.run(['whereis', 'lrelease', '-b'], stdout=subprocess.PIPE).stdout.decode("utf-8")
            lrelease = 'lrelease'
    # source_file = [f[:-3] for f in os.listdir(src) if os.path.isfile(os.path.join(src, f)) and f[-5:-3] == language]
    source_file = [f[:-3] for f in os.listdir(src) if f[-5:-3] == language]
    release_file = []
    for i in source_file:
        print(i)
        result = subprocess.run([lrelease, f'{src+i}.ts', '-qm', f'{dist+i}.qm'],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.stdout.decode("utf-8"))
        if result.returncode == 0:
            release_file.append(i+".qm")
        else:
            print(result.stderr.decode("utf-8"))

        #except subprocess.CalledProcessError as err:
        #    print("lrelease error:")
        #    print(err)'''

    return release_file


def make_package(release_list):
    timestamp = strftime("%Y%m%d%H%M%S", localtime())
    print("Write package info to package.ini ...")
    with open(ini, "w", encoding="utf-8") as f:
        package_info = [f"Name = TeamSpeak 3 简体中文汉化包 软件版本:{target_version}",
                        "Type = Translation",
                        "Author = 寂听",
                        f"Version = Beta-{timestamp}",
                        "Platforms = ",
                        'Description = Source Code: https://github.com/jitingcn/TS3-Translation_zh-CN']
        f.write("\n".join(package_info))

    file_name = 'Chinese_Translation_(zh-CN).ts3_translation'
    print("Zip package ...")
    with zipfile.ZipFile(file_name, 'w', zipfile.ZIP_DEFLATED) as release:
        release.write(ini, "package.ini")
        for i in release_list:
            release.write(dist+i, f"translations/{i}")
        print("Complete.")


if __name__ == '__main__':
    print("Making .qm translations file ...")
    release_file_list = make_release()
    print("Making .ts3_translation release package ...")
    make_package(release_file_list)

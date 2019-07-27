# TS3-Translation_zh-CN
TeamSpeak 3 简体中文翻译源文件

~~本项目目前处于早期阶段,大量字段未翻译~~
2806/4057
当前进度约 70%

[![HitCount](http://hits.dwyl.io/jitingcn/TS3-Translation_zh-CN/master.svg)](http://hits.dwyl.io/jitingcn/TS3-Translation_zh-CN/master)

## 协助翻译
使用 Qt Linguist 程序打开ts源文件即可

### 一些翻译上的约定（暂定）
1. 带快捷键的条目，如 `&Options` 需翻译为 `名称(快捷键)` 的形式，小括号，不带空格: `设置(&O)`
2. 描述性的条目含有括号时，翻译文本使用大括号。<br>
   例：`Manual (Define which items get synchronized)` 译为 `手动 （自定义同步的项目）`
3. 中英文混杂的条目，如英文单词字符数>4，需在单词两侧添加空格。<br>
   例：`Visit TeamSpeak &Webpage` 译为 `访问 TeamSpeak 网站(&W)`
4. `permissions.ts` 和 `ts_core_errors.ts` 为权限和错误代码的英文翻译。翻译权限和错误代码文本时，需要先打开 `xxx_zh.ts` ，然后打开 `xxx.ts` 为只读，进行对照。

## 使用方法
Windows： 前往release页面，下载后直接双击汉化包  `Chinese_Translation_zh-CN.ts3_translation` 即可，如果因为曾经装过旧版之类的问题导致关联程序有误，那么请使用TeamSpeak程序目录下的 `package_inst.exe` 来打开汉化包 `Chinese_Translation_zh-CN.ts3_translation` 。

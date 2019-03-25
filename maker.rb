#!/usr/bin/env ruby

require "zip"
require 'net/http'
require "open3"

Zip.setup do |c|
  c.on_exists_proc = true
  c.continue_on_exists_proc = true
  c.unicode_names = true
  c.default_compression = Zlib::BEST_COMPRESSION
  c.force_entry_names_encoding = 'UTF-8'
end

task = ARGV
build_version = ENV["TRAVIS_BUILD_NUMBER"]
log_url = ENV["TRAVIS_JOB_WEB_URL"]
#language = "zh"
pwd = Dir.pwd
Dir.mkdir("dist") unless Dir.exist?("dist")
package_name = "Chinese_Translation_zh-CN.ts3_translation"

def make_release()
  case RUBY_PLATFORM
    when /ix/i, /ux/i, /gnu/i, /bsd/i
      # "unix"
      lrelease = `which lrelease`.split[0]
    when /win/i, /ming/i
      # "windows"
      lrelease = 'C:/Qt/Qt5.6.3/5.6.3/msvc2015_64/bin/lrelease.exe'
    else
      # "other"
      quit()
  end
  translated_count = 0
  total_count = 0
  translated = /(?:Generated\s)(\d+)(?: translation)/.freeze
  untranslated = /(?:Ignored\s)(\d+)(?: untranslated)/.freeze
  Dir.glob("src/*_zh.ts") do |file|
    puts file
    output = "dist/#{file[4...-3]}.qm"
    stdin, stdout, stderr = Open3.popen3(lrelease, file, "-qm", output)
    index = 0
    stdout.each_line do |line| 
      unless /qt_zh/.match?(file)
        if index == 1
          translated_count += translated.match(line)[1].to_i
          total_count += translated.match(line)[1].to_i
        end
        if index == 2
          total_count += untranslated.match(line)[1].to_i
        end
      end
      puts line 
      index += 1
    end
    stdout.close
    unless stderr.nil?
      stderr.each_line { |line| puts line }
      stderr.close
    end
    puts ""  # new line
  end
  send_progress(translated_count, total_count)
end

def send_progress(done, total)
  percentage = Rational(done*100,total).round(2).to_f
  info =  "当前进度:\n#{done}/#{total}\n#{percentage}%\n".freeze
  puts info
  telegram_push(info)
end

def telegram_push(string)
  tg_api = ENV['TG_API']
  group_id = ENV['TG_GROUP_ID']
  uri = URI("https://api.telegram.org/bot#{tg_api}/sendMessage")
  querystring = {chat_id: group_id ,text: string}
  uri.query = URI.encode_www_form(querystring)
  res = Net::HTTP.get_response(uri)
  puts res.code
  # TODO: error handling
end

def make_package(zipfile_name, build_version=nil, log_url=nil)
  File.open('dist/package.ini', 'w') do |file|
    default_target_version = '3.2.3'
    package_info = [
      "Name = TeamSpeak 3 简体中文汉化包 目标软件版本: #{default_target_version}",
      "Type = Translation",
      "Author = 寂听 & EdisonJwa",
      "Version = travis-dev-build##{build_version}",
      "Platforms = ",
      "Description = 源代码: https://github.com/jitingcn/TS3-Translation_zh-CN" + 
      "    构建日志: #{log_url unless log_url.nil?}"]
    file.write(package_info.join("\n"))
  end
  Zip::File.open(zipfile_name, Zip::File::CREATE) do |zipfile|
    qm_files = Dir.glob("dist/*.qm")
    qm_files.each do |file|
      file = file.split("/")
      zipfile.add("translations/"+file[1], File.join(file))
    end
    zipfile.add("package.ini", File.join(["dist","package.ini"]))
  end
end

make_release()
make_package(package_name)

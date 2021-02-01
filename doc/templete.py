#!/usr/bin/python

"""
  以下所有模块都是python内置的标准模块，无需另外安装
  注意不同的python版本，函数的路径会有所差异，如：
  python2.7时，使用walk函数，from os.path import walk
  python3.8时，使用walk函数，from os import walk
  可通过pip安装ipython程序，命令行执行ipython程序进入交互式界面，按tab查询支持的函数
  可在python/ipython中导入相应的模块后，使用help(function)查询函数支持的参数
"""
from os.path import exists, join, isdir, isfile
"""
  exists : 判断输入路径是否存在， exists()
  join   : 地址拼接，如 join("/usr/bin", "python") 得到路径 "/usr/bin/python"
  isdir  : 判断当前地址是否为目录
  isfile : 判断当前地址是否为文件
"""
from os import walk
"""
  walk  : 遍历输入路径下的目录和文件列表，返回三个参数
          root  输入路径
          dirs  路径下的所有目录
          files 路径下的所有文件
  使用方法如下：
  for root, dirs, files in walk(path):
    for dir in dirs:
      
    for file in files:
      
"""
from argparse import ArgumentParser
"""
  argparse 命令行参数解析的标准模块，可对输入参数的位置、类型进行解析
  亦可使用sys.argv手工处理命令行参数，使用方法如下：
  from sys import argv 或 import sys 并在调用时使用 sys.argv
"""
import re
"""
  re 为正则表达式regular expression的简称，python内置用于正则表达式匹配、查询和替换的模块
  常用函数有以下三个：
  match  : 对字符串从头进行匹配，使用方法：re.match(r"", string)
  search : 对字符串整体进行查询，使用方法：re.search(r"", string)
  sub    : 对字符串的一部分进行匹配和替换，使用方法：re.sub(r"", "", string)
"""

def read_file(file):
  """
    对文本文件进行读取，标准模式，pass和None部分需根据需要自行处理
    read_file函数的参数和返回值，可自行根据需求修改
  """
  with open(file, "r") as fin: # 声明一个读文件的句柄fin
    lines = fin.readlines() # 把文件的所有行读入内存
    for line in lines: # 按行处理
      pass
  
  return None

def write_file(file):
  """
    把内容写入文本文件，标准模式，根据write_file的传入参数，写入数据
  """
  with open(file, "w") as fout:
    print("hello world!", file=fout)
    # fout.write(" ")

if __name__ == "__main__":
  parser = ArgumentParser("log file solution") # 声明一个命令行参数的解析器
  parser.add_argument("path", type=str, help="directory path") # 按顺序增加第一个参数path，字符串类型
  parser.add_argument("type", type=str, help="file type") # 按顺序增加第二个参数type，字符串类型，
  args = parser.parse_args() # 内部调用sys.argv对命令行参数进行解析，返回字典类型
  path = args.path # .后接add_argument的第一个参数名，必须保持一致
  type = args.type
  
  """
  本代码块含义：
  判断path是否存在，如果存在，则遍历path地址下的所有文件和文件夹，调用相应的函数进行处理
  """
  if exists(path):
    for root, dirs, files in walk(path):
      for file in files:
        if re.match(r"%s$" % type, file):
          fpath = join(root, file)
          read_file(fpath)
      for dir in dirs:
        if not re.match(r"^log", dir):
          pass
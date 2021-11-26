#!/usr/bin/env python3

"""
  A script to substitute key word in all files of a directory
"""

import os
import re
import argparse

def replace_word_nonre(file, source, target):
  flag = False
  lines = None
  with open(file, "r") as fin:
    lines = fin.readlines()
  with open(file, "w") as fout:
    for line in lines:
      if source in line:
        flag = True
        fout.write(line.replace(source, target))
      else:
        fout.write(line)
  
  return flag

def replace_word_re(file, source, target):
  flag = False
  lines = None
  mode = re.compile(source)
  with open(file, "r") as fin:
    lines = fin.readlines()
  with open(file, "w") as fout:
    for line in lines:
      if mode.search(line):
        flag = True
        fout.write(mode.sub(line, target))
      else:
        fout.write(line)
  
  return flag

def walk_dir(path, source, target, log, ext, replace_func):
  for dir in os.listdir(path):
    if dir[0] != ".":
      subpath = os.path.join(path, dir)
      if not os.path.isdir(subpath) and ("" == ext or os.path.splitext(subpath)[1] -- ext):
        flag = replace_func(subpath, source, target)
        if log and flag:
          print("replace %s to %s in %s" % (source, target, subpath))
      else:
        walk_dir(subpath, source, target, log, ext, replace_func)

def replace_file_in_dir(args):
  func = replace_word_re if args.re else replace_word_nonre
  walk_dir(args.dict, args.source, args.target, args.log, args.ext, func)


def argument_parse():
  parser = argparse.ArgumentParser(description="substitute key words in files of a directory")
  parser.add_argument("source", action="store", help="source key word")
  parser.add_argument("target", action="store", help="target key word")
  parser.add_argument("--dir", action="store", default=".", help="root directory")
  parser.add_argument("--ext", action="store", default="", help="end with file extension")
  parser.add_argument("--re", action="store_true", help="with regular expression")
  parser.add_argument("--log", action="store_true", help="with log output")
  parser.set_defaults(func=replace_file_in_dir)
  
  return parser


if __name__ == "__main__":
  args = argument_parse()
  print("script configuration")
  print(args)
  args.func(args)
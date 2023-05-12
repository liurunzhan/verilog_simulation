#!/usr/bin/env python3

from sys import argv
from sys import exit as sys_exit
from os import system, popen, makedirs, listdir
from os.path import exists, join, isdir
from time import strftime, localtime
from argparse import ArgumentParser
from shutil import rmtree
from string import Template

case_path = [
  "software/",
  "software/main_tmpl.c",
  "user_def.v"
]

main_tmpl = """/**
  * case : ${case}
  * func : ${description}
  * proj : ${project}
  * vern : ${version}
  * date : ${date}
  */

#include <stdio.h>
#include "${project}.h"

int main(void) 
{
  fprintf(stdout, "test CASE ${case}\\n");
  
  return 0;
}
"""

user_def = """/**
  * case : ${case}
  * func : ${description}
  * proj : ${project}
  * vern : ${version}
  * date : ${date}
  */

initial begin
    $$display("test CASE ${case}");
end
"""

def detect_software(software):
  exists = False
  with popen("%s --version" % software) as pin:
    if pin.read():
      exists = True
  
  return exists

def undefined_function(arguments):
  print("undefined function")

def read_template_from_file(file, default, hash):
  string = None
  template = None
  if exists(file):
    with open(file, "r") as fin:
      string = fin.read()
  else:
    string = default
  try:
    template = Template(string).safe_substitute(hash)
  except:
    template = Template(string).substitute(hash)
  
  return template

def exchange_args_to_dict(args):
  hash = {}
  for name in dir(args):
    value = getattr(args, name)
    if not name.startswith('__') and not callable(value):
      hash[name] = value
  
  return hash

def create_case(args):
  print("create CASE %s by template file" % args.case)
  hash = exchange_args_to_dict(args)
  lines = None
  if exists(args.template):
    with open(args.template, "r") as fin:
      lines = fin.readlines()
  else:
    lines = case_path
  for line in lines:
    line = line.replace("\r", "").replace("\n", "")
    path = join(args.root, args.case, line)
    if line[0] == "#" or " " in line:
      continue
    if line[-1] == "/":
      if not exists(path):
        print("create SUBDIRECTORY %s" % path)
        makedirs(path)
    else:
      paths = line.split("/")
      tfile = join(".", paths[-1])
      if paths[-1] == args.template_c:
        print("generate FILE %s" % path)
        template = read_template_from_file(tfile, main_tmpl, hash)
        with open(path, "w") as fout:
          fout.write(template)
      elif paths[-1] == args.template_v:
        print("generate FILE %s" % path)
        template = read_template_from_file(tfile, user_def, hash)
        with open(path, "w") as fout:
          fout.write(template)

def delete_case(args):
  print("delete CASE %s" % args.case)
  path = join(args.root, args.case)
  if exists(path):
    rmtree(path)

def delete_subdirs(path, dir_name):
  for dir in listdir(path):
    subpath = join(path, dir)
    if isdir(subpath):
      if dir == dir_name:
        rmtree(subpath)
      else:
        delete_subdirs(subpath, dir_name)

def delete_svn_from_dir(args):
  print("delete .svn from SUBDIRECTORY %s" % args.dir)
  delete_subdirs(args.dir, ".svn")

def delete_svn_from_case(args):
  print("delete .svn from CASE %s" % args.case)
  path = join(args.root, args.case)
  delete_subdirs(path, ".svn")

def add_case_to_svn(args):
  print("add case to local svn repository")
  path = join(args.root, args.case)
  system("svn add %s" % path)

def delete_case_from_svn(args):
  print("delete case from local svn repository")
  path = join(args.root, args.case)
  system("svn del %s" % path)

def commit_case_to_svn(args):
  print("commit case to remote svn repository")
  path = join(args.root, args.case)
  system("svn ci %s -m \"commit case %s to svn\"" % (path, args.case))

def delete_git_from_dir(args):
  print("delete .git from SUBDIRECTORY %s" % args.dir)
  delete_subdirs(args.dir, ".git")

def delete_git_from_case(args):
  print("delete .git from CASE %s" % args.case)
  path = join(args.root, args.case)
  delete_subdirs(path, ".git")

def add_case_to_git(args):
  print("add case to local git repository")
  path = join(args.root, args.case)
  system("git add %s" % path)

def delete_case_from_git(args):
  print("delete case from local git repository")
  path = join(args.root, args.case)
  system("svn del %s" % path)

def commit_case_to_git(args):
  print("commit case to remote git repository")
  path = join(args.root, args.case)
  system("git commit %s -m \"commit case %s to svn\"" % (path, args.case))

def add_subparser_args_case(subparsers, cmd, help, func=undefined_function):
  current_date = strftime("%Y-%m-%d", localtime())
  
  # add subparser to subparsers
  parser = subparsers.add_parser(cmd, help=help)
  
  # add positional argument to subparser
  parser.add_argument("case", action="store", type=str, help="case name")
  
  # add optional argument to subparser
  parser.add_argument("--root",        action="store", type=str, default=".",           help="root directory")
  
  # add optional argument to subparser
  parser.add_argument("--description", action="store", type=str, default="",            help="case description")
  parser.add_argument("--project",     action="store", type=str, default="U98TSH128AP", help="project name")
  parser.add_argument("--version",     action="store", type=str, default="0.0.0",       help="case version")
  parser.add_argument("--date",        action="store", type=str, default=current_date,  help="last modified date")
  
  # add optional argument to subparser
  parser.add_argument("--template",    action="store", type=str, default="case.path",   help="verilog template file")
  parser.add_argument("--template-v",  action="store", type=str, default="user_def.v",  help="verilog template file")
  parser.add_argument("--template-c",  action="store", type=str, default="main_tmpl.c",  help="c template file")
  parser.set_defaults(func=func)
  
  return parser

def add_subparser_args_sdir(subparsers, cmd, help, func):
  parser = subparsers.add_parser(cmd, help=help)
  parser.add_argument("dir", action="store", type=str, help="directory")
  parser.set_defaults(func=func)
  
  return parser

def parse_cmd_arguments():
  parser = ArgumentParser(description="manage cases in project")
  subparsers = parser.add_subparsers()
  add_subparser_args_case(subparsers, cmd="create",     help="create case from template"               , func=create_case)
  add_subparser_args_case(subparsers, cmd="delete",     help="delete case from a given path"           , func=delete_case)
  add_subparser_args_case(subparsers, cmd="clean-svn",  help="recursively clean .svn from a given path", func=delete_svn_from_case)
  add_subparser_args_case(subparsers, cmd="svn-add",    help="add case to local svn repository"        , func=add_case_to_svn)
  add_subparser_args_case(subparsers, cmd="svn-del",    help="delete case from local svn repository"   , func=delete_case_from_svn)
  add_subparser_args_case(subparsers, cmd="svn-ci",     help="commit case to remote svn server"        , func=commit_case_to_svn)
  add_subparser_args_case(subparsers, cmd="clean-git",  help="recursively clean .git from a given path", func=delete_git_from_case)
  add_subparser_args_case(subparsers, cmd="git-add",    help="add case to local git repository"        , func=add_case_to_git)
  add_subparser_args_case(subparsers, cmd="git-rm",     help="delete case from local git repository"   , func=delete_case_from_git)
  add_subparser_args_case(subparsers, cmd="git-commit", help="commit case to remote git server"        , func=commit_case_to_git)
  add_subparser_args_sdir(subparsers, cmd="rm-svn",     help="rm .svn from a given directory"          , func=delete_svn_from_dir)
  add_subparser_args_sdir(subparsers, cmd="rm-git",     help="rm .git from a given directory"          , func=delete_git_from_dir)
  
  return parser.parse_args()

if __name__ == "__main__":
  if len(argv) == 1:
    print("no command line argument is given")
    print("use following command to get usage of %s" % argv[0])
    print("%s --help" % argv[0])
    sys_exit(-1)
  arguments = parse_cmd_arguments()
  arguments.func(arguments)
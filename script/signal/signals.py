#!/usr/bin/python3

import os
import argparse
from enum import Enum

class TimeUnit(Enum):
  s  = 1
  ms = 10**3
  us = 10**6
  ns = 10**9
  ps = 10**12
  fs = 10**15

# fsdbreport command style:
# fsdbreport file.fsdb -bt <xxx> -et <xxx> -exp <xxx> -of <xxx> -s "<xxx>" -csv -o "<xxx>"
FSDBREPORT_CMD = "fsdbreport {fsdb} {begin_time} {end_time} {expression} -of {output_format} -s \"{signal}\" -csv -o \"{file}\" >/dev/null 2>&1"

def format_point(signal):
  if signal.startswith("/"):
    signal = signal[1:len(signal)]
  return signal.replace("/", ".")

def format_backslash(signal):
  if not signal.startswith("/"):
    signal = "/" + signal
  return signal.replace(".", "/")

def arg_parse():
  parser = argparse.ArgumentParser(description="a parser to get signals from simulation file")
  parser.add_argument("signals", nargs="+", type=str, help="signal paths")
  parser.add_argument("-i", "--input", type=str, help="input simulation file")
  parser.add_argument("-o", "--output", type=str, help="output file")
  parser.add_argument("-exp", "--expression", default="", type=str, help="signal condition expression")
  parser.add_argument("-bt", "--begin_time", default=0, type=int, help="begin_time time")
  parser.add_argument("-et", "--end_time", default=-1, type=int, help="end_time time")
  parser.add_argument("-of", "--output_format", default="b", choices=["b", "o", "d", "u", "h"], type=str, help="output value format style")
  def func(args):
    begin_time = "-bt %d" % (args.begin_time) if args.begin_time > 0 else ""
    end_time = "-et %d" % (args.end_time) if args.end_time > 0 else ""
    expression = "-exp \"%s\"" % (args.expression) if args.expression != "" else ""
    signals = [format_point(signal) for signal in args.signals]
    for signal in signals:
      cmd = FSDBREPORT_CMD.format(fsdb=args.input, begin_time=begin_time, end_time=end_time, expression=expression, output_format=args.output_format, file=args.output)
      os.system(cmd)
  return parser.parse_args()

if __name__ == "__main__":
  args = arg_parse()
  args.func(args)
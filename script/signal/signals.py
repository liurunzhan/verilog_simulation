#!/usr/bin/env python3

from os import system
from os.path import join
from argparse import ArgumentParser
from enum import Enum
from fnmatch import fnmatch

# import self-defined libraries
from sys import path
path.append(join(__file__, ".."))
from basic_apis import flatten

class TimeUnit(Enum):
  s  = 1
  ms = 10**3
  us = 10**6
  ns = 10**9
  ps = 10**12
  fs = 10**15

def format_point(signal):
  if signal.startswith("/"):
    signal = signal[1:len(signal)]
  return signal.replace("/", ".")

def format_backslash(signal):
  signal.replace(".", "/")
  if not signal.startswith("/"):
    signal = "/" + signal
  return signal

class Signal(object):
  def __init__(self, signal, alias_name, output_format, output):
    self.signal = format_backslash(signal=signal)
    self.a      = alias_name
    self.of     = output_format
    self.output = output
  def __contains__(self, signal):
    return fnmatch(signal, self.signal)

class SignalList(object):
  def __init__(self):
    self.signals = []
  def __len__(self):
    return len(self.signals)
  def __iter__(self):
    return iter(self.signals)
  def __next__(self):
    return next(self.signals)
  def __contains__(self, signal):
    for signal_mode in self.signals:
      if signal in signal_mode:
        return True
    return False
  def append(self, signal, alias_name, output_format, output):
    self.signals.append(Signal(signal=signal, alias_name=alias_name, output_format=output_format, output=output))
    return self
  def extend(self, signals, default_output_format, default_output):
    for signal in signals:
      self.append(signal=signal, alias_name=signal, output_format=default_output_format, output=default_output)
    return self

class FsdbReportCmd(object):
  def __init__(self, fsdb, begin_time, end_time, expression, output_format):
    self.fsdb = fsdb
    self.bt   = "-bt %d" % (begin_time) if begin_time > 0 else ""
    self.et   = "-et %d" % (end_time) if end_time > 0 else ""
    self.exp  = "-exp \"%s\"" % (expression) if expression != "" else ""
    self.of   = output_format
  def __str__(self):
    return self.to_cmd(signal="***", file="***")
  def __repr__(self):
    return str(self)
  def to_cmd(self, signal, file):
    # fsdbreport command style:
    # fsdbreport file.fsdb -bt <xxx> -et <xxx> -exp <xxx> -of <xxx> -s "<xxx>" -csv -o "<xxx>"
    cmd = "fsdbreport {fsdb} {bt} {et} {exp} -of {of} -s \"{signal}\" -csv -o \"{file}\" >/dev/null 2>&1".format(fsdb=self.fsdb, bt=self.bt, et=self.et, exp=self.exp, of=self.of, signal=signal, file=file)
    return cmd
    

def arg_parse():
  parser = ArgumentParser(description="a parser to get signals from simulation file")
  parser.add_argument("signals", nargs="+", type=str, help="signal paths")
  parser.add_argument("-i", "--input", type=str, required=True, help="input simulation file, must be given")
  parser.add_argument("-exp", "--expression", default="", type=str, help="signal condition expression")
  parser.add_argument("-bt", "--begin_time", default=0, type=int, help="begin_time time")
  parser.add_argument("-et", "--end_time", default=-1, type=int, help="end_time time")
  parser.add_argument("-find_forces", "--find_forces", action="store_true", help="find all forces in given scopes")
  parser.add_argument("-exclude_scope", "--exclude_scope", default=[], type=str, append=True, help="exclude given scopes, support one or more")
  parser.add_argument("-o", "--output", type=str, help="output file")
  parser.add_argument("-of", "--output_format", default="b", choices=["b", "o", "d", "u", "h"], type=str, help="output value format style")
  parser.add_argument("--level", default=-1, type=int, help="signal level")
  def func(args):
    cmd_gen = FsdbReportCmd(fsdb=args.input, begin_time=args.begin_time, end_time=args.end_time, expression=args.expression, output_format=args.output_format, file=args.output)
    signals = [format_backslash(signal) for signal in args.signals]
    for signal in signals:
      cmd = cmd_gen.to_cmd(signal=signal, file=args.output)
      system(cmd)
  return parser.parse_args()

if __name__ == "__main__":
  args = arg_parse()
  args.func(args)
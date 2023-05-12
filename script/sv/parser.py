#!/usr/bin/env python3

from enum import Enum

class SVTokenType(Enum):
  COMMIT   = 0
  VARIABLE = 1
  STRING   = 2

class SVTokenState(Enum):
  IDLE     = 0
  VARIABLE = 1
  NUMBER   = 2
  DSTRING  = 3
  SSTRING  = 4
  OPERATOR = 5

class SVScanner(object):
  def __init__(self):
    self.token = []
  def from_file(self, file, encoding="utf-8"):
    pre_state = SVTokenState.IDLE
    state = pre_state
    with open(file, "r", encoding=encoding) as fin:
      for c in fin.read():
        pre_state = state
        if state == SVTokenState.IDLE:
          if c.isalpha() or c == "_":
            state = SVTokenState.VARIABLE
          elif c.isnumeric():
            state = SVTokenState.NUMBER
          elif c == "\"":
            state = SVTokenState.DSTRING
          elif c == "\'":
            state = SVTokenState.SSTRING
        elif state == SVTokenState.VARIABLE:
          if c.isalnum() or c == "_":
            state = SVTokenState.VARIABLE
          else:
            state = SVTokenState.IDLE
        elif state == SVTokenState.NUMBER:
          if c.isnumeric():
            state = SVTokenState.NUMBER
          else:
            state = SVTokenState.IDLE
        elif state == SVTokenState.DSTRING:
          if c != "\"":
            state = SVTokenState.DSTRING
          else:
            state = SVTokenState.IDLE
        elif state == SVTokenState.SSTRING:
          if c != "\'":
            state = SVTokenState.SSTRING
          else:
            state = SVTokenState.IDLE
    if pre_state == SVTokenState.IDLE and state == SVTokenState.VARIABLE:
      pass
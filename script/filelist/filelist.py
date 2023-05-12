#!/usr/bin/env python3

# import standard libraries
from os import scandir, DirEntry
from os.path import exists, isdir, isfile, basename, dirname, join
from fnmatch import fnmatch
from pathlib import PurePath

# import self-defined libraries
from sys import path
path.append(join(__file__, ".."))
from basic_apis import flatten

def ptmatch(item, pattern):
  return PurePath(item).match(pattern) or (isfile(item) and PurePath(dirname(item)).match(pattern))

class EntryFilter(object):
  def __init__(self, includes=[], skips=[], is_path=False):
    self.__includes = includes
    self.__skips    = skips
    self.__match    = ptmatch if self.is_path else fnmatch
  def __contains__(self, item):
    if (self.__match == fnmatch and item.startswith(".")) or item.endswith("~"):
      return False
    if len(self.__includes) == 0:
      return not self.in_skips(item)
    for include in self.__includes:
      if self.__match(item, include):
        return not self.in_skips(item)
    return False
  def includes_length(self):
    return len(self.__includes)
  def skips_length(self):
    return len(self.__skips)
  def in_includes(self, item):
    for include in self.__includes:
      if self.__match(item, include):
        return True
    return False
  def in_skips(self, item):
    for skip in self.__skips:
      if self.__match(item, skip):
        return True
    return False
  def append(self, include=None, skip=None):
    if include is not None:
      self.__includes.append(include)
    if skip is not None:
      self.__skips.append(skip)
    return self
  def remove(self, include=None, skip=None):
    if include is not None:
      while include in self.__includes:
        self.__includes.remove(include)
    if skip is not None:
      while skip in self.__skips:
        self.__skips.remove(include)
  def extend(self, includes=None, skips=None):
    if includes is not None:
      for include in includes:
        if include not in self.__includes:
          self.__includes.append(include)
    if skips is not None:
      for skip in skips:
        if skip not in self.__skips:
          self.__skips.append(skip)
    return self

class FileFilter(object):
  def __init__(self, include_paths=[], skip_paths=[], include_dirs=[], skip_dirs=[], include_files=[], skip_files=[]):
    self.__path_filter = EntryFilter(includes=include_paths, skips=skip_paths, is_path=True)
    self.__dir_filter  = EntryFilter(includes=include_dirs, skips=skip_dirs, is_path=False)
    self.__file_filter = EntryFilter(includes=include_files, skips=skip_files, is_path=False)
  def __contains__(self, item):
    if isinstance(item, str):
      if exists(item):
        filter = self.__dir_filter if isdir(item) else self.__file_filter 
        return basename(item) in filter
      return item in self.__file_filter
    elif isinstance(item, DirEntry):
      filter = self.__dir_filter if item.is_dir() else self.__file_filter
      return item.name in filter
    return False
  def __walk(self, path, filelist, is_iter):
    for item in scandir(path):
      if item.is_file() and not item.is_symlink() and item.name in self.__file_filter:
        if (self.__dir_filter.includes_length() == 0 or basename(dirname(item.path)) in self.__dir_filter) or (self.__path_filter.includes_length() == 0 or item.path in self.__path_filter):
          filelist.append(item.path)
      elif is_iter and item.is_dir() and not self.__dir_filter.in_skips(item.name) and not self.__path_filter.in_skips(item.path):
        self.__walk(path=item.path, filelist=filelist, is_iter=is_iter)
  def walk(self, path, is_iter=False):
    filelist = []
    self.__walk(path=path, filelist=filelist, is_iter=is_iter)
    return filelist

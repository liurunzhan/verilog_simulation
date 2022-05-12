#!/usr/bin/python3

from os import scandir, DirEntry
from os.path import exists, isdir, isfile, basename
from fnmatch import fnmatch

class itemFilter(object):
  def __init__(self, includes=[], skips=[]):
    self.includes = includes
    self.skips    = skips
  def __contains__(self, item):
    if item.startswith(".") or item.endswith("~"):
      return False
    if len(self.includes) == 0:
      for skip in self.skips:
        if fnmatch(item, skip):
          return False
      return True
    for include in self.includes:
      if fnmatch(item, include):
        for skip in self.skips:
          if fnmatch(item, skip):
            return False
        return True
    return False
  def append(self, include=None, skip=None):
    if include is not None:
      self.includes.append(include)
    if skip is not None:
      self.skips.append(skip)
    return self
  def extend(self, includes=None, skips=None):
    if includes is not None:
      self.includes.extend(includes)
    if skips is not None:
      self.skips.extend(skips)
    return self

class fileFilter(object):
  def __init__(self, include_dirs=[], skip_dirs=[], include_files=[], skip_files=[]):
    self.dir_filter = itemFilter(includes=include_dirs, skips=skip_dirs)
    self.file_filter = itemFilter(includes=include_files, skips=skip_files)
  def __contains__(self, item):
    if isinstance(item, str):
      if exists(item):
        filter = self.dir_filter if isdir(item) else self.file_filter 
        return basename(item) in filter
      return item in self.file_filter
    elif isinstance(item, DirEntry):
      filter = self.dir_filter if item.is_dir() else self.file_filter
      return item.name in filter
    return False
  def __walk(self, path, filelist, is_iter):
    for item in scandir(path):
      if item.is_file() and not item.is_symlink() and item.name in self.file_filter:
        filelist.append(item.path)
      elif is_iter and item.is_dir() and item.name in self.dir_filter:
        self.__walk(path=item.path, filelist=filelist, is_iter=is_iter)
  def walk(self, path, is_iter=False):
    filelist = []
    self.__walk(path=path, filelist=filelist, is_iter=is_iter)
    return filelist

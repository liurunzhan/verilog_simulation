#!/usr/bin/python3

# standard libraries
from json import load
from configparser import ConfigParser
from os.path import exists, basename
import argparse

CONFIG_PLATFORM = "PLATFORM"

def items_from_ini(file):
	items = {}
	try:
		conf = ConfigParser()
		conf.read(file)
		data = conf.items(CONFIG_PLATFORM)
		for i in range(len(data)):
			try:
				items[data[i][0]] = int(data[i][1])
			except:
				items[data[i][0]] = data[i][1]
	except:
		pass
	return items

def items_from_json(file):
	items = {}
	with open(file, "r") as fin:
		data = load(fin)[CONFIG_PLATFORM]
		for key in data:
			items[key] = data[key]
	return items

def items_from_file(file):
	if not exists(file):
		return {}
	items = None
	name = basename(file)
	if name.endswith(".json"):
		items = items_from_json(file)
	elif name.endswith(".ini"):
		items = items_from_ini(file)
	else:
		items = {}
	return items

class Platform(object):
	def __init__(self, items):
		self.max_threads = items["MAX_THREADS"]
		self.max_hours = items["MAX_HOURS"]

if __name__ == "__main__":
	items = items_from_file("./config.ini")
	print(items)
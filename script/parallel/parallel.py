#!/usr/bin/python3

# self-built modules
import json
import configparser
import os
import argparse

CONFIG_PLATFORM = "PLATFORM"

def items_from_ini(file):
	items = {}
	try:
		conf = configparser.ConfigParser()
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
		data = json.load(fin)[CONFIG_PLATFORM]
		for key in data:
			items[key] = data[key]
	return items

def items_from_file(file):
	if not os.path.exists(file):
		return {}
	items = None
	basename = os.path.basename(file)
	if basename.endswith(".json"):
		items = items_from_json(file)
	elif basename.endswith(".ini"):
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
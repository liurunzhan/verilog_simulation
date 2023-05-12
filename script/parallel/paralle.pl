#!/usr/bin/env perl

# language style
use strict;
use warning;

# third-party modules
use Config::IniFiles;
use JSON;

my $CONFIG_PLATFORM = "PLATFORM";

sub items_from_ini {
  my ($file) = @_;
	my %items = ();
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
	return \%items;
}

sub items_from_json {
  my ($file) = @_;
	my %items = ();
	with open(file, "r") as fin:
		data = json.load(fin)[CONFIG_PLATFORM]
		for key in data:
			items[key] = data[key]
	return \%items;
}

sub items_from_file {
  my ($file) = @_;
	if not os.path.exists(file):
		return {}
	my %items = ();
	basename = os.path.basename(file)
	if basename.endswith(".json"):
		items = items_from_json(file)
	elsif basename.endswith(".ini"):
		items = items_from_ini(file)
	else:
		
	return \%items;
}

sub run_commands {
  my ($items, $commands) = @_;
  
	for my $i () {
		
	}
}
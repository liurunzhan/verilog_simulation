#!/usr/bin/perl -w

## AUTHOR      : liurunzhan
## DATE        : 2021-02-01
## VERSION     : 1.1
## LICENSE     : GPL 3.0
## FUNCTION    : filelist generator
## DESCRIPTION : 1. generate file list of Verilog file(*.v) or System Verilog file (*.sv)
##             : from a given directory, which can be used in simulation and synthesis.
##             : 2. each subdirectory is considered as a ip made from different modules,
##             : occupying a individual block in the file list.

use strict;
use warnings;
use Cwd;
use File::Spec;
use File::Basename;
use Getopt::Long;
use Scalar::Util qw(looks_like_number);

$Getopt::Long::ignorecase = 0;

my $TRUE = 1;
my $FALSE = 0;

# parse command lines
my %cmds = %{cmd_parser()};

if($cmds{"with_help"})
{
  help_print();
  exit(0);
}

cmd_print(\%cmds);

my $files = generate_filelist(\%cmds);
if($cmds{"print"})
{ print_filelist($files); }
else
{ write_filelist($files, $cmds{"output"}); }

sub cmd_parser
{
  my $work = ".";
  my %hash = ();
  my %uncover = ();
  my $with_definition = $FALSE;
  my $with_class      = $FALSE;
  my $with_task       = $FALSE;
  my $with_function   = $FALSE;
  my $with_interface  = $FALSE;
  my $output          = "filelist";
  my $print           = $FALSE;
  my $with_help       = $FALSE;

  GetOptions(
    "work:s"     => \$work,
    "uncover:s"  => \%hash,
    "definition" => \$with_definition,
    "class"      => \$with_class,
    "task"       => \$with_task,
    "function"   => \$with_function,
    "interface"  => \$with_interface,
    "output:s"   => \$output,
    "print"      => \$print,
    "help"       => \$with_help
  ) or die "parse command line error!";

  $work            = ($work            eq "" ? "."        : $work  );
  $with_definition = ($with_definition == 0  ? $FALSE     : $TRUE  );
  $with_class      = ($with_class      == 0  ? $FALSE     : $TRUE  );
  $with_task       = ($with_task       == 0  ? $FALSE     : $TRUE  );
  $with_function   = ($with_function   == 0  ? $FALSE     : $TRUE  );
  $with_interface  = ($with_interface  == 0  ? $FALSE     : $TRUE  );
  $output          = ($output          eq "" ? "filelist" : $output);
  $print           = ($print           == 0  ? $FALSE     : $TRUE  );
  $with_help       = ($with_help       == 0  ? $FALSE     : $TRUE  );
  
  # if uncover has file passed, decode this file and add them to @uncover
  foreach my $dir (sort{$a cmp $b} keys %hash)
  {
    if(-f $dir)
    {
      open my $fin, "<", $dir or die "$dir is read wrong!";
      while(<$fin>)
      {
        $_ =~ s/\r?\n//g;
        if(($_ ne "") && (!exists($uncover{$_})))
        { $uncover{$_} = 0; }
      }
      close($fin);
    }
    elsif($dir ne "")
    {
      if(!exists($uncover{$dir}))
      { $uncover{$dir} = 0; }
    }
  }
  
  my %cmds = (
    "work"            => $work,
    "uncover"         => \%uncover,
    "with_definition" => $with_definition,
    "with_class"      => $with_class,
    "with_task"       => $with_task,
    "with_function"   => $with_function,
    "with_interface"  => $with_interface,
    "output"          => $output,
    "print"           => $print,
    "with_help"       => $with_help
  );
  
  return \%cmds;
}

sub cmd_print
{
  my ($cmds) = @_;
  print("CONFIGURATIONS ARE : \n");
  print("work            => ", $cmds{"work"},                                       "\n");
  print("uncover         => ", join(":", sort{$a cmp $b} keys %{$cmds{"uncover"}}), "\n");
  print("with_definition => ", $cmds{"with_definition"} == 0 ? "FALSE" : "TRUE",    "\n");
  print("with_class      => ", $cmds{"with_class"}      == 0 ? "FALSE" : "TRUE",    "\n");
  print("with_task       => ", $cmds{"with_task"}       == 0 ? "FALSE" : "TRUE",    "\n");
  print("with_function   => ", $cmds{"with_function"}   == 0 ? "FALSE" : "TRUE",    "\n");
  print("with_interface  => ", $cmds{"with_interface"}  == 0 ? "FALSE" : "TRUE",    "\n");
  print("output          => ", $cmds{"output"},                                     "\n");
  print("print           => ", $cmds{"print"}           == 0 ? "FALSE" : "TRUE",    "\n");
  print("with_help       => ", $cmds{"with_help"}       == 0 ? "FALSE" : "TRUE",    "\n\n");
}

sub help_print
{
  print("INTRODUCTION of $0:\n");
  print("$0 supports (system) verilog project\n");
  print(" " x length($0), " is designed to generate file list\n\n");
  print("USAGE of $0:\n");
  print("$0 <cmds>\n");
  print("<cmds> : \n");
  print("         -w --work       redefine work directory with (system) verilog project once\n");
  print("         -u --uncover    define uncovered directory in project once or more\n");
  print("         -d --definition include macro definitions and parameters or not\n");
  print("         -c --class      include class or not\n");
  print("         -t --task       include task or not\n");
  print("         -f --function   include function or not\n");
  print("         -i --interface  include interface or not\n");
  print("         -o --output     output file name\n");
  print("         -p --print      print to terminal or file given by -o\n");
  print("         -h --help       get introduction and usage of $0\n");
  print("EXAMPLE of $0 : \n");
  print("$0 -w ../.. -d => work directory is ../.., filelist with definitions\n\n");
}

# used to judge whether a system verilog/verilog file
# has a module defined or not
sub judge_file_is_module
{
  my ($file) = @_;
  my $flag = $FALSE;
  open my $fin, "<", $file or die "$file does not exists!";
  while(<$fin>)
  {
    $_ =~ s/\r?\n$//g;
    $_ =~ s/^([\s\t]*)//g;
    if($_ =~ /^module[\s\t]/)
    { $flag = $TRUE; last; }
  }
  close($fin);
  
  return $flag;
}

# used to judge whether a system verilog/verilog file 
# only has macro definitions, parameters and annotation 
# defined or not
sub judge_file_is_definition
{
  my ($file) = @_;
  my $flag = $TRUE;
  open my $fin, "<", $file or die "$file does not exists!";
  while(<$fin>)
  {
    $_ =~ s/\r?\n$//g;
    $_ =~ s/^([\s\t]*)//g;
    if(($_ !~ /^`define[\s\t]/) && ($_ !~ /^parameter[\s\t]/) && ($_ !~ /^localparam[\s\t]/)
     && ($_ !~ /^defparam[\s\t]/) && ($_ !~ /^specparam[\s\t]/) && ($_ !~ /^\/\//) && ($_ ne ""))
    { $flag = $FALSE; last; }
  }
  close($fin);
  
  return $flag;
}

# used to judge whether a system verilog/verilog file 
# has class defined or not
sub judge_file_is_class
{
  my ($file) = @_;
  my $flag = $FALSE;
  open my $fin, "<", $file or die "$file does not exists!";
  while(<$fin>)
  {
    $_ =~ s/\r?\n$//g;
    $_ =~ s/^([\s\t]*)//g;
    if($_ =~ /^class[\s\t]/)
    { $flag = $TRUE; last; }
  }
  close($fin);
  
  return $flag;
}

# used to judge whether a system verilog/verilog file 
# has a task defined or not
sub judge_file_is_task
{
  my ($file) = @_;
  my $flag = $FALSE;
  open my $fin, "<", $file or die "$file does not exists!";
  while(<$fin>)
  {
    $_ =~ s/\r?\n$//g;
    $_ =~ s/^([\s\t]*)//g;
    if($_ =~ /^task[\s\t]/)
    { $flag = $TRUE; last; }
  }
  close($fin);
  
  return $flag;
}

# used to judge whether a system verilog/verilog file 
# has a function defined or not
sub judge_file_is_function
{
  my ($file) = @_;
  my $flag = $FALSE;
  open my $fin, "<", $file or die "$file does not exists!";
  while(<$fin>)
  {
    $_ =~ s/\r?\n$//g;
    $_ =~ s/^([\s\t]*)//g;
    if($_ =~ /^function[\s\t]/)
    { $flag = $TRUE; last; }
  }
  close($fin);
  
  return $flag;
}

# used to judge whether a system verilog/verilog file 
# has class defined or not
sub judge_file_is_interface
{
  my ($file) = @_;
  my $flag = $FALSE;
  open my $fin, "<", $file or die "$file does not exists!";
  while(<$fin>)
  {
    $_ =~ s/\r?\n$//g;
    $_ =~ s/^([\s\t]*)//g;
    if($_ =~ /^interface[\s\t]/)
    { $flag = $TRUE; last; }
  }
  close($fin);
  
  return $flag;
}

sub walk_dir
{
  my ($cmds, $hash, $dir) = @_;
  
  my %uncover         = %{$$cmds{"uncover"}     };
  my $with_definition = $$cmds{"with_definition"};
  my $with_class      = $$cmds{"with_class"     };
  my $with_task       = $$cmds{"with_task"      };
  my $with_function   = $$cmds{"with_function"  };
  my $with_interface  = $$cmds{"with_interface" };
  my $with_help       = $$cmds{"with_help"      };
  
  # absolute path
  if(exists($uncover{$dir}))
  { return; }
  
  opendir (my $din, $dir) or die "$dir does not exists";
  my @subdirs = readdir($din);
  closedir($din);
  my @dirs = ();
  foreach my $subdir (@subdirs)
  {
    # relative path
    if(($subdir !~ /^\./) && (!exists($uncover{$subdir})))
    {
      my $path = File::Spec->catdir($dir, $subdir);
      if(-d $path)
      { push(@dirs, $path); }
      elsif((-f $path) && ($path =~ /\.s?v$/))
      {
        if(!exists($$hash{$dir}))
        {
          $$hash{$dir} = 
          {
            "incdir"     => $FALSE,
            "module"     => [],
            "definition" => [],
            "class"      => [],
            "task"       => [],
            "function"   => [],
            "interface"  => [],
          };
        }
        if(judge_file_is_module($path))
        { push(@{$$hash{$dir}{"module"}}, $subdir); }
        elsif(judge_file_is_definition($path))
        {
          if($with_definition)
          { push(@{$$hash{$dir}{"definition"}}, $subdir); }
          else
          {
            if($FALSE == $$hash{$dir}{"incdir"})
            { $$hash{$dir}{"incdir"} = $TRUE; }
          }
        }
        elsif(judge_file_is_class($path))
        {
          if($with_class)
          { push(@{$$hash{$dir}{"class"}}, $subdir); }
          else
          {
            if($FALSE == $$hash{$dir}{"incdir"})
            { $$hash{$dir}{"incdir"} = $TRUE; }
          }
        }
        elsif(judge_file_is_task($path))
        {
          if($with_task)
          { push(@{$$hash{$dir}{"task"}}, $subdir); }
          else
          {
            if($FALSE == $$hash{$dir}{"incdir"})
            { $$hash{$dir}{"incdir"} = $TRUE; }
          }
        }
        elsif(judge_file_is_function($path))
        {
          if($with_function)
          { push(@{$$hash{$dir}{"function"}}, $subdir); }
          else
          {
            if($FALSE == $$hash{$dir}{"incdir"})
            { $$hash{$dir}{"incdir"} = $TRUE; }
          }
        }
        elsif(judge_file_is_interface($path))
        {
          if($with_interface)
          { push(@{$$hash{$dir}{"interface"}}, $subdir); }
          else
          {
            if($FALSE == $$hash{$dir}{"incdir"})
            { $$hash{$dir}{"incdir"} = $TRUE; }
          }
        }
      }
    }
  }
  foreach my $path (@dirs)
  { walk_dir($cmds, $hash, $path); }
}

sub generate_filelist
{
  my ($cmds) = @_;
  my $work = $$cmds{"work"};
  my %hash = ();
  walk_dir($cmds, \%hash, $work);
  
  return \%hash;
}

sub write_filelist
{
  my ($hash, $file) = @_;
  if(!defined($hash) || !%{$hash})
  {
    print("no file is selected in $file\n");
    exit(-1);
  }
  print("write file list in FILE $file:\n");
  open my $fout, ">", $file or die "$file cannnot be written";
  foreach my $path (sort{$a cmp $b} keys %{$hash})
  {
    print $fout "\n// $path\n";
    if($$hash{$path}{"incdir"} == $TRUE)
    { print $fout "+incdir+$path\n"; }
    foreach my $subpath (sort{$a cmp $b} @{$$hash{$path}{"definition"}})
    {
      my $tmp = File::Spec->catfile($path, $subpath);
      print $fout "$tmp\n";
    }
    foreach my $subpath (sort{$a cmp $b} @{$$hash{$path}{"module"}})
    {
      my $tmp = File::Spec->catfile($path, $subpath);
      print $fout "$tmp\n";
    }
    foreach my $subpath (sort{$a cmp $b} @{$$hash{$path}{"class"}})
    {
      my $tmp = File::Spec->catfile($path, $subpath);
      print $fout "$tmp\n";
    }
    foreach my $subpath (sort{$a cmp $b} @{$$hash{$path}{"task"}})
    {
      my $tmp = File::Spec->catfile($path, $subpath);
      print $fout "$tmp\n";
    }
    foreach my $subpath (sort{$a cmp $b} @{$$hash{$path}{"function"}})
    {
      my $tmp = File::Spec->catfile($path, $subpath);
      print $fout "$tmp\n";
    }
    foreach my $subpath (sort{$a cmp $b} @{$$hash{$path}{"interface"}})
    {
      my $tmp = File::Spec->catfile($path, $subpath);
      print $fout "$tmp\n";
    }
  }
  close($fout);
  print("writing done!\n");
}

sub print_filelist
{
  my ($hash) = @_;
  if(!defined($hash) || !%{$hash})
  {
    print("no file is selected\n");
    exit(-1);
  }
  print("print file list to TERMINAL\n\n");
  foreach my $path (sort{$a cmp $b} keys %{$hash})
  {
    print("\n// $path\n");
    if($$hash{$path}{"incdir"} == $TRUE)
    { print("+incdir+$path\n"); }
    foreach my $subpath (sort{$a cmp $b} @{$$hash{$path}{"definition"}})
    {
      my $tmp = File::Spec->catfile($path, $subpath);
      print("$tmp\n");
    }
    foreach my $subpath (sort{$a cmp $b} @{$$hash{$path}{"module"}})
    {
      my $tmp = File::Spec->catfile($path, $subpath);
      print("$tmp\n");
    }
    foreach my $subpath (sort{$a cmp $b} @{$$hash{$path}{"class"}})
    {
      my $tmp = File::Spec->catfile($path, $subpath);
      print("$tmp\n");
    }
    foreach my $subpath (sort{$a cmp $b} @{$$hash{$path}{"task"}})
    {
      my $tmp = File::Spec->catfile($path, $subpath);
      print("$tmp\n");
    }
    foreach my $subpath (sort{$a cmp $b} @{$$hash{$path}{"function"}})
    {
      my $tmp = File::Spec->catfile($path, $subpath);
      print("$tmp\n");
    }
    foreach my $subpath (sort{$a cmp $b} @{$$hash{$path}{"interface"}})
    {
      my $tmp = File::Spec->catfile($path, $subpath);
      print("$tmp\n");
    }
  }
  print("\nprinting done!\n");
}
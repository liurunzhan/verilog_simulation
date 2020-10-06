#!/bin/sh

root=$1
sim_dir=${root}/sim
src_dir=${root}/src
tool_dir=${root}/tool

if test -z "$root"
then
  echo "project name cannot be empty!"
  exit 1
fi

if [ -d ${root} ]
then
  echo "project directory ${root} has alread existed!"
  echo "please remove or rename it or define a new project name"
  exit 1
fi

mkdir -p ${root}
mkdir -p ${sim_dir}
mkdir -p ${src_dir}
mkdir -p ${tool_dir}

# go to tool directory
cd ${tool_dir}

# clone repository of iverilog and install it
if [ -z `which iverilog` ]; then
  git clone --recursive https://github.com/steveicarus/iverilog iverilog
  cd iverilog
  ./autoconf.sh
  ./configure
  make
  sudo make install
  cd ..
fi

if [ -z `which iverilog` ]; then
  echo "verilog compiler is not installed or found!"
  exit 1
fi

# clone repository of gtkwave and install it
if [ -z `which gtkwave` ]; then
  git clone --recursive https://github.com/gtkwave/gtkwave gtkwave
  cd gtkwave/gtkwave3
  ./configure
  make
  sudo make install
  cd ../..
fi

if [ -z `which gtkwave` ]; then
  echo "wave debug software is not installed or found!"
  exit 1
fi

# clone repository of yosys and install it
if [ -z `which yosys` ]; then
  git clone --recursive https://github.com/YosysHQ/yosys yosys
  cd yosys
  make config-gcc
  make
  sudo make install
  cd ..
fi

if [ -z `which yosys` ]; then
  echo "synthesis software is not installed or found!"
  exit 1
fi

# back to root directory
cd ../.. 

# create Makefile in simulation directory
echo ".PHONY: all clean
all:
	./run
clean:
	-rm -rf ../../${root}
" > ${sim_dir}/Makefile

# create run in simulation directory to call iverilog and gtkwave
echo "#!/bin/sh

rm -f mainsim mainsim.vcd mainsim.lxt
list=\`cat filelist\`
iverilog -g2012 -o mainsim mainsim.v \$list
vvp -n mainsim -lxt2
cp mainsim.vcd mainsim.lxt
gtkwave mainsim.lxt
" > ${sim_dir}/run

# create file list in simulation directory
echo  "../src/${root}.v" > ${sim_dir}/filelist

# create ip top in source directory
echo "module ${root} (
  rstn,
  clk
);
input rstn;
input clk;

endmodule
" > ${src_dir}/${root}.v

# create top file in simulation directory
echo "\`timescale 1ns/1ns

module top();
	
reg sysrstn;
reg rstn;
reg clk;

parameter SYSRST_START  = 10;
parameter RST_START     = 20-SYSRST_START;
parameter CLK_START     = 30-RST_START;
parameter SYSRST_END    = 9900-SYSRST_START;
parameter TIME_FINISH   = 10000;
	
always @(*)
  begin
    if(!sysrstn)
        rstn = 1'b0;
    else
        rstn = #RST_START 1'b1;
  end
	
always @(*)
  begin
    if(!rstn)
        clk = 1'b0;
    else
        clk = #CLK_START ~clk;
  end

${root} u_${root} (
  .rstn (rst_n),
  .clk  (clk)
);
	
initial
  begin
    clk = 1'b0;
    sysrstn = 1'b0;
    #SYSRST_START sysrstn = 1'b1;
    #SYSRST_END sysrstn = 1'b0;
  end
	
initial
  begin
    \$dumpfile(\"mainsim.vcd\");
    \$dumpvars;
    #TIME_FINISH \$finish;
  end
endmodule
" > ${sim_dir}/mainsim.v